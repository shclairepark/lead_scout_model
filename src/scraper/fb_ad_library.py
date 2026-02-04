"""
Facebook Ad Library Scraper (Production).

Scrapes the Meta Ad Library API to find businesses advertising
products/services targeting the 50+ demographic.

Requires: META_ACCESS_TOKEN in .env file

Usage:
    python -m src.scraper.fb_ad_library --niche health --output data/fb_leads_raw.csv
"""

import os
import csv
import time
import argparse
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime
from urllib.parse import urlparse
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()


@dataclass
class AdLibraryLead:
    """Represents a lead extracted from Facebook Ad Library."""
    advertiser_name: str
    page_id: str
    page_url: str
    domain: Optional[str]
    ad_creative_text: str
    niche: str
    scraped_at: str
    
    # Enrichment fields (filled later)
    contact_email: Optional[str] = None
    contact_name: Optional[str] = None


class FacebookAdLibraryScraper:
    """
    Scrapes Facebook Ad Library for advertisers in senior-focused niches.
    
    Requires META_ACCESS_TOKEN environment variable.
    Get your token from: https://developers.facebook.com/tools/explorer/
    """
    
    # Senior-focused search terms by niche
    NICHE_KEYWORDS = {
        "health": [
            "arthritis relief", "joint pain", "hearing aids", 
            "mobility scooter", "compression socks", "back pain relief"
        ],
        "home_services": [
            "walk-in tub", "stairlift", "medical alert system",
            "grab bars", "home security seniors", "aging in place"
        ],
        "insurance": [
            "medicare supplement", "life insurance seniors",
            "final expense insurance", "burial insurance"
        ],
        "travel": [
            "senior cruise deals", "RV travel", "retirement travel",
            "senior tours", "accessible travel"
        ],
        "supplements": [
            "glucosamine", "memory supplement", "vision supplement",
            "prostate health", "bone health supplement"
        ]
    }
    
    # Meta Ad Library API endpoint
    API_BASE_URL = "https://graph.facebook.com/v18.0/ads_archive"
    
    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize the scraper.
        
        Args:
            access_token: Meta API access token (defaults to META_ACCESS_TOKEN env var)
        """
        self.access_token = access_token or os.getenv("META_ACCESS_TOKEN")
        if not self.access_token:
            raise ValueError(
                "META_ACCESS_TOKEN not found. Set it in .env file or pass as argument.\n"
                "Get your token from: https://developers.facebook.com/tools/explorer/"
            )
        self.leads: List[AdLibraryLead] = []
        
    def scrape_niche(self, niche: str, limit: int = 100) -> List[AdLibraryLead]:
        """
        Scrape leads for a specific niche.
        
        Args:
            niche: One of health, home_services, insurance, travel, supplements
            limit: Maximum number of leads to collect
            
        Returns:
            List of AdLibraryLead objects
        """
        if niche not in self.NICHE_KEYWORDS:
            raise ValueError(f"Unknown niche: {niche}. Valid: {list(self.NICHE_KEYWORDS.keys())}")
        
        keywords = self.NICHE_KEYWORDS[niche]
        leads = []
        
        for keyword in keywords:
            if len(leads) >= limit:
                break
                
            print(f"   Searching: '{keyword}'...")
            keyword_leads = self._search_keyword(keyword, niche, limit - len(leads))
            leads.extend(keyword_leads)
            
            # Rate limiting (Meta API has limits)
            time.sleep(2)
        
        self.leads.extend(leads)
        return leads
    
    def _search_keyword(self, keyword: str, niche: str, limit: int) -> List[AdLibraryLead]:
        """Search for ads matching a keyword using Meta Ad Library API."""
        params = {
            "access_token": self.access_token,
            "search_terms": keyword,
            "ad_type": "ALL",
            "ad_reached_countries": "US",
            "fields": "page_id,page_name,ad_creative_bodies,ad_snapshot_url",
            "limit": min(limit, 50)  # API max per request
        }
        
        try:
            response = requests.get(self.API_BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "error" in data:
                print(f"   ⚠️ API Error: {data['error'].get('message', 'Unknown error')}")
                return []
            
            leads = []
            seen_page_ids = set()  # Deduplicate by page
            
            for ad in data.get("data", []):
                page_id = ad.get("page_id", "")
                
                # Skip duplicates
                if page_id in seen_page_ids:
                    continue
                seen_page_ids.add(page_id)
                
                creative_text = ""
                if ad.get("ad_creative_bodies"):
                    creative_text = ad["ad_creative_bodies"][0] if ad["ad_creative_bodies"] else ""
                
                lead = AdLibraryLead(
                    advertiser_name=ad.get("page_name", "Unknown"),
                    page_id=page_id,
                    page_url=f"https://facebook.com/{page_id}",
                    domain=None,  # Will be enriched later
                    ad_creative_text=creative_text[:500],
                    niche=niche,
                    scraped_at=datetime.now().isoformat()
                )
                leads.append(lead)
            
            print(f"   Found {len(leads)} unique advertisers")
            return leads
            
        except requests.RequestException as e:
            print(f"   ❌ Request error for '{keyword}': {e}")
            return []
    
    def import_from_csv(self, csv_path: str, niche: str) -> List[AdLibraryLead]:
        """
        Import leads from a manually exported Ad Library CSV.
        
        The Meta Ad Library website allows CSV export of search results.
        This method parses that export format.
        """
        leads = []
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                lead = AdLibraryLead(
                    advertiser_name=row.get("Page name", "Unknown"),
                    page_id=row.get("Page ID", ""),
                    page_url=f"https://facebook.com/{row.get('Page ID', '')}",
                    domain=self._extract_domain(row.get("Website", "")),
                    ad_creative_text=row.get("Ad creative body", "")[:500],
                    niche=niche,
                    scraped_at=datetime.now().isoformat()
                )
                leads.append(lead)
        
        self.leads.extend(leads)
        return leads
    
    def _extract_domain(self, url: str) -> Optional[str]:
        """Extract domain from a URL."""
        if not url:
            return None
        try:
            parsed = urlparse(url if url.startswith("http") else f"https://{url}")
            return parsed.netloc.replace("www.", "")
        except Exception:
            return None
    
    def save_to_csv(self, output_path: str) -> None:
        """Save collected leads to CSV."""
        if not self.leads:
            print("No leads to save.")
            return
        
        fieldnames = [
            "advertiser_name", "page_id", "page_url", "domain",
            "ad_creative_text", "niche", "scraped_at",
            "contact_email", "contact_name"
        ]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for lead in self.leads:
                writer.writerow(asdict(lead))
        
        print(f"✅ Saved {len(self.leads)} leads to {output_path}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about collected leads."""
        niche_counts = {}
        for lead in self.leads:
            niche_counts[lead.niche] = niche_counts.get(lead.niche, 0) + 1
        
        return {
            "total_leads": len(self.leads),
            "by_niche": niche_counts,
            "with_domain": sum(1 for l in self.leads if l.domain),
            "with_email": sum(1 for l in self.leads if l.contact_email)
        }


