"""
Archetype Definitions
=====================

12 archetypes corresponding to zodiacal stages.
Each represents a mode of cognition/competency.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class Archetype:
    """
    An archetypal mode of cognition/competency.

    Maps to zodiacal signs and developmental stages.
    """
    id: int
    name: str
    sign: str
    theme: str
    baseline_stage: int  # Which stage it fully activates
    keywords: List[str]
    description: str


# The 12 Archetypes (aligned with zodiacal stages)
ARCHETYPES = [
    Archetype(
        id=1,
        name="Initiative",
        sign="Aries",
        theme="Self-Initialization / Beginning",
        baseline_stage=1,
        keywords=["start", "begin", "initiate", "self", "action", "direct"],
        description="First action, self-assertion, direct engagement with world"
    ),

    Archetype(
        id=2,
        name="Value",
        sign="Taurus",
        theme="Resource Acquisition / Stability",
        baseline_stage=2,
        keywords=["value", "resource", "acquire", "stable", "material", "worth"],
        description="Resource valuation, stability seeking, material engagement"
    ),

    Archetype(
        id=3,
        name="Communication",
        sign="Gemini",
        theme="Information Exchange / Duality",
        baseline_stage=3,
        keywords=["communicate", "exchange", "language", "information", "dual", "connect"],
        description="Information processing, communication, connecting disparate elements"
    ),

    Archetype(
        id=4,
        name="Memory",
        sign="Cancer",
        theme="Memory Formation / Care",
        baseline_stage=4,
        keywords=["remember", "care", "nurture", "protect", "emotion", "past"],
        description="Memory integration, emotional processing, protective care"
    ),

    Archetype(
        id=5,
        name="Expression",
        sign="Leo",
        theme="Creative Expression / Identity",
        baseline_stage=5,
        keywords=["express", "create", "identity", "radiate", "unique", "center"],
        description="Creative expression, identity assertion, radiating presence"
    ),

    Archetype(
        id=6,
        name="Analysis",
        sign="Virgo",
        theme="Pattern Recognition / Precision",
        baseline_stage=6,
        keywords=["analyze", "pattern", "precise", "refine", "detail", "improve"],
        description="Analytical processing, pattern recognition, refinement"
    ),

    Archetype(
        id=7,
        name="Relationship",
        sign="Libra",
        theme="Balance / Cooperation",
        baseline_stage=7,
        keywords=["balance", "relate", "cooperate", "harmony", "other", "fair"],
        description="Relational thinking, balance seeking, cooperative engagement"
    ),

    Archetype(
        id=8,
        name="Transformation",
        sign="Scorpio",
        theme="Deep Change / Intensity",
        baseline_stage=8,
        keywords=["transform", "depth", "intense", "merge", "power", "hidden"],
        description="Transformative processing, depth exploration, intensity"
    ),

    Archetype(
        id=9,
        name="Meaning",
        sign="Sagittarius",
        theme="Meaning-Making / Expansion",
        baseline_stage=9,
        keywords=["meaning", "expand", "explore", "philosophy", "belief", "far"],
        description="Meaning-making, philosophical reasoning, expansive thinking"
    ),

    Archetype(
        id=10,
        name="Structure",
        sign="Capricorn",
        theme="Mastery / Organization",
        baseline_stage=10,
        keywords=["structure", "master", "organize", "achieve", "discipline", "build"],
        description="Structural thinking, mastery pursuit, organizational capacity"
    ),

    Archetype(
        id=11,
        name="Innovation",
        sign="Aquarius",
        theme="Collective Integration / Revolution",
        baseline_stage=11,
        keywords=["innovate", "collective", "future", "network", "unusual", "freedom"],
        description="Innovative thinking, collective awareness, network cognition"
    ),

    Archetype(
        id=12,
        name="Unity",
        sign="Pisces",
        theme="Transcendence / Dissolution",
        baseline_stage=12,
        keywords=["transcend", "dissolve", "unity", "spiritual", "boundless", "flow"],
        description="Unifying perception, boundary dissolution, transcendent awareness"
    ),
]


def get_archetype_by_id(archetype_id: int) -> Archetype:
    """Get archetype by ID (1-12)."""
    for arch in ARCHETYPES:
        if arch.id == archetype_id:
            return arch
    raise ValueError(f"Invalid archetype ID: {archetype_id}")


def get_archetype_by_stage(stage: int) -> Archetype:
    """Get primary archetype for developmental stage."""
    return get_archetype_by_id(min(stage, 12))


def get_archetype_by_sign(sign: str) -> Archetype:
    """Get archetype by zodiacal sign name."""
    for arch in ARCHETYPES:
        if arch.sign.lower() == sign.lower():
            return arch
    raise ValueError(f"Invalid sign: {sign}")
