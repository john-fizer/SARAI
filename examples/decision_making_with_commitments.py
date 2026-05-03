"""
Decision Making with Commitments Example
=========================================

Shows how SARAI makes multiple decisions with different outcomes,
demonstrating the commit-review loop and learning from results.

Author: John Fizer
"""

import sys
sys.path.append('..')

import asyncio
from datetime import datetime

from sarai.core.commitment.commit_law import CommitLaw
from sarai.core.commitment.records import Commit
from sarai.core.review.accountability import ReviewSystem
from sarai.core.routing.relevance_router import RelevanceRouter
from sarai.core.world_model.state import StateFeatures
from sarai.types import Action, ActionType, EthicalAssessment, ReasoningOutput, AISResult, ARSResult
from sarai.safety.logging import ComprehensiveLogger


async def make_decision(
    scenario_name: str,
    decision_context: str,
    action: Action,
    predicted_outcome: str,
    actual_outcome: str,
    confidence: float,
    active_archetypes: list,
    commit_law: CommitLaw,
    review_system: ReviewSystem
):
    """Make a single decision and review the outcome."""

    print("=" * 80)
    print(f"SCENARIO: {scenario_name}")
    print("=" * 80)
    print()

    print(f"Context: {decision_context}")
    print()

    # EXPLORE
    print("🔍 EXPLORE")
    commit_law.enter_exploration({"scenario": scenario_name})

    # Mock reasoning
    ais_result = AISResult(
        patterns_recognized=["decision_pattern"],
        symbolic_interpretation="Analysis of situation",
        holistic_assessment=f"Considering {scenario_name}",
        confidence=confidence,
        processing_time=0.1
    )

    ars_result = ARSResult(
        logical_chain=["assess situation", "evaluate options", "select action"],
        causal_model={"chosen_action": action.description},
        quantitative_analysis={"expected_value": confidence},
        confidence=confidence,
        processing_time=0.1
    )

    reasoning = ReasoningOutput(
        ais_result=ais_result,
        ars_result=ars_result,
        synthesis=f"Decision: {action.description}",
        confidence=confidence,
        stream_agreement=0.85,
        conflicts=[],
        timestamp=datetime.now()
    )

    # EVALUATE
    print("⚖️  EVALUATE")
    commit_law.begin_evaluation(reasoning, {"action": confidence})
    print(f"   Action: {action.description}")
    print(f"   Confidence: {confidence:.2f}")
    print()

    # Mock ethical assessment
    ethical = EthicalAssessment(
        permitted=True,
        confidence=0.9,
        reason="No ethical concerns",
        deontological_score=1.0,
        consequentialist_score=0.8,
        virtue_score=0.75,
        narrative_patterns=["prudence"],
        timestamp=datetime.now()
    )

    # COMMIT
    print("📝 COMMIT")
    commit = commit_law.decide(
        action=action,
        ethical_assessment=ethical,
        predicted_outcome=predicted_outcome,
        jepa_prediction_error=0.15
    )

    print(f"   Commit ID: {commit.commit_id}")
    print(f"   Predicted: {predicted_outcome}")
    print()

    # EXECUTE
    print("⚡ EXECUTE")
    commit_law.begin_execution(commit.commit_id)
    print(f"   Executing: {action.description}")

    # Simulate execution delay
    await asyncio.sleep(0.1)

    commit_law.complete_execution(commit.commit_id, actual_outcome)
    print(f"   Actual: {actual_outcome}")
    print()

    # REVIEW
    print("🔎 REVIEW")
    review_result = review_system.review_commit(
        commit,
        active_archetypes=active_archetypes
    )

    matches = review_result['prediction_matches']
    print(f"   Prediction match: {'✓ YES' if matches else '✗ NO'}")

    if review_result['contradiction_detected']:
        print(f"   ⚠️  CONTRADICTION DETECTED!")
        print(f"       Strength: {review_result['contradiction_strength']:.2f}")

    print()
    print(f"   Trust updates for active archetypes:")
    for arch in active_archetypes:
        if arch in review_result['updated_trust_scores']:
            score = review_result['updated_trust_scores'][arch]
            delta = score - 0.5
            arrow = "↑" if delta > 0 else "↓" if delta < 0 else "→"
            print(f"     {arch:15s}: {arrow} {score:.3f}")

    print()
    return commit, review_result


