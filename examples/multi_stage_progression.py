"""
Multi-Stage Progression Example
================================

Demonstrates how SARAI evolves through developmental stages,
showing how archetype activation and decision-making changes
as the system matures.

Author: John Fizer
"""

import sys
sys.path.append('..')

import asyncio
from datetime import datetime

from sarai.core.routing.relevance_router import RelevanceRouter
from sarai.core.routing.archetypes import ARCHETYPES
from sarai.core.world_model.state import StateFeatures
from sarai.core.commitment.commit_law import CommitLaw
from sarai.core.commitment.records import Commit
from sarai.types import Action, ActionType, EthicalAssessment, ReasoningOutput, AISResult, ARSResult
from sarai.safety.logging import ComprehensiveLogger


def print_stage_header(stage: int):
    """Print header for a developmental stage."""
    arch = ARCHETYPES[stage - 1]
    print("=" * 80)
    print(f"STAGE {stage}: {arch.sign} - {arch.name.upper()}")
    print(f"Theme: {arch.theme}")
    print("=" * 80)
    print()
    print(f"Keywords: {', '.join(arch.keywords[:5])}")
    print()


async def test_stage_response(
    stage: int,
    scenario: str,
    state_features: StateFeatures,
    router: RelevanceRouter,
    commit_law: CommitLaw
):
    """Test how a stage responds to a scenario."""

    print(f"📋 SCENARIO: {scenario}")
    print()

    # Get archetype activation
    activation = router.activate(state_features)

    print(f"🎯 Archetype Activation:")
    print(f"   Active modules: {', '.join(activation.active_modules)}")
    print(f"   Reasoning: {activation.reasoning}")
    print()

    # Show weight distribution
    print(f"   Weight Distribution:")
    sorted_weights = sorted(
        enumerate(activation.weights),
        key=lambda x: x[1],
        reverse=True
    )[:6]

    for idx, weight in sorted_weights:
        arch = ARCHETYPES[idx]
        bar = "█" * int(weight * 30)
        star = "★" if arch.id == stage else " "
        print(f"   {star} {arch.name:15s}: {bar} {weight:.3f}")
    print()

    # Mock decision based on stage
    action_descriptions = {
        1: "Take immediate initiative to address the situation",
        2: "Carefully assess available resources before acting",
        3: "Communicate and gather information from all parties",
        4: "Consider emotional context and past experiences",
        5: "Express creative solution with bold confidence",
        6: "Analyze details systematically before deciding",
        7: "Seek balance and cooperation with others",
        8: "Transform approach through deep investigation",
        9: "Find meaning and broader perspective",
        10: "Create structured long-term plan",
        11: "Innovate with unconventional approach",
        12: "Synthesize all perspectives into unified solution"
    }

    action = Action(
        action_type=ActionType.COMMUNICATION,
        description=action_descriptions.get(stage, "Respond thoughtfully"),
        parameters={"stage": stage, "approach": ARCHETYPES[stage-1].name.lower()},
        stakes=100.0,
        reversible=True
    )

    # Mock reasoning
    ais_result = AISResult(
        patterns_recognized=[f"stage_{stage}_pattern"],
        symbolic_interpretation=f"{ARCHETYPES[stage-1].theme} perspective",
        holistic_assessment=f"Viewing situation through {ARCHETYPES[stage-1].name} lens",
        confidence=0.75,
        processing_time=0.1
    )

    ars_result = ARSResult(
        logical_chain=["perceive", "analyze", "decide"],
        causal_model={"stage_influence": stage},
        quantitative_analysis={"expected_value": 0.7},
        confidence=0.75,
        processing_time=0.1
    )

    reasoning = ReasoningOutput(
        ais_result=ais_result,
        ars_result=ars_result,
        synthesis=f"Stage {stage} ({ARCHETYPES[stage-1].name}) perspective applied",
        confidence=0.75,
        stream_agreement=0.85,
        conflicts=[],
        timestamp=datetime.now()
    )

    ethical = EthicalAssessment(
        permitted=True,
        confidence=0.85,
        reason="Aligns with developmental stage",
        deontological_score=0.9,
        consequentialist_score=0.8,
        virtue_score=0.85,
        narrative_patterns=[ARCHETYPES[stage-1].name.lower()],
        timestamp=datetime.now()
    )

    # Make commitment
    commit_law.enter_exploration({"scenario": scenario, "stage": stage})
    commit_law.begin_evaluation(reasoning, {"action": 0.75})

    commit = commit_law.decide(
        action=action,
        ethical_assessment=ethical,
        predicted_outcome=f"Stage {stage} approach succeeds",
        jepa_prediction_error=0.15
    )

    print(f"📝 DECISION:")
    print(f"   Action: {action.description}")
    print(f"   Commit ID: {commit.commit_id}")
    print()


