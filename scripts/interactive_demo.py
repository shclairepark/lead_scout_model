#!/usr/bin/env python3
"""
Lead Scout Interactive Demo
Simulates the end-to-end workflow: Input -> Signal Simulation -> Pipeline Processing -> Results
"""

import sys
import os
import json
import random
import time
import argparse
from datetime import datetime
from typing import List, Dict, Any

# Add project root to path
sys.path.append(os.getcwd())

from src.context import SenderProfile
from src.pipeline.engine import PipelineEngine
from src.signals import SignalEvent, SignalType, SignalSource

def clear_screen():
    print("\033[H\033[J", end="")

def print_banner():
    clear_screen()
    print("=" * 60)
    print("🚀 LEAD SCOUT - Interactive Agency Demo")
    print("=" * 60)
    print("Auto-pilot outbound based on intent signals + context.")
    print()

def get_sender_input() -> Dict[str, Any]:
    """Wizard to get user context."""
    parser = argparse.ArgumentParser(description="Lead Scout Interactive Demo")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for deterministic runs")
    parser.add_argument("--auto-input", type=str, help="Path to JSON file with sender profile input")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)
        print(f"🎲 Random Seed Set: {args.seed}")

    # Defaults for quick testing
    if args.auto_input:
        with open(args.auto_input, 'r') as f:
            data = json.load(f)
            # Handle list of scenarios (return all)
            if isinstance(data, list):
                if not data:
                    print("❌ Error: Input JSON list is empty.")
                    sys.exit(1)
                print(f"⚠️ Input is a list. Will run {len(data)} scenarios sequentially.")
                
                scenarios = []
                for item in data:
                   profile_data = item.get("sender_profile", item)
                   name = profile_data.get("name", "Acme AI")
                   desc = profile_data.get("description", "We scale revenue")
                   industry = profile_data.get("target_industries", ["saas"])[0]
                   role = profile_data.get("target_roles", ["VP Sales"])[0]
                   
                   scenarios.append({
                       "profile": SenderProfile(
                            name=name,
                            description=desc,
                            value_props=[desc],
                            target_industries=[industry.lower()],
                            target_roles=[role]
                        ),
                        "hints": item.get("simulation_hints", {})
                   })
                return scenarios
            
            # Single scenario
            profile_data = data.get("sender_profile", data)
            
            name = profile_data.get("name", "Acme AI")
            desc = profile_data.get("description", "We scale revenue")
            industry = profile_data.get("target_industries", ["saas"])[0]
            role = profile_data.get("target_roles", ["VP Sales"])[0]
            
            print(f"🤖 Auto-Input Loaded: {name} ({industry})")
            
            return [{
                "profile": SenderProfile(
                    name=name,
                    description=desc,
                    value_props=[desc],
                    target_industries=[industry.lower()],
                    target_roles=[role]
                ),
                "hints": profile_data.get("simulation_hints", {})
            }]
    else:
        print("📝 Step 1: Configure Your Agent")
        print("-" * 30)
        name = input("   Your Company Name [Acme AI]: ").strip() or "Acme AI"
        desc = input("   Value Proposition [We help SaaS scale revenue]: ").strip() or "We help SaaS companies scale revenue through automated attribution."
        industry = input("   Target Industry [SaaS]: ").strip() or "saas"
        role = input("   Target Role [VP Sales]: ").strip() or "VP Sales"
    
    return [{
        "profile": SenderProfile(
            name=name,
            description=desc,
            value_props=[desc],
            target_industries=[industry.lower()],
            target_roles=[role]
        ),
        "hints": {}
    }]


def load_profiles() -> List[Dict[str, Any]]:
    """Load mock profiles."""
    path = "data/public_profiles.json"
    if not os.path.exists(path):
        print(f"❌ Error: {path} not found. Run 'python data/create_mock_json.py' first.")
        sys.exit(1)
        
    with open(path, 'r') as f:
        return json.load(f)

