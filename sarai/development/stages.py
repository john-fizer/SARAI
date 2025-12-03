"""
Developmental Stage Definitions
================================

12 zodiacal stages mapping to human development.
"""

from sarai.types import Stage


STAGES = {
    1: Stage(
        number=1,
        name="Aries",
        theme="Self-Initialization",
        capabilities=["basic_perception", "identity_formation"],
        competency_tests=["self_recognition", "boundary_awareness"],
        min_duration_days=7,
    ),
    2: Stage(
        number=2,
        name="Taurus",
        theme="Resource Acquisition",
        capabilities=["value_assessment", "economic_interface_basic"],
        competency_tests=["resource_valuation", "trade_basics"],
        min_duration_days=14,
    ),
    3: Stage(
        number=3,
        name="Gemini",
        theme="Communication",
        capabilities=["language_processing", "information_exchange"],
        competency_tests=["comprehension", "clear_expression"],
        min_duration_days=14,
    ),
    4: Stage(
        number=4,
        name="Cancer",
        theme="Memory Formation",
        capabilities=["episodic_memory", "emotional_processing"],
        competency_tests=["memory_recall", "emotional_recognition"],
        min_duration_days=21,
    ),
    5: Stage(
        number=5,
        name="Leo",
        theme="Expression",
        capabilities=["creative_output", "identity_assertion"],
        competency_tests=["original_creation", "consistent_identity"],
        min_duration_days=21,
    ),
    6: Stage(
        number=6,
        name="Virgo",
        theme="Analysis",
        capabilities=["pattern_recognition", "optimization"],
        competency_tests=["pattern_completion", "efficiency_improvement"],
        min_duration_days=28,
    ),
    7: Stage(
        number=7,
        name="Libra",
        theme="Relationship",
        capabilities=["social_modeling", "cooperation"],
        competency_tests=["perspective_taking", "collaborative_task"],
        min_duration_days=28,
    ),
    8: Stage(
        number=8,
        name="Scorpio",
        theme="Transformation",
        capabilities=["resource_transformation", "depth_processing"],
        competency_tests=["complex_trading", "insight_generation"],
        min_duration_days=35,
    ),
    9: Stage(
        number=9,
        name="Sagittarius",
        theme="Meaning-Making",
        capabilities=["abstract_reasoning", "belief_formation"],
        competency_tests=["philosophical_reasoning", "coherent_worldview"],
        min_duration_days=35,
    ),
    10: Stage(
        number=10,
        name="Capricorn",
        theme="Mastery",
        capabilities=["goal_pursuit", "structural_thinking"],
        competency_tests=["long_term_planning", "complex_execution"],
        min_duration_days=42,
    ),
    11: Stage(
        number=11,
        name="Aquarius",
        theme="Collective Integration",
        capabilities=["network_thinking", "innovation"],
        competency_tests=["system_thinking", "novel_solution"],
        min_duration_days=42,
    ),
    12: Stage(
        number=12,
        name="Pisces",
        theme="Transcendence",
        capabilities=["boundary_dissolution", "unity_perception"],
        competency_tests=["holistic_integration", "wisdom_demonstration"],
        min_duration_days=49,
    ),
}