def main():
    """CLI entry point for Facebook Ad Library scraper."""
    parser = argparse.ArgumentParser(
        description="Scrape Facebook Ad Library for senior-market advertisers"
    )
    parser.add_argument(
        "--niche", "-n",
        choices=["health", "home_services", "insurance", "travel", "supplements", "all"],
        default="all",
        help="Niche to scrape (default: all)"
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=100,
        help="Maximum leads per niche (default: 100)"
    )
    parser.add_argument(
        "--output", "-o",
        default="data/fb_leads_raw.csv",
        help="Output CSV path (default: data/fb_leads_raw.csv)"
    )
    
    args = parser.parse_args()
    
    try:
        scraper = FacebookAdLibraryScraper()
    except ValueError as e:
        print(f"❌ {e}")
        return
    
    niches = list(FacebookAdLibraryScraper.NICHE_KEYWORDS.keys()) if args.niche == "all" else [args.niche]
    
    print(f"\n🔍 Scraping Facebook Ad Library for: {', '.join(niches)}")
    print("=" * 60)
    
    for niche in niches:
        print(f"\n📂 Niche: {niche.upper()}")
        leads = scraper.scrape_niche(niche, limit=args.limit)
        print(f"   Total: {len(leads)} leads")
    
    scraper.save_to_csv(args.output)
    
    stats = scraper.get_stats()
    print(f"\n📊 Summary:")
    print(f"   Total leads: {stats['total_leads']}")
    for niche, count in stats['by_niche'].items():
        print(f"   - {niche}: {count}")


if __name__ == "__main__":
    main()
