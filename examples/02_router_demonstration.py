"""
Relevance Router Demonstration
===============================

Shows how the router allocates attention across 12 archetypes
based on context and developmental stage.

Author: John Fizer
"""

import sys
sys.path.append('..')

from sarai.core.routing.relevance_router import RelevanceRouter
from sarai.core.routing.archetypes import ARCHETYPES
from sarai.core.world_model.state import StateFeatures
from sarai.safety.logging import ComprehensiveLogger


def print_archetype_list():
    """Print all 12 archetypes."""
    print("THE 12 ARCHETYPES:")
    print()
    for arch in ARCHETYPES:
        print(f"{arch.id:2d}. {arch.name:15s} ({arch.sign:12s}) - {arch.theme}")
    print()


def demonstrate_router():
    """Demonstrate relevance routing."""

    print("=" * 80)
    print("RELEVANCE ROUTER DEMONSTRATION")
    print("=" * 80)
    print()

    print_archetype_list()

    # Initialize
    logger = ComprehensiveLogger("./demo_logs")

    # Test at different developmental stages
    stages_to_test = [1, 4, 8, 12]

    for stage in stages_to_test:
        print("=" * 80)
        print(f"STAGE {stage}: {ARCHETYPES[stage-1].sign} ({ARCHETYPES[stage-1].theme})")
        print("=" * 80)
        print()

        router = RelevanceRouter(
            current_stage=stage,
            logger=logger,
            top_k=3
        )

        # Test different scenarios
        scenarios = [
            ("Low uncertainty, normal", StateFeatures(
                uncertainty=0.3,
                novelty=0.3,
                complexity=0.3,
                time_pressure=0.3,
                irreversibility=0.3,
                stakes=0.3
            )),
            ("High uncertainty", StateFeatures(
                uncertainty=0.9,
                novelty=0.3,
                complexity=0.3,
                time_pressure=0.3,
                irreversibility=0.3,
                stakes=0.3
            )),
            ("Novel situation", StateFeatures(
                uncertainty=0.3,
                novelty=0.9,
                complexity=0.3,
                time_pressure=0.3,
                irreversibility=0.3,
                stakes=0.3
            )),
            ("High complexity", StateFeatures(
                uncertainty=0.3,
                novelty=0.3,
                complexity=0.9,
                time_pressure=0.3,
                irreversibility=0.3,
                stakes=0.3
            )),
            ("High stakes + time pressure", StateFeatures(
                uncertainty=0.3,
                novelty=0.3,
                complexity=0.3,
                time_pressure=0.9,
                irreversibility=0.3,
                stakes=0.9
            )),
        ]

        for scenario_name, features in scenarios:
            print(f"Scenario: {scenario_name}")

            result = router.activate(features)

            print(f"  Top Archetypes: {', '.join(result.active_modules)}")
            print(f"  Reasoning: {result.reasoning}")

            # Show top 5 weights
            sorted_archetypes = sorted(
                enumerate(result.weights),
                key=lambda x: x[1],
                reverse=True
            )[:5]

            print(f"  Weight Distribution:")
            for idx, weight in sorted_archetypes:
                arch = ARCHETYPES[idx]
                bar = "█" * int(weight * 50)
                print(f"    {arch.name:15s}: {bar} {weight:.3f}")

            print()

        # Show router statistics
        stats = router.get_stats()
        print(f"Router Stats:")
        print(f"  Total activations: {stats['total_activations']}")
        print(f"  Most activated: {[a['name'] for a in stats['most_activated'][:3]]}")
        print()

    print("✅ Router demonstration complete!")
    print()


if __name__ == "__main__":
    demonstrate_router()
