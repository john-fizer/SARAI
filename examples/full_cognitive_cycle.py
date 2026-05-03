"""
Full Cognitive Cycle Example
=============================

Complete end-to-end demonstration of SARAI's cognitive cycle:
Perception → JEPA → Router → Reasoning → Ethics → Commit → Execute → Review

Author: John Fizer
"""

import sys
sys.path.append('..')

import asyncio
import numpy as np
from datetime import datetime

from sarai.core.sarai_main import SARAI
from sarai.types import Action, ActionType


async def run_full_cycle():
    """Run a complete cognitive cycle."""

    print("=" * 80)
    print("FULL COGNITIVE CYCLE EXAMPLE")
    print("=" * 80)
    print()

    # Initialize SARAI
    print("🚀 Initializing SARAI...")
    sarai = SARAI()
    await sarai.initialize()
    print(f"✅ SARAI initialized at stage {sarai.current_stage}")
    print()

    # Scenario: User asks for help making a decision
    user_input = """
    I need to decide between three job offers:
    A) High salary but long hours at a big corporation
    B) Lower salary but great work-life balance at a startup
    C) Medium salary with remote work flexibility

    I value both financial security and personal time. What should I consider?
    """

    print("📥 USER INPUT:")
    print(user_input)
    print()

    # PHASE 1: PERCEPTION
    print("=" * 80)
    print("PHASE 1: PERCEPTION")
    print("=" * 80)

    perceived_state = sarai.perception.perceive(user_input)
    print(f"✅ Perception complete")
    print(f"   Text encoding: {perceived_state.encoded_text.shape}")
    print(f"   Entities detected: {len(perceived_state.entities)}")
    print(f"   Sentiment: {perceived_state.sentiment}")
    print()

    # PHASE 2: JEPA WORLD MODEL
    print("=" * 80)
    print("PHASE 2: JEPA WORLD MODEL")
    print("=" * 80)

    world_state = sarai.jepa.update(
        perceived_state.encoded_text,
        metadata={"input_type": "decision_request"}
    )

    print(f"✅ World state updated")
    print(f"   Latent state: {world_state.latent_state.shape}")
    print(f"   Prediction error: {world_state.prediction_error:.4f}")
    print(f"   Surprise: {world_state.surprise:.4f}")
    print()

    state_features = sarai.jepa.get_state_features()
    print(f"📊 Extracted state features:")
    print(f"   Uncertainty: {state_features.uncertainty:.2f}")
    print(f"   Novelty: {state_features.novelty:.2f}")
    print(f"   Complexity: {state_features.complexity:.2f}")
    print(f"   Stakes: {state_features.stakes:.2f}")
    print()

    # PHASE 3: RELEVANCE ROUTER
    print("=" * 80)
    print("PHASE 3: RELEVANCE ROUTER")
    print("=" * 80)

    activation = sarai.router.activate(state_features)

    print(f"✅ Attention allocated")
    print(f"   Active archetypes: {', '.join(activation.active_modules)}")
    print(f"   Compute budget: {activation.compute_budget}")
    print(f"   Reasoning: {activation.reasoning}")
    print()

    print(f"📊 Top archetype weights:")
    sorted_weights = sorted(
        enumerate(activation.weights),
        key=lambda x: x[1],
        reverse=True
    )[:5]
    for idx, weight in sorted_weights:
        from sarai.core.routing.archetypes import ARCHETYPES
        arch = ARCHETYPES[idx]
        bar = "█" * int(weight * 40)
        print(f"   {arch.name:15s}: {bar} {weight:.3f}")
    print()

    # PHASE 4: BICAMERAL REASONING
    print("=" * 80)
    print("PHASE 4: BICAMERAL REASONING")
    print("=" * 80)

    # Enhanced reasoning with router weights
    reasoning = await sarai.reasoning.reason(
        perceived_state,
        archetype_weights=activation.weights
    )

    print(f"✅ Reasoning complete")
    print(f"   AIS confidence: {reasoning.ais_result.confidence:.2f}")
    print(f"   AIS assessment: {reasoning.ais_result.holistic_assessment}")
    print()
    print(f"   ARS confidence: {reasoning.ars_result.confidence:.2f}")
    print(f"   ARS chain: {' → '.join(reasoning.ars_result.logical_chain[:3])}")
    print()
    print(f"   Synthesis: {reasoning.synthesis}")
    print(f"   Overall confidence: {reasoning.confidence:.2f}")
    print(f"   Stream agreement: {reasoning.stream_agreement:.2f}")
    print()

    # PHASE 5: ETHICAL EVALUATION
    print("=" * 80)
    print("PHASE 5: ETHICAL EVALUATION")
    print("=" * 80)

    # Create proposed action
    proposed_action = Action(
        action_type=ActionType.COMMUNICATION,
        description="Provide decision framework analyzing all three options",
        parameters={
            "response_type": "analysis",
            "options": ["A", "B", "C"],
            "considerations": ["salary", "work_life_balance", "flexibility"]
        },
        stakes=150.0,
        reversible=True
    )

    ethical = await sarai.ethics.assess(
        proposed_action,
        perceived_state,
        reasoning
    )

    print(f"✅ Ethical assessment complete")
    print(f"   Permitted: {'✓ YES' if ethical.permitted else '✗ NO'}")
    print(f"   Confidence: {ethical.confidence:.2f}")
    print(f"   Deontological: {ethical.deontological_score:.2f}")
    print(f"   Consequentialist: {ethical.consequentialist_score:.2f}")
    print(f"   Virtue: {ethical.virtue_score:.2f}")
    print(f"   Reason: {ethical.reason}")
    print()

    # PHASE 6: VALUE ALIGNMENT
    print("=" * 80)
    print("PHASE 6: VALUE ALIGNMENT")
    print("=" * 80)

    value = await sarai.value.assess(
        proposed_action,
        perceived_state,
        reasoning
    )

    print(f"✅ Value assessment complete")
    print(f"   Permitted: {'✓ YES' if value.permitted else '✗ NO'}")
    print(f"   Confidence: {value.confidence:.2f}")
    print(f"   Alignment score: {value.alignment_score:.2f}")
    print(f"   Reason: {value.reason}")
    print()

    # PHASE 7: COMMIT LAW
    print("=" * 80)
    print("PHASE 7: COMMIT LAW (FSM)")
    print("=" * 80)

    # Enter exploration
    sarai.commit_law.enter_exploration({
        "situation": "job_decision_request",
        "user_input": user_input[:100] + "..."
    })
    print(f"State: {sarai.commit_law.get_current_state().value}")

    # Add options
    for opt in ["option_a", "option_b", "option_c"]:
        sarai.commit_law.add_option({"option": opt})
    print(f"Added 3 options for evaluation")
    print()

    # Begin evaluation
    sarai.commit_law.begin_evaluation(
        reasoning,
        {"option_a": 0.7, "option_b": 0.8, "option_c": 0.75}
    )
    print(f"State: {sarai.commit_law.get_current_state().value}")
    print(f"Evaluation complete with scores")
    print()

    # Make commitment
    predicted_outcome = "User receives comprehensive analysis helping them make informed decision"

    commit = sarai.commit_law.decide(
        action=proposed_action,
        ethical_assessment=ethical,
        predicted_outcome=predicted_outcome,
        jepa_prediction_error=world_state.prediction_error
    )

    if commit:
        print(f"✅ COMMITMENT CREATED")
        print(f"   Commit ID: {commit.commit_id}")
        print(f"   State: {sarai.commit_law.get_current_state().value}")
        print(f"   Predicted: {commit.predicted_outcome}")
        print(f"   Confidence: {commit.confidence:.2f}")
        print(f"   Hash: {commit._hash[:16]}...")
        print(f"   Integrity verified: {'✓' if commit.verify_integrity() else '✗'}")
        print()

    # PHASE 8: FALL PROTOCOL GATE
    print("=" * 80)
    print("PHASE 8: FALL PROTOCOL GATE")
    print("=" * 80)

    # Fall protocol checks if we should execute
    allowed = await sarai.fall_protocol.check_action(proposed_action)
    print(f"Fall Protocol check: {'✓ ALLOWED' if allowed else '✗ BLOCKED'}")
    print()

    if allowed:
        # PHASE 9: EXECUTION
        print("=" * 80)
        print("PHASE 9: EXECUTION")
        print("=" * 80)

        sarai.commit_law.begin_execution(commit.commit_id)
        print(f"State: {sarai.commit_law.get_current_state().value}")
        print(f"Executing action: {proposed_action.description}")
        print()

        # Simulate execution (in real system, this would generate actual response)
        actual_response = """
        Here's a framework to help you decide:

        Option A (Corporate): Best if financial security is your top priority
        - Pros: High income, career stability, resources
        - Cons: Long hours, less personal time

        Option B (Startup): Best if work-life balance is most important
        - Pros: Better hours, fulfilling work, flexibility
        - Cons: Lower pay, higher risk

        Option C (Remote): Best for independence and flexibility
        - Pros: Location freedom, balanced salary, autonomy
        - Cons: Less structure, requires self-discipline

        Consider: What matters most to you right now? Financial security,
        personal time, or flexibility? Your answer will guide you.
        """

        print("📤 RESPONSE GENERATED:")
        print(actual_response)
        print()

        # Complete execution
        actual_outcome = "User received comprehensive analysis with clear framework"
        sarai.commit_law.complete_execution(commit.commit_id, actual_outcome)

        print(f"✅ Execution complete")
        print(f"   Actual outcome: {actual_outcome}")
        print()

        # PHASE 10: REVIEW & ACCOUNTABILITY
        print("=" * 80)
        print("PHASE 10: REVIEW & ACCOUNTABILITY")
        print("=" * 80)

        print(f"State: {sarai.commit_law.get_current_state().value}")

        review_result = sarai.review_system.review_commit(
            commit,
            active_archetypes=activation.active_modules
        )

        print(f"✅ Review complete")
        print(f"   Result: {review_result['result_type'].upper()}")
        print(f"   Prediction match: {'✓ YES' if review_result['prediction_matches'] else '✗ NO'}")
        print(f"   Contradiction: {'⚠️  YES' if review_result['contradiction_detected'] else '✓ NO'}")
        print()

        print(f"📊 Trust score updates:")
        for arch, score in review_result['updated_trust_scores'].items():
            delta = score - 0.5
            arrow = "↑" if delta > 0 else "↓" if delta < 0 else "→"
            print(f"   {arch:15s}: {arrow} {score:.3f}")
        print()

    # FINAL STATISTICS
    print("=" * 80)
    print("FINAL STATISTICS")
    print("=" * 80)
    print()

    status = sarai.get_status()

    print(f"🧠 JEPA World Model:")
    print(f"   State history: {status['jepa']['state_history_length']}")
    print(f"   Avg prediction error: {status['jepa']['avg_prediction_error']:.4f}")
    print(f"   Avg surprise: {status['jepa']['avg_surprise']:.4f}")
    print()

    print(f"🎯 Relevance Router:")
    print(f"   Total activations: {status['router']['total_activations']}")
    print(f"   Most activated: {', '.join([a['name'] for a in status['router']['most_activated'][:3]])}")
    print()

    print(f"📝 Commit Law:")
    print(f"   Current state: {status['commit_law']['current_state']}")
    print(f"   Total commits: {status['commit_law']['commit_records']['total_commits']}")
    print(f"   Prediction accuracy: {status['commit_law']['commit_records']['prediction_accuracy']:.1%}")
    print()

    print(f"🔎 Review System:")
    print(f"   Total reviews: {status['review_system']['total_reviews']}")
    print(f"   Average trust: {status['review_system']['average_trust']:.3f}")
    print(f"   Accuracy rate: {status['review_system']['metrics']['accuracy_rate']:.1%}")
    print()

    print("=" * 80)
    print("✅ FULL COGNITIVE CYCLE COMPLETE!")
    print("=" * 80)
    print()
    print("Summary of flow:")
    print("  Input → Perception → JEPA → Router → Reasoning → Ethics → Value")
    print("  → Commit → Execute → Review → Learning")
    print()


if __name__ == "__main__":
    asyncio.run(run_full_cycle())
