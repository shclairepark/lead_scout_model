#!/usr/bin/env python3
"""
Lead Scout Signal Collection Demo

Run from terminal:
    python run_signals.py              # Interactive demo
    python run_signals.py --simulate   # Simulate incoming signals
    python run_signals.py --help       # Show help
"""

import argparse
import time
import random
from datetime import datetime, timedelta

from src.signals import LinkedInSignalMonitor, ExternalSignalAggregator, SignalEvent


def print_banner():
    """Print welcome banner."""
    print("\n" + "=" * 60)
    print("🔍 LEAD SCOUT - Signal Collection (Block 0)")
    print("=" * 60)
    print("Monitors LinkedIn engagement, funding rounds, role changes...")
    print()


def print_signal(signal: SignalEvent, prefix: str = "📡"):
    """Pretty print a signal event."""
    print(f"\n{prefix} Signal Detected!")
    print(f"   Type:      {signal.type.value}")
    print(f"   User:      {signal.user_id}")
    print(f"   Strength:  {signal.strength:.2f}")
    print(f"   Source:    {signal.source.value}")
    print(f"   Timestamp: {signal.timestamp.strftime('%Y-%m-%d %H:%M')}")
    if signal.company_id:
        print(f"   Company:   {signal.company_id}")
    print(f"   Data:      {signal.data}")