def simulate_signals(profile: Dict[str, Any], hints: Dict[str, Any] = None) -> List[SignalEvent]:
    """Generate random or hinted signals for a profile."""
    signals = []
    hints = hints or {}
    
    forced_type = hints.get("force_signal_type")
    
    # CASE A: Explicit Hint Override
    if forced_type:
        # Check if profile matches target if specified
        target_company = hints.get("target_company")
        profile_company = profile.get("company", profile.get("current_company", ""))
        if target_company and target_company.lower() not in profile_company.lower():
            return [] # Skip unrelated profiles in strict mode
            
        # Generate the forced signal
        if forced_type == "funding_round":
             signals.append(SignalEvent(
                type=SignalType.FUNDING_ROUND,
                user_id=profile["linkedin_url"],
                timestamp=datetime.now(),
                source=SignalSource.CRUNCHBASE,
                data={"round_type": "Series C", "amount": 40000000},
                strength=0.95
            ))
        elif forced_type == "content_engagement":
             signals.append(SignalEvent(
                type=SignalType.CONTENT_ENGAGEMENT,
                user_id=profile["linkedin_url"],
                timestamp=datetime.now(),
                source=SignalSource.LINKEDIN,
                data={"event_type": "comment", "post_topic": hints.get("topic", "Industry Trends")},
                strength=0.6
            ))
        return signals

    # CASE B: Default Random Simulation
    # Chance of having signals
    if random.random() < 0.05: # 5% inactive (95% active for demo)
        return []
        
    # High intent chance (2% for top tier)
    is_hot = random.random() < 0.02
    
    # Generate MULTIPLE signals per lead for realistic counts
    
    # 1. Funding Round (15% chance, 1 signal if triggered)
    if random.random() < 0.15:
        signals.append(SignalEvent(
            type=SignalType.FUNDING_ROUND,
            user_id=profile["linkedin_url"],
            timestamp=datetime.now(),
            source=SignalSource.CRUNCHBASE,
            data={"round_type": random.choice(["Series A", "Series B", "Series C"]), 
                  "amount": random.choice([5000000, 15000000, 40000000, 100000000])},
            strength=0.9
        ))
        
    # 2. Demo Request (2% - highest intent)
    if is_hot:
        signals.append(SignalEvent(
            type=SignalType.DEMO_REQUEST,
            user_id=profile["linkedin_url"],
            timestamp=datetime.now(),
            source=SignalSource.COMPANY_WEBSITE,
            data={"context": "Pricing Page"},
            strength=1.0
        ))
    
    # 3. Competitor Engagement (25% chance, 1-3 signals)
    if random.random() < 0.25:
        competitors = ["Salesforce", "HubSpot", "Outreach", "SalesLoft", "Gong", "Clari"]
        count = random.randint(1, 3)
        for _ in range(count):
            signals.append(SignalEvent(
                type=SignalType.COMPETITOR_ENGAGEMENT,
                user_id=profile["linkedin_url"],
                timestamp=datetime.now(),
                source=SignalSource.LINKEDIN,
                data={"competitor": random.choice(competitors), "action": random.choice(["like", "comment", "share"])},
                strength=0.7
            ))
        
    # 4. Content Engagement (50% chance, 1-5 signals)
    if random.random() < 0.50:
        topics = ["AI Sales", "Revenue Ops", "GTM Strategy", "Pipeline Generation", "Sales Automation"]
        count = random.randint(1, 5)
        for _ in range(count):
            signals.append(SignalEvent(
                type=SignalType.CONTENT_ENGAGEMENT,
                user_id=profile["linkedin_url"],
                timestamp=datetime.now(),
                source=SignalSource.LINKEDIN,
                data={"event_type": random.choice(["like", "comment", "share"]), "post_topic": random.choice(topics)},
                strength=0.3
            ))
        
    # 5. Profile Visit (35% chance, 1-3 visits)
    if random.random() < 0.35:
        count = random.randint(1, 3)
        for _ in range(count):
            signals.append(SignalEvent(
                type=SignalType.PROFILE_VISIT,
                user_id=profile["linkedin_url"],
                timestamp=datetime.now(),
                source=SignalSource.LINKEDIN,
                data={"viewer_company": random.choice(["Unknown", "Competitor", "Partner", "Prospect"])},
                strength=0.2
            ))
    
    # 6. Event Attendance (12% chance, 1-2 events)
    if random.random() < 0.12:
        events = ["SaaStr Annual", "Dreamforce", "G2 Rev Conf", "Pavilion Summit", "AAiSP Leadership"]
        count = random.randint(1, 2)
        for _ in range(count):
            signals.append(SignalEvent(
                type=SignalType.EVENT_ATTENDANCE,
                user_id=profile["linkedin_url"],
                timestamp=datetime.now(),
                source=SignalSource.LINKEDIN,
                data={"event_name": random.choice(events)},
                strength=0.4
            ))
        
    return signals

