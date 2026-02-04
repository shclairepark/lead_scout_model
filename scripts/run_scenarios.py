#!/usr/bin/env python3
"""
Scenario Runner for Lead Scout Demo
Executes deterministic test scenarios defined in data/customer_inputs.json
"""

import json
import os
import subprocess
import sys
import time

def run_scenarios():
    # Load scenarios
    with open("data/customer_inputs.json", "r") as f:
        scenarios = json.load(f)
        
    print(f"🚀 Running {len(scenarios)} Deterministic Scenarios...")
    print("=" * 60)
    
    for i, scenario in enumerate(scenarios):
        print(f"\n▶️  Scenario {i+1}: {scenario['sender_profile']['name']} ({scenario['id']})")
        print(f"   Expected: {scenario['expected_result']}")
        print("-" * 40)
        
        # Create temp input file
        temp_input = f"temp_input_{i}.json"
        with open(temp_input, "w") as f:
            json.dump(scenario["sender_profile"], f)
            
        try:
            # Run demo script as subprocess
            # Using seed 12345 for consistency
            cmd = [
                sys.executable, 
                "scripts/interactive_demo.py", 
                "--auto-input", temp_input,
                "--seed", "12345" 
            ]
            
            # Capture output
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print("❌ Error running scenario:")
                print(result.stderr)
            else:
                # Parse output to find leads
                output = result.stdout
                if "High Quality Leads Found (0)" in output:
                    print("   Result: 0 Leads Found")
                else:
                    # simplistic parsing
                    import re
                    match = re.search(r"High Quality Leads Found \((\d+)\)", output)
                    count = match.group(1) if match else "?"
                    print(f"   Result: {count} Leads Found")
                    
                    # Print first lead if exists
                    if count != "0" and count != "?":
                        lines = output.split('\n')
                        for line in lines:
                            if " | " in line and "NAME" not in line:
                                print(f"   Top Lead: {line.strip()}")
                                break
                                
        finally:
            # Cleanup
            if os.path.exists(temp_input):
                 os.remove(temp_input)
                 
        time.sleep(0.5)

    print("\n✅ All scenarios completed.")

if __name__ == "__main__":
    run_scenarios()
