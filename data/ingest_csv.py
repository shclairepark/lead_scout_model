"""
CSV Data Ingestion Script (Refactored).

Uses the consolidated PipelineEngine for processing.
"""

import csv
import json
import argparse
from datetime import datetime
from collections import defaultdict
from typing import Dict, Any

from src.signals import SignalEvent, SignalType, SignalSource
from src.context import SenderProfile
from src.pipeline import PipelineEngine, SystemConfig

def parse_csv(file_path: str) -> Dict[str, Dict[str, Any]]:
    """Parse CSV file into grouped lead data."""
    leads_data = defaultdict(lambda: {"profile": {}, "signals": []})
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            user_id = row['user_id']
            # Profile
            leads_data[user_id]["profile"] = {
                "name": row['full_name'],
                "title": row['title'],
                "company_name": row['company_name'],
                "linkedin_url": row['linkedin_url'],
                "company_domain": row.get('company_domain', ''),
                "industry": row.get('industry', 'saas'),
                "company_size": row.get('company_size', 100),
            }
            # Signal
            if row.get('signal_type'):
                try:
                    ts = datetime.fromisoformat(row.get('timestamp')) if row.get('timestamp') else datetime.now()
                    sig_data = json.loads(row.get('signal_data', '{}').replace('""', '"'))
                    
                    try:
                        stype_str = row['signal_type'].upper()
                        if stype_str == "DEMO_REQUEST": stype = SignalType.DEMO_REQUEST
                        elif stype_str == "PRICING_PAGE_VISIT": stype = SignalType.PRICING_PAGE_VISIT
                        else: stype = SignalType[stype_str]
                    except KeyError:
                        stype = SignalType.CONTENT_ENGAGEMENT
                        
                    signal = SignalEvent(
                        type=stype,
                        user_id=user_id,
                        timestamp=ts,
                        source=SignalSource.LINKEDIN,
                        data=sig_data,
                        # Heuristic strength mapping
                        strength=1.0 if stype in [SignalType.DEMO_REQUEST, SignalType.FUNDING_ROUND] else 0.8
                    )
                    leads_data[user_id]["signals"].append(signal)
                except Exception as e:
                    print(f"⚠️ Error parsing signal for {user_id}: {e}")
    return leads_data


def main():
    parser = argparse.ArgumentParser(description="Ingest CSV data using PipelineEngine")
    parser.add_argument("csv_file", help="Path to CSV file with lead data")
    args = parser.parse_args()
    
    # 1. Setup Context
    sender_context = SenderProfile(
        name="DefenseAI",
        description="Enterprise Security Automation",
        value_props=["SOC2", "Compliance", "Zero Trust"],
        target_industries=["fintech", "security", "enterprise"],
        target_roles=["CISO", "VP Security"]
    )
    
    # 2. Initialize Engine
    engine = PipelineEngine(sender_context, config=SystemConfig())
    
    # 3. Process
    try:
        data = parse_csv(args.csv_file)
        print(f"\n🚀 Processing {len(data)} leads via PipelineEngine...")
        print("="*60)
        
        for user_id, lead_info in data.items():
            result = engine.process_lead(
                user_id=user_id,
                profile_data=lead_info["profile"],
                signals=lead_info["signals"]
            )
            
            # Print Formatted Result
            profile = result['lead'].contact
            company = result['lead'].company
            print(f"👤 LEAD: {profile.name} ({profile.title} @ {company.name})")
            print(f"   Industry: {company.industry.value if company.industry else 'Unknown'}")
            print(f"   🏢 Generic ICP Score: {result['icp']['score']}/100")
            print(f"   🧠 Semantic Fit:      {result['semantic']['score']:.1f}/100")
            print(f"   🔥 Intent Score:      {result['intent']['score']}/100 ({result['intent']['label']})")
            
            if result['decision']['should_engage']:
                print(f"   ✅ DECISION: ENGAGE")
                if result['draft']:
                    print(f"   📝 Draft: {result['draft'].body[:50]}...")
            else:
                 print(f"   ❌ DECISION: SKIP")
            print("-" * 60)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