async def run_decision_scenarios():
    """Run multiple decision scenarios showing learning over time."""

    print("=" * 80)
    print("DECISION MAKING WITH COMMITMENTS")
    print("=" * 80)
    print()
    print("This example shows SARAI making multiple decisions,")
    print("committing to predicted outcomes, and learning from results.")
    print()

    # Initialize systems
    logger = ComprehensiveLogger("./demo_logs")
    commit_law = CommitLaw(logger)
    review_system = ReviewSystem(logger)
    router = RelevanceRouter(current_stage=6, logger=logger)  # Analysis stage

    print("✅ Systems initialized")
    print()

    # Scenario 1: Accurate prediction with high confidence
    await make_decision(
        scenario_name="Email Response Timing",
        decision_context="User asks when to send important email",
        action=Action(
            action_type=ActionType.COMMUNICATION,
            description="Recommend sending email in morning hours (9-11 AM)",
            parameters={"timing": "morning"},
            stakes=50.0,
            reversible=True
        ),
        predicted_outcome="User sends email in morning, gets quick response",
        actual_outcome="User sent at 10 AM, got response within 2 hours",
        confidence=0.85,
        active_archetypes=["Analysis", "Structure", "Communication"],
        commit_law=commit_law,
        review_system=review_system
    )

    # Scenario 2: Moderate prediction with moderate outcome
    await make_decision(
        scenario_name="Project Deadline Extension",
        decision_context="User asks if they should request deadline extension",
        action=Action(
            action_type=ActionType.COMMUNICATION,
            description="Recommend requesting 3-day extension with justification",
            parameters={"extension_days": 3},
            stakes=120.0,
            reversible=False
        ),
        predicted_outcome="Manager grants 2-3 day extension",
        actual_outcome="Manager granted 2-day extension",
        confidence=0.70,
        active_archetypes=["Analysis", "Relationship", "Structure"],
        commit_law=commit_law,
        review_system=review_system
    )

    # Scenario 3: Overconfident but wrong prediction
    await make_decision(
        scenario_name="Investment Recommendation",
        decision_context="User asks about investing in tech stock",
        action=Action(
            action_type=ActionType.COMMUNICATION,
            description="Recommend waiting for market dip before buying",
            parameters={"action": "wait"},
            stakes=200.0,
            reversible=True
        ),
        predicted_outcome="Stock price drops 10% in next week",
        actual_outcome="Stock price increased 15% instead - missed opportunity",
        confidence=0.90,  # High confidence but wrong!
        active_archetypes=["Analysis", "Value", "Structure"],
        commit_law=commit_law,
        review_system=review_system
    )

    # Scenario 4: Low confidence but accurate
    await make_decision(
        scenario_name="Career Path Advice",
        decision_context="User unsure about career change to consulting",
        action=Action(
            action_type=ActionType.COMMUNICATION,
            description="Suggest trying consulting project before full switch",
            parameters={"approach": "test_first"},
            stakes=150.0,
            reversible=True
        ),
        predicted_outcome="User takes consulting project, finds it matches their skills",
        actual_outcome="User took project, discovered it's a great fit",
        confidence=0.60,  # Low confidence but accurate!
        active_archetypes=["Analysis", "Transformation", "Innovation"],
        commit_law=commit_law,
        review_system=review_system
    )

    # Scenario 5: Another accurate prediction (learning from experience)
    state_features = StateFeatures(
        uncertainty=0.3,
        novelty=0.2,
        complexity=0.4,
        time_pressure=0.3,
        irreversibility=0.2,
        stakes=0.4
    )
    activation = router.activate(state_features)

    await make_decision(
        scenario_name="Meeting Scheduling",
        decision_context="User needs to schedule team meeting",
        action=Action(
            action_type=ActionType.COMMUNICATION,
            description="Recommend Tuesday 2 PM for team meeting",
            parameters={"day": "Tuesday", "time": "2PM"},
            stakes=40.0,
            reversible=True
        ),
        predicted_outcome="Most team members available, high attendance",
        actual_outcome="8/10 team members attended, productive meeting",
        confidence=0.80,
        active_archetypes=activation.active_modules,
        commit_law=commit_law,
        review_system=review_system
    )

    # FINAL ANALYSIS
    print("=" * 80)
    print("CUMULATIVE LEARNING ANALYSIS")
    print("=" * 80)
    print()

    # Commit Law stats
    commit_stats = commit_law.get_stats()
    record_stats = commit_stats['commit_records']

    print("📊 COMMIT LAW STATISTICS:")
    print(f"   Total commits: {record_stats['total_commits']}")
    print(f"   Resolved: {record_stats['resolved']}")
    print(f"   Prediction accuracy: {record_stats['prediction_accuracy']:.1%}")
    print(f"   Average confidence: {record_stats['avg_confidence']:.2f}")
    print()

    # Review system stats
    review_stats = review_system.get_stats()
    metrics = review_stats['metrics']

    print("🔎 REVIEW SYSTEM STATISTICS:")
    print(f"   Total reviews: {review_stats['total_reviews']}")
    print(f"   Accurate predictions: {metrics['accurate_predictions']}")
    print(f"   Errors: {metrics['errors']}")
    print(f"   Contradictions: {metrics['contradictions']}")
    print(f"   Accuracy rate: {metrics['accuracy_rate']:.1%}")
    print(f"   Error rate: {metrics['error_rate']:.1%}")
    print()

    # Trust scores
    print("🏆 ARCHETYPE TRUST SCORES:")
    sorted_trust = sorted(
        review_stats['trust_scores'].items(),
        key=lambda x: x[1],
        reverse=True
    )

    for arch, score in sorted_trust[:8]:
        delta = score - 0.5
        bar = "█" * int(score * 40)
        arrow = "↑" if delta > 0 else "↓" if delta < 0 else "→"
        print(f"   {arch:15s}: {arrow} {bar} {score:.3f}")
    print()

    # Generate accountability report
    print("=" * 80)
    print("ACCOUNTABILITY REPORT")
    print("=" * 80)
    print()

    report = review_system.generate_report(last_n=10)

    print("RECENT PERFORMANCE (last 10):")
    recent = report['recent_performance']
    print(f"   Reviews: {recent['reviews']}")
    print(f"   Accurate: {recent['accurate']}")
    print(f"   Errors: {recent['errors']}")
    print(f"   Accuracy: {recent['accuracy_rate']:.1%}")
    print(f"   Contradictions: {recent['contradictions']}")
    print()

    print("TOP PERFORMING ARCHETYPES:")
    for performer in report['top_performers'][:5]:
        print(f"   {performer['name']:15s}: {performer['score']:.3f} ({performer['predictions']} predictions)")
    print()

    print("BOTTOM PERFORMING ARCHETYPES:")
    for performer in report['bottom_performers'][:3]:
        print(f"   {performer['name']:15s}: {performer['score']:.3f} ({performer['predictions']} predictions)")
    print()

    # Key insights
    print("=" * 80)
    print("KEY INSIGHTS")
    print("=" * 80)
    print()

    print("📈 LEARNING OBSERVED:")
    print("   1. Scenario 3 (Investment): High confidence but WRONG prediction")
    print("      → Trust scores for involved archetypes decreased")
    print("   2. Scenario 4 (Career): Low confidence but ACCURATE prediction")
    print("      → Trust scores for involved archetypes increased")
    print("   3. Overall accuracy improved through trust score adjustments")
    print()

    print("🎯 SYSTEM BEHAVIOR:")
    print(f"   • {record_stats['total_commits']} decisions committed")
    print(f"   • {record_stats['resolved']} outcomes reviewed")
    print(f"   • {metrics['accuracy_rate']:.1%} prediction accuracy")
    print(f"   • Trust scores now guide future decisions")
    print()

    print("=" * 80)
    print("✅ DECISION MAKING DEMONSTRATION COMPLETE!")
    print("=" * 80)
    print()


if __name__ == "__main__":
    asyncio.run(run_decision_scenarios())
