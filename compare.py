# compare.py
# Automatically extracts and compares 
# Section A and B from all run files

import os
import re

def extract_verdict(text):
    """Extract Section A verdict"""
    text_lower = text.lower()
    
    if 'a. overall' in text_lower or 'overall realism' in text_lower:
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if 'overall' in line.lower():
                # Check next few lines for verdict
                context = ' '.join(lines[i:i+3]).lower()
                if 'yes' in context and 'no' not in context:
                    return 'YES'
                elif 'no' in context and 'yes' not in context:
                    return 'NO'
                elif 'partly' in context or 'partial' in context:
                    return 'PARTLY'
    return 'UNCLEAR'

def extract_top_gap(text):
    """Extract first gap from Section B"""
    lines = text.split('\n')
    in_b = False
    
    for i, line in enumerate(lines):
        if 'b.' in line.lower() and 'gap' in line.lower():
            in_b = True
            continue
        if in_b and line.strip().startswith('1.'):
            # Clean the gap text
            gap = line.strip()
            gap = re.sub(r'^\d+\.\s*\*+', '', gap)
            gap = re.sub(r'\*+', '', gap)
            return gap.strip()[:80]
    
    return 'Not found'

def analyze_system(folder, prefix, num_runs=10):
    """Analyze all runs for a system"""
    results = []
    
    for i in range(1, num_runs + 1):
        filename = os.path.join(folder, f"{prefix}_run{i:02d}.txt")
        
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                text = f.read()
            
            verdict = extract_verdict(text)
            gap = extract_top_gap(text)
            results.append({
                'run': i,
                'verdict': verdict,
                'top_gap': gap
            })
        else:
            results.append({
                'run': i,
                'verdict': 'FILE NOT FOUND',
                'top_gap': 'FILE NOT FOUND'
            })
    
    return results

def count_consistency(results):
    """Count how consistent verdicts are"""
    verdicts = [r['verdict'] for r in results]
    most_common = max(set(verdicts), key=verdicts.count)
    count = verdicts.count(most_common)
    percentage = (count / len(verdicts)) * 100
    return most_common, count, percentage

if __name__ == "__main__":
    print("=" * 60)
    print("SYSTEM A vs SYSTEM B — FULL COMPARISON")
    print("=" * 60)
    
    # Analyze System A
    print("\n--- SYSTEM A (No Grounding) ---\n")
    a_results = analyze_system("System_A", "system_a")
    
    for r in a_results:
        print(f"Run {r['run']:02d} | {r['verdict']:8} | {r['top_gap']}")
    
    a_verdict, a_count, a_pct = count_consistency(a_results)
    print(f"\nMost common verdict: {a_verdict}")
    print(f"Consistency: {a_count}/10 runs = {a_pct:.0f}%")
    
    # Analyze System B
    print("\n--- SYSTEM B (KG-Grounded) ---\n")
    b_results = analyze_system("System_B", "system_b")
    
    for r in b_results:
        print(f"Run {r['run']:02d} | {r['verdict']:8} | {r['top_gap']}")
    
    b_verdict, b_count, b_pct = count_consistency(b_results)
    print(f"\nMost common verdict: {b_verdict}")
    print(f"Consistency: {b_count}/10 runs = {b_pct:.0f}%")
    
    # Final comparison
    print("\n" + "=" * 60)
    print("RESEARCH FINDING")
    print("=" * 60)
    print(f"System A consistency: {a_pct:.0f}% ({a_count}/10 runs said {a_verdict})")
    print(f"System B consistency: {b_pct:.0f}% ({b_count}/10 runs said {b_verdict})")
    
    if b_pct > a_pct:
        print("\nFINDING: System B MORE consistent than System A")
        print("Knowledge grounding IMPROVES verdict consistency")
    elif a_pct > b_pct:
        print("\nFINDING: System A MORE consistent than System B")
        print("Knowledge grounding did NOT improve consistency")
    else:
        print("\nFINDING: Both systems equally consistent")
    
    # Save results
    with open("comparison_results.txt", "w") as f:
        f.write("SYSTEM A vs SYSTEM B COMPARISON\n")
        f.write("=" * 60 + "\n\n")
        f.write("SYSTEM A (No Grounding):\n")
        for r in a_results:
            f.write(f"Run {r['run']:02d} | {r['verdict']:8} | {r['top_gap']}\n")
        f.write(f"\nConsistency: {a_pct:.0f}%\n\n")
        f.write("SYSTEM B (KG-Grounded):\n")
        for r in b_results:
            f.write(f"Run {r['run']:02d} | {r['verdict']:8} | {r['top_gap']}\n")
        f.write(f"\nConsistency: {b_pct:.0f}%\n\n")
        f.write(f"FINDING: System {'B' if b_pct > a_pct else 'A'} more consistent\n")
    
    print("\nResults saved to comparison_results.txt")
    