def interactive_demo():
    """Run interactive demo of signal collection."""
    print_banner()
    
    monitor = LinkedInSignalMonitor()
    aggregator = ExternalSignalAggregator()
    
    print("📊 Demo 1: LinkedIn Engagement Signals")
    print("-" * 40)
    
    # Simulate LinkedIn engagement
    engagements = [
        {"event_type": "like", "user_id": "urn:li:person:alice123", "post_id": "post_001", "user_name": "Alice Chen"},
        {"event_type": "comment", "user_id": "urn:li:person:bob456", "post_id": "post_001", "user_name": "Bob Smith"},
        {"event_type": "share", "user_id": "urn:li:person:alice123", "post_id": "post_002", "user_name": "Alice Chen"},
    ]
    
    for engagement in engagements:
        signal = monitor.parse_engagement(engagement)
        print_signal(signal, "👍" if engagement["event_type"] == "like" else "💬" if engagement["event_type"] == "comment" else "🔄")
        time.sleep(0.5)
    
    print("\n\n📊 Demo 2: Profile Visit Tracking")
    print("-" * 40)
    
    visit = monitor.parse_profile_visit({
        "visitor_id": "urn:li:person:carol789",
        "visitor_url": "https://linkedin.com/in/carol-johnson",
        "visit_count": 3,
    })
    print_signal(visit, "👀")
    
    print("\n\n📊 Demo 3: Signal Aggregation")
    print("-" * 40)
    
    # Aggregate Alice's signals
    aggregation = monitor.aggregate_signals("urn:li:person:alice123")
    print(f"\n📈 Aggregation for Alice Chen:")
    print(f"   Total Signals:    {aggregation['total_count']}")
    print(f"   Frequency Score:  {aggregation['frequency_score']:.3f}")
    print(f"   Signal Types:     {aggregation['signal_types']}")
    print(f"   Latest Activity:  {aggregation['latest_timestamp'].strftime('%Y-%m-%d %H:%M')}")
    
    print("\n\n📊 Demo 4: External Signals (Funding)")
    print("-" * 40)
    
    funding = aggregator.parse_funding_event({
        "company_id": "company:acme-tech",
        "funding_amount": 25_000_000,
        "round_type": "series_b",
        "investor_names": ["Sequoia Capital", "Andreessen Horowitz"],
    })
    print_signal(funding, "💰")
    
    print("\n\n📊 Demo 5: External Signals (Role Change)")
    print("-" * 40)
    
    role_change = aggregator.parse_role_change({
        "user_id": "urn:li:person:dave101",
        "new_title": "VP of Engineering",
        "previous_title": "Director of Engineering",
        "company_id": "company:acme-tech",
    })
    print_signal(role_change, "🎯")
    
    print("\n\n📊 Demo 6: Event Attendance")
    print("-" * 40)
    
    event = aggregator.parse_event_signal({
        "attendee_id": "urn:li:person:eve202",
        "event_name": "SaaS Growth Summit 2026",
        "event_type": "conference",
        "company_id": "company:startup-xyz",
    })
    print_signal(event, "📅")

    print("\n\n📊 Demo 7: Lead Enrichment (Block 1.5)")
    print("-" * 40)
    
    from src.enrichment import LeadEnricher, ICPMatcher, Industry
    
    enricher = LeadEnricher()
    icp_matcher = ICPMatcher()
    
    # Enrich a lead
    print("✨ Enriching Lead: data-driven startup founder...")
    lead = enricher.enrich_lead(
        user_id="urn:li:person:alex_founder",
        linkedin_profile_url="https://linkedin.com/in/alex-founder",
        linkedin_company_url="https://linkedin.com/company/data-startup",
        contact_data={"name": "Alex Founder", "title": "Co-Founder & CTO", "email": "alex@datastartup.io"},
        company_data={"name": "Data Startup", "size": 65, "industry": "SaaS", "funding_stage": "series_a"},
        social_data={"mutual_connections": ["Sarah VC", "Mike Angel"], "shared_groups": ["SaaS Founders"]}
    )
    
    print(f"   Name:      {lead.contact.name}")
    print(f"   Role:      {lead.contact.title} ({lead.contact.seniority_level.value})")
    print(f"   Company:   {lead.company.name} ({lead.company.size} emp, {lead.company.industry.value})")
    print(f"   Social:    {lead.social_graph.mutual_connections} mutuals")
    
    print("\n\n📊 Demo 8: ICP Scoring")
    print("-" * 40)
    
    # Calculate score
    score_result = icp_matcher.calculate_icp_score(lead)
    
    print(f"   🎯 ICP Score: {score_result['icp_score']}/100")
    print(f"   Authority:   {score_result['authority_level'].upper()}")
    print("   Breakdown:")
    for dim, score in score_result['breakdown'].items():
        print(f"     - {dim.ljust(10)}: {score:.2f}")

    print("\n\n📊 Demo 9: Intent Scoring (Block 2.5)")
    print("-" * 40)
    
    from src.scoring import IntentScorer, IntentScore, ScoringConfig
    from src.signals import SignalEvent, SignalType, SignalSource
    from datetime import datetime
    
    scorer = IntentScorer()
    
    # 1. Hot Lead (Demo Request + Engagement)
    print("🔥 Scoring Hot Lead (Demo Request)...")
    hot_signals = [
        SignalEvent(
            type=SignalType.EVENT_ATTENDANCE,
            user_id="urn:li:person:hot_lead",
            timestamp=datetime.now(),
            source=SignalSource.LINKEDIN,
            data={"event_type": "demo_request"},
            strength=1.0
        )
    ]
    hot_score = scorer.calculate_intent_score(hot_signals)
    print(f"   Score: {hot_score.score} ({hot_score.label.value.upper()})")
    
    # 2. Buying Committee Detection
    print("\n👥 Checking Buying Committee...")
    company_signals = [
        SignalEvent(type=SignalType.PROFILE_VISIT, user_id="u1", timestamp=datetime.now(), source=SignalSource.LINKEDIN, company_id="c1"),
        SignalEvent(type=SignalType.CONTENT_ENGAGEMENT, user_id="u2", timestamp=datetime.now(), source=SignalSource.LINKEDIN, company_id="c1"),
    ]
    committee_factor = scorer.detect_buying_committee("u1", company_signals)
    print(f"   Multiplier: {committee_factor}x (2 active contacts)")

    print("\n\n📊 Demo 10: Engagement Pipeline (Block 3.5)")
    print("-" * 40)
    
    from src.engagement import HighIntentFilter, ConversationStarter
    from src.enrichment import EnrichedLead, EnrichedCompany, EnrichedContact, SeniorityLevel
    
    # Setup
    intent_filter = HighIntentFilter()
    starter = ConversationStarter()
    
    # Create a qualified lead
    qualified_lead = EnrichedLead(
        user_id="urn:li:person:qualified",
        company=EnrichedCompany(company_id="c1", name="Growth Startup", website="growth.io"),
        contact=EnrichedContact(user_id="u1", name="Sarah CTO", seniority_level=SeniorityLevel.C_LEVEL)
    )
    
    # 1. Decision Logic
    print("🚦 Evaluating Lead for Outreach...")
    decision = intent_filter.evaluate_lead(
        lead=qualified_lead,
        intent_score=hot_score,  # Reusing score from Demo 9 (75.0)
        icp_score_val=90.0
    )
    
    if decision.should_engage:
        print(f"   Decison:  GO ({decision.reason})")
        print(f"   Priority: {decision.priority.value.upper()}")
        
        # 2. Message Generation
        print("\n📝 Generating Outreach...")
        msg = starter.generate_message(qualified_lead, hot_signals)
        print(f"   Subject:  {msg.subject or '(No Subject)'}")
        print(f"   Body Preview:\n   {'-'*20}\n   {msg.body.replace(chr(10), chr(10)+'   ')}\n   {'-'*20}")
    else:
        print(f"   Decision: NO GO ({decision.reason})")

    print("\n\n✅ Demo Complete!")
    print("=" * 60)
    print("Full Pipeline Ready: Collection -> Enrichment -> Scoring -> Engagement")
    print("Use --simulate for continuous mode.")
    print()


