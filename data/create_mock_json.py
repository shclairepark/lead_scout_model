import json
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

# Mock data from generate_leads.py (copied to avoid import issues with relative paths)
PUBLIC_PROFILES = [
    ("Jason Lemkin", "Founder & CEO", "SaaStr", "saastr.com", "saas", 150),
    ("Lars Nilsson", "CEO", "SalesSource", "salessource.com", "saas", 75),
    ("Chris Oliver", "Founder", "GoRails", "gorails.com", "education", 10),
    ("Alok Goel", "Co-founder & CEO", "Drivetrain", "drivetrain.ai", "saas", 50),
    ("David Sacks", "General Partner", "Craft Ventures", "craftventures.com", "vc", 50),
    ("Paul Graham", "Co-Founder", "Y Combinator", "ycombinator.com", "vc", 200),
    ("Sam Altman", "CEO", "OpenAI", "openai.com", "ai_ml", 500),
    ("Satya Nadella", "CEO", "Microsoft", "microsoft.com", "enterprise", 200000),
    ("Sundar Pichai", "CEO", "Google", "google.com", "enterprise", 150000),
    ("Elon Musk", "CEO", "Tesla", "tesla.com", "automotive", 100000),
    ("Brian Chesky", "CEO", "Airbnb", "airbnb.com", "marketplace", 6000),
    ("Patrick Collison", "CEO", "Stripe", "stripe.com", "fintech", 8000),
    ("John Collison", "President", "Stripe", "stripe.com", "fintech", 8000),
    ("Tobias Lutke", "CEO", "Shopify", "shopify.com", "ecommerce", 10000),
    ("Marc Benioff", "CEO", "Salesforce", "salesforce.com", "saas", 70000),
    ("Stewart Butterfield", "CEO", "Slack", "slack.com", "saas", 3000),
    ("Eric Yuan", "CEO", "Zoom", "zoom.us", "saas", 5000),
    ("Dharmesh Shah", "CTO", "HubSpot", "hubspot.com", "martech", 6000),
    ("Brian Halligan", "Co-Founder", "HubSpot", "hubspot.com", "martech", 6000),
    ("Aaron Levie", "CEO", "Box", "box.com", "enterprise", 2500),
    ("Drew Houston", "CEO", "Dropbox", "dropbox.com", "saas", 3000),
    ("Melanie Perkins", "CEO", "Canva", "canva.com", "design", 4000),
    ("Daniel Ek", "CEO", "Spotify", "spotify.com", "media", 9000),
    ("Ried Hoffman", "Partner", "Greylock", "greylock.com", "vc", 100),
    ("Peter Thiel", "Partner", "Founders Fund", "foundersfund.com", "vc", 80),
    ("Naval Ravikant", "Founder", "AngelList", "angellist.com", "fintech", 200),
    ("Alexis Ohanian", "Founder", "Seven Seven Six", "sevensevensix.com", "vc", 50),
    ("Garry Tan", "CEO", "Y Combinator", "ycombinator.com", "vc", 200),
    ("Austen Allred", "CEO", "BloomTech", "bloomtech.com", "education", 300),
    ("Amjad Masad", "CEO", "Replit", "replit.com", "devtools", 100),
    ("Guillermo Rauch", "CEO", "Vercel", "vercel.com", "devtools", 500),
    ("Nat Friedman", "Investor", "GitHub (Former CEO)", "github.com", "devtools", 3000),
    ("Thomas Dohmke", "CEO", "GitHub", "github.com", "devtools", 3000),
    ("Sid Sijbrandij", "CEO", "GitLab", "gitlab.com", "devtools", 2000),
    ("Mitchell Hashimoto", "Founder", "HashiCorp", "hashicorp.com", "devtools", 2500),
    ("Armon Dadgar", "CTO", "HashiCorp", "hashicorp.com", "devtools", 2500),
    ("Jesse Beyroutey", "Partner", "Waldorf", "waldorf.com", "vc", 20),
    ("Mike Cannon-Brookes", "Co-CEO", "Atlassian", "atlassian.com", "saas", 10000),
    ("Scott Farquhar", "Co-CEO", "Atlassian", "atlassian.com", "saas", 10000),
    ("Jeff Lawson", "CEO", "Twilio", "twilio.com", "devtools", 8000),
    ("Jennifer Tejada", "CEO", "PagerDuty", "pagerduty.com", "devtools", 1000),
    ("Edith Harbaugh", "Co-Founder", "LaunchDarkly", "launchdarkly.com", "devtools", 500),
    ("Christine Spang", "CTO", "Nylas", "nylas.com", "devtools", 300),
    ("Mathilde Collin", "CEO", "Front", "front.com", "saas", 400),
    ("Laura Behrens Wu", "CEO", "Shippo", "goshippo.com", "ecommerce", 300),
    ("Pedro Franceschi", "Co-CEO", "Brex", "brex.com", "fintech", 1200),
    ("Henrique Dubugras", "Co-CEO", "Brex", "brex.com", "fintech", 1200),
    ("Zach Perret", "CEO", "Plaid", "plaid.com", "fintech", 1000),
    ("William Hockey", "Co-Founder", "Plaid", "plaid.com", "fintech", 1000),
    ("Max Levchin", "CEO", "Affirm", "affirm.com", "fintech", 2500),
    ("Vlad Tenev", "CEO", "Robinhood", "robinhood.com", "fintech", 4000),
    ("Baiju Bhatt", "Co-Founder", "Robinhood", "robinhood.com", "fintech", 4000),
    ("Nik Storonsky", "CEO", "Revolut", "revolut.com", "fintech", 6000),
    ("Sebastian Siemiatkowski", "CEO", "Klarna", "klarna.com", "fintech", 5000),
    ("Rene Lacerte", "CEO", "Bill.com", "bill.com", "fintech", 2000),
    ("Ryan Petersen", "CEO", "Flexport", "flexport.com", "logistics", 3000),
    ("Parker Conrad", "CEO", "Rippling", "rippling.com", "saas", 2000),
    ("Dylan Field", "CEO", "Figma", "figma.com", "design", 1500),
    ("Ivan Zhao", "CEO", "Notion", "notion.so", "saas", 1000),
    ("Shishir Mehrotra", "CEO", "Coda", "coda.io", "saas", 500),
    ("Rahul Vohra", "CEO", "Superhuman", "superhuman.com", "saas", 150),
    ("Des Traynor", "Co-Founder", "Intercom", "intercom.com", "martech", 1500),
    ("Eoghan McCabe", "Chairman", "Intercom", "intercom.com", "martech", 1500),
    ("Karen Peacock", "CEO", "Intercom", "intercom.com", "martech", 1500), 
    ("Sid Patil", "CEO", "GitLab", "gitlab.com", "devtools", 2000), 
    ("Job van der Voort", "CEO", "Remote", "remote.com", "hr_tech", 1000),
    ("Deel Founder", "CEO", "Deel", "deel.com", "hr_tech", 3000),
    ("Tony Xu", "CEO", "DoorDash", "doordash.com", "marketplace", 8000),
    ("Logan Green", "CEO", "Lyft", "lyft.com", "marketplace", 5000),
    ("Dara Khosrowshahi", "CEO", "Uber", "uber.com", "marketplace", 20000),
    ("Evan Spiegel", "CEO", "Snap", "snap.com", "media", 5000),
    ("Ben Silbermann", "CEO", "Pinterest", "pinterest.com", "media", 4000),
    ("Jack Dorsey", "CEO", "Block", "block.xyz", "fintech", 10000),
    ("Hayden Adams", "CEO", "Uniswap", "uniswap.org", "crypto", 100),
    ("Brian Armstrong", "CEO", "Coinbase", "coinbase.com", "crypto", 5000),
    ("Vitalik Buterin", "Co-Founder", "Ethereum", "ethereum.org", "crypto", 100),
    ("Changpeng Zhao", "Founder", "Binance", "binance.com", "crypto", 8000),
    ("Sam Bankman-Fried", "Founder", "FTX (Defunct)", "ftx.com", "crypto", 0),
    ("Do Kwon", "Founder", "Terra (Defunct)", "terra.money", "crypto", 0),
    ("Palmer Luckey", "Founder", "Anduril", "anduril.com", "defense", 2000),
    ("Alex Karp", "CEO", "Palantir", "palantir.com", "defense", 4000),
    ("Trae Stephens", "Partner", "Founders Fund", "foundersfund.com", "vc", 80),
    ("George Kurtz", "CEO", "CrowdStrike", "crowdstrike.com", "security", 8000),
    ("Nikesh Arora", "CEO", "Palo Alto Networks", "paloaltonetworks.com", "security", 12000),
    ("Jay Chaudhry", "CEO", "Zscaler", "zscaler.com", "security", 6000),
    ("Ken Xie", "CEO", "Fortinet", "fortinet.com", "security", 10000),
    ("Shantanu Narayen", "CEO", "Adobe", "adobe.com", "saas", 25000),
    ("Safra Catz", "CEO", "Oracle", "oracle.com", "enterprise", 140000),
    ("Arvind Krishna", "CEO", "IBM", "ibm.com", "enterprise", 280000),
    ("Lisa Su", "CEO", "AMD", "amd.com", "hardware", 25000),
    ("Jensen Huang", "CEO", "Nvidia", "nvidia.com", "hardware", 26000),
    ("Pat Gelsinger", "CEO", "Intel", "intel.com", "hardware", 120000),
    ("Tim Cook", "CEO", "Apple", "apple.com", "hardware", 160000),
    ("Mark Zuckerberg", "CEO", "Meta", "meta.com", "media", 70000),
    ("Adam Neumann", "Founder", "Flow", "flow.life", "proptech", 100),
    ("Travis Kalanick", "CEO", "CloudKitchens", "cloudkitchens.com", "proptech", 2000),
    ("Masayoshi Son", "CEO", "SoftBank", "softbank.jp", "vc", 5000),
    ("Bill Gates", "Co-Chair", "Gates Foundation", "gatesfoundation.org", "nonprofit", 1800),
    ("Ginni Rometty", "Former CEO", "IBM", "ibm.com", "enterprise", 280000),
    ("Meg Whitman", "Ambassador", "US Govt", "state.gov", "government", 100),
    ("Susan Wojcicki", "Former CEO", "YouTube", "youtube.com", "media", 2000),
    ("Sheryl Sandberg", "Founder", "LeanIn", "leanin.org", "nonprofit", 50),
    ("Marissa Mayer", "CEO", "Sunshine", "sunshine.com", "consumer", 20),
]

def create_json():
    profiles = []
    for p in PUBLIC_PROFILES:
        name, title, company, domain, industry, size = p
        
        profile = {
            "name": name,
            "title": title,
            "company_name": company,
            "company_domain": domain,
            "industry": industry,
            "company_size": size,
            "linkedin_url": f"https://linkedin.com/in/{name.lower().replace(' ', '-')}"
        }
        profiles.append(profile)
        
    output_path = "data/public_profiles.json"
    with open(output_path, "w") as f:
        json.dump(profiles, f, indent=2)
        
    print(f"Created {output_path} with {len(profiles)} profiles.")

if __name__ == "__main__":
    create_json()