def run_scenario(sender_profile, sys_hints):
    """Run a single end-to-end demo scenario."""
    print("\n✅ Agent Configured.")
    print("-" * 30)
    print(f"   Sender: {sender_profile.name}")
    print(f"   Target Industry: {', '.join(sender_profile.target_industries)}")
    print(f"   Target Role: {', '.join(sender_profile.target_roles)}")
    print("-" * 30)

    engine = PipelineEngine(sender_profile=sender_profile)
    
    print("   Loading Lead Database...")
    profiles = load_profiles()
    print(f"   Loaded {len(profiles)} profiles.")
    
    print("\n🔄 Step 2: Scanning & Processing Signals...")
    print("-" * 30)
    
    results = []
    
    # Progress visualization
    total = len(profiles)
    for i, profile in enumerate(profiles):
        # Simulate Signals with Hints
        signals = simulate_signals(profile, hints=sys_hints)
        
        # Add profile ID explicitly if missing for robust matching
        uid = profile["linkedin_url"]
        
        # Run Pipeline
        result = engine.process_lead(uid, profile, signals)
        
        # Check Decision
        if result["decision"]["should_engage"]:
            # Attach raw signals to result for visualization
            result["_signals"] = signals
            results.append(result)
            
        # Simple progress bar
        if i % 10 == 0 or i == total - 1:
            sys.stdout.write(f"\r   Scanning: [{'=' * int(20 * (i+1)/total):<20}] {i+1}/{total}")
            sys.stdout.flush()
            
    print("\n   Done.")
    
    # Sort by score
    results.sort(key=lambda x: x["intent"]["score"], reverse=True)
    
    print(f"\n✨ Step 3: High Quality Leads Found ({len(results)})")
    print("-" * 60)
    
    if not results:
        print("   No leads met the engagement criteria. Try broadening target industry.")
        return

    print(f"\n   Found {len(results)} matches based on Intent + Context fit:")
    
    for i, res in enumerate(results):
        lead = res["lead"]
        score = res["intent"]["score"]   # Rule-based score
        label = res["intent"]["label"].upper()
        
        # Neural Score
        neural_prob = res["intent"].get("neural_prob", 0.0)
        ai_score = f"{neural_prob*100:.0f}%"
        
        raw_signals = res.get("_signals", [])
        
        print("\n" + "=" * 100)
        print(f"🎯 MATCH #{i+1}: {lead.contact.name} ({lead.company.name})")
        print(f"   Rule Score: {score:.0f}% | 🧠 AI Model Confidence: {ai_score} ({label})")
        print("-" * 100)
        
        # Calculate counts
        counts = {t.name: 0 for t in SignalType}
        for s in raw_signals:
            if hasattr(s, 'type'):
                counts[s.type.name] = counts.get(s.type.name, 0) + 1
                
        # Print Grid of Counts
        col_width = 15
        row_1 = [tup for tup in list(counts.items())[:5]]
        row_2 = [tup for tup in list(counts.items())[5:10]]
        
        # Header Row 1
        print("SIGNAL COUNTS:")
        print("  " + "".join([f"{k[:14]:<16}" for k, v in row_1]))
        print("  " + "".join([f"{str(v):<16}" for k, v in row_1]))
        print("  " + "".join([f"{k[:14]:<16}" for k, v in row_2]))
        print("  " + "".join([f"{str(v):<16}" for k, v in row_2]))

            
        # Top Signal Details (retaining the useful context view)
        if raw_signals:
             top_sig = max(raw_signals, key=lambda s: s.strength)
             print(f"   💡 Key Driver: {top_sig.type.name} (Strength {top_sig.strength})")
             # Print specific data if relevant
             if top_sig.data:
                 print(f"      Context: {top_sig.data}")


def run_demo():
    print_banner()
    
    # 1. Setup Context (returns list of scenarios)
    scenarios = get_sender_input()
    
    for i, scenario in enumerate(scenarios):
        if len(scenarios) > 1:
            print(f"\n\n🚀 RUNNING SCENARIO {i+1}/{len(scenarios)}")
            print("=" * 40)
            
        run_scenario(scenario["profile"], scenario["hints"])
        
        if i < len(scenarios) - 1:
            time.sleep(2) # Pause for readability between runs

if __name__ == "__main__":
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\n\n🛑 Demo interrupted.")