def simulate_signals():
    """Simulate continuous signal stream."""
    print_banner()
    print("🔄 Simulating live signal stream (Ctrl+C to stop)...")
    print("-" * 60)
    
    monitor = LinkedInSignalMonitor()
    aggregator = ExternalSignalAggregator()
    
    # Sample data pools
    users = [
        ("urn:li:person:alice123", "Alice Chen"),
        ("urn:li:person:bob456", "Bob Smith"),
        ("urn:li:person:carol789", "Carol Johnson"),
        ("urn:li:person:dave101", "Dave Wilson"),
        ("urn:li:person:eve202", "Eve Martinez"),
    ]
    
    companies = ["company:acme-tech", "company:startup-xyz", "company:enterprise-co"]
    event_types = ["like", "comment", "share"]
    titles = ["VP of Sales", "CTO", "Director of Engineering", "Head of Product", "CEO"]
    
    signal_count = 0
    
    try:
        while True:
            signal_type = random.choice(["engagement", "visit", "funding", "role", "event"])
            user_id, user_name = random.choice(users)
            company = random.choice(companies)
            
            if signal_type == "engagement":
                signal = monitor.parse_engagement({
                    "event_type": random.choice(event_types),
                    "user_id": user_id,
                    "post_id": f"post_{random.randint(1, 100)}",
                    "user_name": user_name,
                })
                print_signal(signal, "👍")
                
            elif signal_type == "visit":
                signal = monitor.parse_profile_visit({
                    "visitor_id": user_id,
                    "visitor_url": f"https://linkedin.com/in/{user_name.lower().replace(' ', '-')}",
                    "visit_count": random.randint(1, 5),
                })
                print_signal(signal, "👀")
                
            elif signal_type == "funding":
                signal = aggregator.parse_funding_event({
                    "company_id": company,
                    "funding_amount": random.choice([1_000_000, 5_000_000, 20_000_000, 50_000_000]),
                    "round_type": random.choice(["seed", "series_a", "series_b"]),
                })
                print_signal(signal, "💰")
                
            elif signal_type == "role":
                signal = aggregator.parse_role_change({
                    "user_id": user_id,
                    "new_title": random.choice(titles),
                    "company_id": company,
                })
                print_signal(signal, "🎯")
                
            else:
                signal = aggregator.parse_event_signal({
                    "attendee_id": user_id,
                    "event_name": f"Tech Conference {random.randint(2025, 2027)}",
                    "event_type": random.choice(["conference", "webinar", "workshop"]),
                    "company_id": company,
                })
                print_signal(signal, "📅")
            
            signal_count += 1
            print(f"\n   [Total signals collected: {signal_count}]")
            
            # Random delay between signals
            time.sleep(random.uniform(1.0, 3.0))
            
    except KeyboardInterrupt:
        print(f"\n\n🛑 Stopped. Collected {signal_count} signals.")
        
        # Show aggregation summary
        print("\n📈 Signal Summary by User:")
        print("-" * 40)
        for user_id, user_name in users:
            agg = monitor.aggregate_signals(user_id)
            if agg["total_count"] > 0:
                print(f"   {user_name}: {agg['total_count']} signals, freq={agg['frequency_score']:.3f}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Lead Scout Signal Collection Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_signals.py              Run interactive demo
  python run_signals.py --simulate   Simulate live signal stream
        """
    )
    parser.add_argument(
        "--simulate", "-s",
        action="store_true",
        help="Simulate continuous signal stream"
    )
    
    args = parser.parse_args()
    
    if args.simulate:
        simulate_signals()
    else:
        interactive_demo()


if __name__ == "__main__":
    main()
