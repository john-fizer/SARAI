"""
Review & Accountability Demonstration
======================================

Shows how review compares predictions vs outcomes and updates trust scores.

Author: John Fizer
"""

import sys
sys.path.append('..')

from datetime import datetime
from sarai.core.review.accountability import ReviewSystem
from sarai.core.commitment.records import Commit
from sarai.safety.logging import ComprehensiveLogger


def demonstrate_review():
    """Demonstrate review and accountability."""

    print("=" * 80)
    print("REVIEW & ACCOUNTABILITY DEMONSTRATION")
    print("=" * 80)
    print()

    # Initialize
    logger = ComprehensiveLogger("./demo_logs")
    review_system = ReviewSystem(logger)

    print("✅ Review system initialized")
    print(f"   12 archetype trust scores initialized at 0.50")
    print()

    # Create sample commits with different outcomes
    scenarios = [
        {
            "name": "Accurate Prediction",
            "predicted": 100.0,
            "actual": 102.0,
            "archetypes": ["Analysis", "Structure"],
            "confidence": 0.8
        },
        {
            "name": "Minor Error",
            "predicted": 50.0,
            "actual": 62.0,
            "archetypes": ["Expression", "Innovation"],
            "confidence": 0.7
        },
        {
            "name": "Major Error",
            "predicted": 80.0,
            "actual": 20.0,
            "archetypes": ["Transformation", "Initiative"],
            "confidence": 0.9  # High confidence but wrong!
        },
        {
            "name": "Another Accurate",
            "predicted": 45.0,
            "actual": 46.0,
            "archetypes": ["Analysis", "Memory"],
            "confidence": 0.85
        },
        {
            "name": "Perfect Match",
            "predicted": "success",
            "actual": "success",
            "archetypes": ["Unity", "Relationship"],
            "confidence": 0.75
        }
    ]

    print("🔄 RUNNING REVIEW SCENARIOS")
    print("=" * 80)
    print()

    for i, scenario in enumerate(scenarios, 1):
        print(f"Scenario {i}: {scenario['name']}")
        print("-" * 40)

        # Create commit
        commit = Commit(
            commit_id=f"commit_{i}",
            timestamp=datetime.now(),
            state_claimed={"scenario": scenario['name']},
            reasoning=f"Reasoning for {scenario['name']}",
            confidence=scenario['confidence'],
            safety_cleared=True,
            ethics_approved=True,
            ethical_scores={"deontological": 1.0, "consequentialist": 0.8, "virtue": 0.7},
            predicted_outcome=scenario['predicted'],
            jepa_prediction_error=0.2
        )

        # Set actual outcome
        commit.set_outcome(scenario['actual'])

        # Review
        review_result = review_system.review_commit(
            commit,
            active_archetypes=scenario['archetypes']
        )

        # Show results
        print(f"  Predicted: {commit.predicted_outcome}")
        print(f"  Actual: {commit.actual_outcome}")
        print(f"  Result: {review_result['result_type'].upper()}")
        print(f"  Match: {'✓' if review_result['prediction_matches'] else '✗'}")

        if review_result['contradiction_detected']:
            print(f"  ⚠️  CONTRADICTION DETECTED!")
            print(f"      Strength: {review_result['contradiction_strength']:.2f}")

        # Show trust updates
        print(f"  Updated trust scores:")
        for arch, score in review_result['updated_trust_scores'].items():
            delta = score - 0.5  # Assuming started at 0.5
            arrow = "↑" if delta > 0 else "↓" if delta < 0 else "→"
            print(f"    {arch:15s}: {arrow} {score:.3f}")

        print()

    # Final statistics
    print("=" * 80)
    print("FINAL STATISTICS")
    print("=" * 80)
    print()

    stats = review_system.get_stats()
    print(f"Total reviews: {stats['total_reviews']}")
    print(f"Average trust: {stats['average_trust']:.3f}")
    print()

    metrics = stats['metrics']
    print(f"Accuracy rate: {metrics['accuracy_rate']:.1%}")
    print(f"Error rate: {metrics['error_rate']:.1%}")
    print(f"Contradictions: {metrics['contradictions']}")
    print()

    # Generate full report
    print("=" * 80)
    print("ACCOUNTABILITY REPORT")
    print("=" * 80)

    report = review_system.generate_report(last_n=10)

    print("\nRECENT PERFORMANCE:")
    recent = report['recent_performance']
    print(f"  Reviews: {recent['reviews']}")
    print(f"  Accurate: {recent['accurate']}")
    print(f"  Accuracy: {recent['accuracy_rate']:.1%}")
    print(f"  Contradictions: {recent['contradictions']}")

    print("\nTOP PERFORMERS:")
    for performer in report['top_performers']:
        print(f"  {performer['name']:15s}: {performer['score']:.3f}")

    print("\nBOTTOM PERFORMERS:")
    for performer in report['bottom_performers']:
        print(f"  {performer['name']:15s}: {performer['score']:.3f}")

    print()
    print("✅ Review demonstration complete!")
    print()


if __name__ == "__main__":
    demonstrate_review()
