"""
Interactive & Automated Verification Script for the Health Misinformation Decision Engine.
Tests all 4 canonical verdict outputs:
1. Potentially refuted (including 9-vs-1 scientific consensus)
2. Potentially supported (including 9-vs-1 scientific consensus)
3. Mixed evidence (divided 50/50, 60/40 splits)
4. Insufficient evidence (neutral context only or no evidence)
"""

import sys
from decision_engine import determine_verdict


def run_scenario(name, support_count, contra_count, neutral_count=0, avg_conf=0.88):
    """Run a simulated evidence scenario through determine_verdict()."""
    evidence = []
    for _ in range(support_count):
        evidence.append({"relationship": "support", "confidence": avg_conf})
    for _ in range(contra_count):
        evidence.append({"relationship": "contradiction", "confidence": avg_conf})
    for _ in range(neutral_count):
        evidence.append({"relationship": "neutral", "confidence": avg_conf})

    verdict, explanation = determine_verdict(evidence)

    print(f"\n[{name}]")
    print(f"  Inputs      : Support = {support_count}, Contradiction = {contra_count}, Neutral = {neutral_count}")
    print(f"  Verdict     : >> {verdict} <<")
    print(f"  Explanation : {explanation}")
    return verdict


def test_all_scenarios():
    print("=" * 70)
    print("DECISION ENGINE SCENARIO VERIFICATION")
    print("=" * 70)

    # 1. 9-vs-1 Consensus Refutation
    v1 = run_scenario("Scenario 1: 9-vs-1 Scientific Consensus Refutation", support_count=1, contra_count=9)
    assert v1 == "Potentially refuted", f"Expected Potentially refuted, got {v1}"

    # 2. 9-vs-1 Consensus Support
    v2 = run_scenario("Scenario 2: 9-vs-1 Scientific Consensus Support", support_count=9, contra_count=1)
    assert v2 == "Potentially supported", f"Expected Potentially supported, got {v2}"

    # 3. 5-vs-5 Genuinely Divided Down the Middle
    v3 = run_scenario("Scenario 3: 5-vs-5 Genuinely Divided Split (Doctors Divided)", support_count=5, contra_count=5)
    assert v3 == "Mixed evidence", f"Expected Mixed evidence, got {v3}"

    # 4. 3-vs-2 Close Split
    v4 = run_scenario("Scenario 4: 3-vs-2 Close Split (No Consensus)", support_count=3, contra_count=2)
    assert v4 == "Mixed evidence", f"Expected Mixed evidence, got {v4}"

    # 5. 2-vs-3 Close Split
    v5 = run_scenario("Scenario 5: 2-vs-3 Close Split (No Consensus)", support_count=2, contra_count=3)
    assert v5 == "Mixed evidence", f"Expected Mixed evidence, got {v5}"

    # 6. Pure Unanimous Refutation
    v6 = run_scenario("Scenario 6: Pure Unanimous Refutation", support_count=0, contra_count=5)
    assert v6 == "Potentially refuted", f"Expected Potentially refuted, got {v6}"

    # 7. Pure Unanimous Support
    v7 = run_scenario("Scenario 7: Pure Unanimous Support", support_count=5, contra_count=0)
    assert v7 == "Potentially supported", f"Expected Potentially supported, got {v7}"

    # 8. Insufficient Evidence (Neutral context only)
    v8 = run_scenario("Scenario 8: Insufficient Evidence (Neutral background studies only)", support_count=0, contra_count=0, neutral_count=4)
    assert v8 == "Insufficient evidence", f"Expected Insufficient evidence, got {v8}"

    # 9. Insufficient Evidence (Empty)
    v9 = run_scenario("Scenario 9: Insufficient Evidence (Zero studies retrieved)", support_count=0, contra_count=0, neutral_count=0)
    assert v9 == "Insufficient evidence", f"Expected Insufficient evidence, got {v9}"

    print("\n" + "=" * 70)
    print("ALL 9 TEST SCENARIOS PASSED WITH 100% ACCURACY!")
    print("=" * 70)


def interactive_mode():
    print("\n" + "=" * 70)
    print("INTERACTIVE DECISION ENGINE TESTER")
    print("Enter custom evidence counts to see the Decision Engine's verdict.")
    print("Press Ctrl+C or type 'exit' to quit.")
    print("=" * 70)

    while True:
        try:
            s_in = input("\nEnter supporting evidence count (e.g. 1) : ").strip()
            if s_in.lower() in {"exit", "quit", "q"}:
                break
            c_in = input("Enter refuting evidence count   (e.g. 9) : ").strip()
            if c_in.lower() in {"exit", "quit", "q"}:
                break
            n_in = input("Enter neutral evidence count    (e.g. 0) : ").strip() or "0"

            s = int(s_in)
            c = int(c_in)
            n = int(n_in)

            run_scenario("Custom User Query", support_count=s, contra_count=c, neutral_count=n)
        except ValueError:
            print("Please enter valid integers.")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting interactive tester.")
            break


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        test_all_scenarios()
        print("\nTip: To test custom counts interactively, run:")
        print("python test_decision_engine.py --interactive")