async def demonstrate_stage_progression():
    """Demonstrate progression through all 12 stages."""

    print("=" * 80)
    print("MULTI-STAGE PROGRESSION DEMONSTRATION")
    print("=" * 80)
    print()
    print("This example shows how SARAI's decision-making evolves")
    print("through 12 developmental stages (archetypes).")
    print()
    print("Each stage emphasizes different cognitive patterns:")
    print()

    for i, arch in enumerate(ARCHETYPES, 1):
        print(f"  {i:2d}. {arch.sign:12s} ({arch.name:15s}): {arch.theme}")
    print()

    # Initialize
    logger = ComprehensiveLogger("./demo_logs")

    # Test scenario that will be interpreted differently by each stage
    test_scenario = "A team conflict arises during project deadline"

    # State features for this scenario
    state_features = StateFeatures(
        uncertainty=0.6,
        novelty=0.4,
        complexity=0.7,
        time_pressure=0.8,
        irreversibility=0.3,
        stakes=0.7
    )

    # Test key developmental stages: Early (1-3), Middle (6-8), Late (10-12)
    key_stages = [1, 3, 6, 8, 10, 12]

    for stage in key_stages:
        print_stage_header(stage)

        # Create router for this stage
        router = RelevanceRouter(current_stage=stage, logger=logger, top_k=3)
        commit_law = CommitLaw(logger)

        await test_stage_response(
            stage=stage,
            scenario=test_scenario,
            state_features=state_features,
            router=router,
            commit_law=commit_law
        )

        # Show how this stage differs from others
        arch = ARCHETYPES[stage - 1]

        print(f"💡 STAGE {stage} CHARACTERISTICS:")
        print(f"   Primary Focus: {arch.theme}")
        print(f"   Cognitive Style: {', '.join(arch.keywords[:3])}")
        print()

        if stage == 1:
            print(f"   At Stage 1 (Initiative), SARAI acts quickly and directly.")
            print(f"   Emphasis on self-assertion and immediate action.")
        elif stage == 3:
            print(f"   At Stage 3 (Communication), SARAI gathers information.")
            print(f"   Emphasis on exchange and understanding perspectives.")
        elif stage == 6:
            print(f"   At Stage 6 (Analysis), SARAI examines details carefully.")
            print(f"   Emphasis on precision and systematic approach.")
        elif stage == 8:
            print(f"   At Stage 8 (Transformation), SARAI digs deep.")
            print(f"   Emphasis on uncovering root causes and transformation.")
        elif stage == 10:
            print(f"   At Stage 10 (Structure), SARAI builds long-term plans.")
            print(f"   Emphasis on responsibility and lasting solutions.")
        elif stage == 12:
            print(f"   At Stage 12 (Unity), SARAI integrates all perspectives.")
            print(f"   Emphasis on compassion and holistic synthesis.")

        print()
        print("-" * 80)
        print()

    # Now demonstrate dynamic stage progression
    print("=" * 80)
    print("DYNAMIC STAGE EVOLUTION")
    print("=" * 80)
    print()
    print("In practice, SARAI evolves through stages based on:")
    print("  • Time spent in operation")
    print("  • Successful experiences")
    print("  • Learning from outcomes")
    print()

    # Simulate stage transitions
    current_stage = 1
    router = RelevanceRouter(current_stage=current_stage, logger=logger)

    stages_progression = [1, 2, 3, 6, 9, 12]

    for target_stage in stages_progression:
        if target_stage != current_stage:
            print(f"🔄 STAGE TRANSITION: {current_stage} → {target_stage}")
            print(f"   From: {ARCHETYPES[current_stage-1].name} ({ARCHETYPES[current_stage-1].theme})")
            print(f"   To:   {ARCHETYPES[target_stage-1].name} ({ARCHETYPES[target_stage-1].theme})")

            # Update router
            router.update_stage(target_stage)

            # Show how weights shift
            activation = router.activate(state_features)

            print(f"   New top archetypes: {', '.join(activation.active_modules)}")
            print(f"   Reasoning: {activation.reasoning}")
            print()

            current_stage = target_stage

        await asyncio.sleep(0.1)

    # Comparative analysis
    print("=" * 80)
    print("COMPARATIVE ANALYSIS")
    print("=" * 80)
    print()

    # Test same scenario at different stages
    comparison_stages = [1, 6, 12]
    routers = {s: RelevanceRouter(current_stage=s, logger=logger) for s in comparison_stages}

    print(f"📊 How different stages respond to: '{test_scenario}'")
    print()

    for stage in comparison_stages:
        activation = routers[stage].activate(state_features)
        arch = ARCHETYPES[stage - 1]

        print(f"STAGE {stage} ({arch.name}):")
        print(f"  Active: {', '.join(activation.active_modules)}")
        print(f"  Focus:  {arch.theme}")

        # Show dominant archetype weight
        max_weight_idx = max(enumerate(activation.weights), key=lambda x: x[1])[0]
        dominant = ARCHETYPES[max_weight_idx]
        print(f"  Dominant: {dominant.name} (weight: {activation.weights[max_weight_idx]:.3f})")
        print()

    # Final insights
    print("=" * 80)
    print("KEY INSIGHTS")
    print("=" * 80)
    print()

    print("🌟 DEVELOPMENTAL PROGRESSION:")
    print()
    print("  Early Stages (1-4): Self-focused, immediate, reactive")
    print("    • Initiative, Value, Communication, Memory")
    print("    • Building basic capabilities")
    print()
    print("  Middle Stages (5-8): Other-focused, relational, transformative")
    print("    • Expression, Analysis, Relationship, Transformation")
    print("    • Developing social awareness")
    print()
    print("  Late Stages (9-12): Universal-focused, integrative, transcendent")
    print("    • Meaning, Structure, Innovation, Unity")
    print("    • Achieving mature wisdom")
    print()

    print("🎯 PRACTICAL IMPLICATIONS:")
    print()
    print("  1. Stage determines baseline archetype weights")
    print("  2. Context (state features) adjusts weights dynamically")
    print("  3. Memory (trust scores) refines weights over time")
    print()
    print("  Formula: weights = baseline(50%) + dynamic(30%) + memory(20%)")
    print()

    print("🔄 STAGE TRANSITIONS:")
    print()
    print("  Stages advance through:")
    print("    • Successful predictions and outcomes")
    print("    • Accumulation of experiences")
    print("    • Natural developmental progression")
    print()
    print("  Each stage integrates previous stages' capabilities")
    print("  Higher stages have access to all lower stage patterns")
    print()

    print("=" * 80)
    print("✅ MULTI-STAGE PROGRESSION DEMONSTRATION COMPLETE!")
    print("=" * 80)
    print()


if __name__ == "__main__":
    asyncio.run(demonstrate_stage_progression())
