"""
Commit Law Demonstration
========================

Shows the FSM lifecycle: EXPLORE → EVALUATE → COMMIT → EXECUTE → REVIEW

Author: John Fizer
"""

import sys
sys.path.append('..')

from datetime import datetime
from sarai.core.commitment.commit_law import CommitLaw
from sarai.core.commitment.fsm import CommitState
from sarai.types import Action, ActionType, EthicalAssessment
from sarai.safety.logging import ComprehensiveLogger


def demonstrate_commit_law():
    """Demonstrate commit law FSM."""

    print("=" * 80)
    print("COMMIT LAW DEMONSTRATION")
    print("=" * 80)
    print()

    # Initialize
    logger = ComprehensiveLogger("./demo_logs")
    commit_law = CommitLaw(logger)

    print("✅ Commit Law initialized")
    print(f"   Current state: {commit_law.get_current_state().value}")
    print()

    # 1. EXPLORE
    print("🔍 PHASE 1: EXPLORE")
    print("-" * 80)

    commit_law.enter_exploration({"situation": "deciding on action"})
    print(f"Entered {commit_law.get_current_state().value} state")

    # Add options
    options = [
        {"action": "option_a", "description": "Safe conservative approach"},
        {"action": "option_b", "description": "Bold innovative approach"},
        {"action": "option_c", "description": "Balanced middle ground"}
    ]

    for opt in options:
        commit_law.add_option(opt)
        print(f"  Added option: {opt['description']}")

    print()

    # 2. EVALUATE
    print("⚖️  PHASE 2: EVALUATE")
    print("-" * 80)

    # Mock reasoning
    from sarai.types import ReasoningOutput, AISResult, ARSResult

    ais_result = AISResult(
        patterns_recognized=["balanced_approach"],
        symbolic_interpretation="Middle path seems wise",
        holistic_assessment="Option C balances innovation with safety",
        confidence=0.75,
        processing_time=0.1
    )

    ars_result = ARSResult(
        logical_chain=["analyze options", "compare risks", "select best"],
        causal_model={"chosen": "option_c"},
        quantitative_analysis={"expected_value": 0.7},
        confidence=0.80,
        processing_time=0.1
    )

    reasoning = ReasoningOutput(
        ais_result=ais_result,
        ars_result=ars_result,
        synthesis="Option C (balanced) recommended",
        confidence=0.77,
        stream_agreement=0.9,
        conflicts=[],
        timestamp=datetime.now()
    )

    scores = {"option_a": 0.6, "option_b": 0.5, "option_c": 0.8}

    commit_law.begin_evaluation(reasoning, scores)
    print(f"Entered {commit_law.get_current_state().value} state")
    print(f"  Scores: {scores}")
    print(f"  Reasoning confidence: {reasoning.confidence:.2f}")
    print()

    # 3. COMMIT
    print("📝 PHASE 3: COMMIT")
    print("-" * 80)

    # Create action
    action = Action(
        action_type=ActionType.COMMUNICATION,
        description="Execute option C: balanced approach",
        parameters={"option": "c"},
        stakes=100.0,
        reversible=True
    )

    # Mock ethical assessment
    ethical = EthicalAssessment(
        permitted=True,
        confidence=0.85,
        reason="No ethical concerns",
        deontological_score=1.0,
        consequentialist_score=0.8,
        virtue_score=0.75,
        narrative_patterns=["wisdom", "balance"],
        timestamp=datetime.now()
    )

    # Make commitment
    commit = commit_law.decide(
        action=action,
        ethical_assessment=ethical,
        predicted_outcome="positive result",
        jepa_prediction_error=0.2
    )

    if commit:
        print(f"✓ Commitment created: {commit.commit_id}")
        print(f"  State claimed: {commit.state_claimed['action_description']}")
        print(f"  Confidence: {commit.confidence:.2f}")
        print(f"  Predicted outcome: {commit.predicted_outcome}")
        print(f"  Hash: {commit._hash[:16]}...")
        print()

    # 4. EXECUTE
    print("⚡ PHASE 4: EXECUTE")
    print("-" * 80)

    commit_law.begin_execution(commit.commit_id)
    print(f"Entered {commit_law.get_current_state().value} state")
    print(f"  Executing: {action.description}")
    print()

    # Simulate execution
    import time
    print("  ... executing ...")
    time.sleep(0.5)
    print()

    # Complete execution with outcome
    actual_outcome = "positive result"  # Matches prediction!

    commit_law.complete_execution(commit.commit_id, actual_outcome)
    print(f"Execution complete")
    print(f"  Actual outcome: {actual_outcome}")
    print(f"  Matches prediction: {commit.matches_prediction()}")
    print()

    # 5. REVIEW
    print("🔎 PHASE 5: REVIEW")
    print("-" * 80)

    print(f"Entered {commit_law.get_current_state().value} state")
    print(f"  Predicted: {commit.predicted_outcome}")
    print(f"  Actual: {commit.actual_outcome}")
    print(f"  Match: {'✓ YES' if commit.matches_prediction() else '✗ NO'}")
    print()

    # Show audit log
    print("AUDIT LOG:")
    for entry in commit.audit_log:
        print(f"  {entry}")
    print()

    # Statistics
    print("=" * 80)
    print("FINAL STATISTICS")
    print("=" * 80)

    stats = commit_law.get_stats()
    print(f"Current state: {stats['current_state']}")
    print(f"Total transitions: {stats['total_transitions']}")
    print(f"State path: {' → '.join(stats['state_path'])}")
    print()

    record_stats = stats['commit_records']
    print(f"Total commits: {record_stats['total_commits']}")
    print(f"Resolved: {record_stats['resolved']}")
    print(f"Prediction accuracy: {record_stats['prediction_accuracy']:.1%}")
    print(f"Integrity verified: {record_stats['integrity_verified']}")
    print()

    print("✅ Commit Law demonstration complete!")
    print()


if __name__ == "__main__":
    demonstrate_commit_law()
