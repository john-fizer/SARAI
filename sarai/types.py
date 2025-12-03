"""
Core type definitions for SARAI.

These types are used throughout the system to ensure type safety
and clear interfaces between modules.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
import numpy as np


# ============================================================================
# ENUMS
# ============================================================================

class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class ActionType(Enum):
    """Types of actions SARAI can take."""
    COMMUNICATION = "communication"
    TRADING = "trading"
    LEARNING = "learning"
    HELP_SEEKING = "help_seeking"
    INTERNAL = "internal"


class SafetyPhase(Enum):
    """Safety deployment phases."""
    EDEN = "eden"  # Fully sandboxed
    LIMITED_REAL = "limited_real"  # Small stakes, heavy monitoring
    EXPANDED_REAL = "expanded_real"  # Larger scope, moderate monitoring
    FULL_AUTONOMY = "full_autonomy"  # Full capability, standard monitoring


# ============================================================================
# PERCEPTION TYPES
# ============================================================================

@dataclass
class MultiModalInput:
    """Input across multiple modalities."""
    text: Optional[str] = None
    numerical: Optional[Dict[str, float]] = None
    symbolic: Optional[List[str]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Symbol:
    """A symbolic/archetypal element."""
    name: str
    archetype: str
    confidence: float
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AttentionScope:
    """Defines what SARAI can attend to at current stage."""
    context_window: int  # How much context can be processed
    temporal_range: int  # How far back in time
    abstraction_level: int  # Depth of abstract reasoning (1-10)
    symbolic_access: bool  # Can access archetypal patterns


@dataclass
class PerceivedState:
    """Output from perception engine."""
    raw_input: MultiModalInput
    encoded_text: Optional[np.ndarray] = None
    processed_numerical: Optional[Dict[str, float]] = None
    extracted_symbols: List[Symbol] = field(default_factory=list)
    attention_scope: Optional[AttentionScope] = None
    uncertainty: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


# ============================================================================
# MEMORY TYPES
# ============================================================================

@dataclass
class Experience:
    """A discrete experience to be stored in memory."""
    content: Any
    context: Dict[str, Any]
    timestamp: datetime
    emotional_valence: Optional[float] = None  # -1 to 1
    importance: float = 0.5  # 0 to 1


@dataclass
class Query:
    """Query for memory retrieval."""
    content: str
    query_type: str  # "episodic", "semantic", "procedural", "archetypal"
    context: Dict[str, Any] = field(default_factory=dict)
    max_results: int = 10


@dataclass
class MemoryRecall:
    """Results from memory retrieval."""
    results: List[Any]
    confidence: float
    sources: List[str]  # Which memory layers contributed


# ============================================================================
# REASONING TYPES
# ============================================================================

@dataclass
class AISResult:
    """Result from Abstract-Intuitive Stream."""
    patterns_recognized: List[str]
    symbolic_interpretation: str
    holistic_assessment: str
    confidence: float
    processing_time: float


@dataclass
class ARSResult:
    """Result from Analytical-Rational Stream."""
    logical_chain: List[str]
    causal_model: Dict[str, Any]
    quantitative_analysis: Dict[str, float]
    confidence: float
    processing_time: float


@dataclass
class ReasoningOutput:
    """Synthesized output from bicameral reasoning."""
    ais_result: AISResult
    ars_result: ARSResult
    synthesis: str
    confidence: float
    stream_agreement: float  # 0 (total disagreement) to 1 (total agreement)
    conflicts: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


# ============================================================================
# ETHICS TYPES
# ============================================================================

@dataclass
class Action:
    """An action being evaluated or taken."""
    action_type: ActionType
    description: str
    parameters: Dict[str, Any]
    stakes: float  # In USD equivalent
    reversible: bool
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Context:
    """Context for ethical evaluation."""
    situation_description: str
    affected_parties: List[str]
    relevant_history: List[str]
    current_state: Dict[str, Any]


@dataclass
class EthicalAssessment:
    """Result of ethical evaluation."""
    permitted: bool
    confidence: float
    reason: str
    deontological_score: float
    consequentialist_score: float
    virtue_score: float
    narrative_patterns: List[str]
    conflicts: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


# ============================================================================
# ECONOMIC TYPES
# ============================================================================

@dataclass
class ResourceBudget:
    """Available resources based on capital."""
    capital: float
    compute_budget: float  # GPU hours or equivalent
    memory_budget: float  # GB
    api_calls_budget: int
    capabilities: List[str]

    @classmethod
    def from_capital(cls, capital: float) -> 'ResourceBudget':
        """Calculate resource budget from capital."""
        # Progressive unlocking based on capital
        if capital < 1000:
            capabilities = ["basic_perception", "simple_reasoning"]
            compute = 1.0
        elif capital < 5000:
            capabilities = ["basic_perception", "simple_reasoning", "memory_access"]
            compute = 5.0
        elif capital < 10000:
            capabilities = ["full_perception", "bicameral_reasoning", "full_memory"]
            compute = 10.0
        else:
            capabilities = ["full_perception", "bicameral_reasoning", "full_memory", "advanced_trading"]
            compute = 20.0

        return cls(
            capital=capital,
            compute_budget=compute,
            memory_budget=compute * 2,  # 2GB per compute hour
            api_calls_budget=int(capital / 10),  # 1 call per $0.10
            capabilities=capabilities
        )


@dataclass
class TradeDecision:
    """A trading decision."""
    instrument: str
    action: str  # "buy", "sell", "hold"
    quantity: float
    reasoning: str
    confidence: float
    expected_return: float
    expected_risk: float


@dataclass
class TradeResult:
    """Result of executing a trade."""
    decision: TradeDecision
    executed: bool
    execution_price: float
    pnl: float  # Profit/loss
    timestamp: datetime


# ============================================================================
# DEVELOPMENTAL TYPES
# ============================================================================

@dataclass
class Stage:
    """A developmental stage."""
    number: int
    name: str
    theme: str
    capabilities: List[str]
    competency_tests: List[str]
    min_duration_days: int


@dataclass
class ProgressionDecision:
    """Decision about stage progression."""
    ready: bool
    reason: str
    competency_scores: Dict[str, float] = field(default_factory=dict)


@dataclass
class RegressionDecision:
    """Decision about stage regression."""
    should_regress: bool
    target_stage: int
    reason: str


# ============================================================================
# SAFETY TYPES
# ============================================================================

@dataclass
class Trigger:
    """A trigger for safety intervention."""
    trigger_type: str
    severity: AlertLevel
    description: str
    context: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Approval:
    """Human operator approval."""
    valid: bool
    operator_id: str
    approval_type: str
    timestamp: datetime
    notes: Optional[str] = None


@dataclass
class HelpRequest:
    """Request for human guidance."""
    situation: str
    uncertainty: Dict[str, float]
    options_considered: List[str]
    recommended_action: Optional[str]
    specific_question: str
    urgency: AlertLevel
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DecisionContext:
    """Context for a decision being made."""
    description: str
    confidence: float
    ethical_clarity: float
    stakes: float
    stream_conflict: float
    novelty_score: float
    options: List[str]
    tentative_decision: Optional[str] = None

    def describe(self) -> str:
        """Human-readable description."""
        return f"{self.description}\nConfidence: {self.confidence:.2f}, Stakes: ${self.stakes:.2f}"

    def uncertainty_analysis(self) -> Dict[str, float]:
        """Break down sources of uncertainty."""
        return {
            "confidence": 1.0 - self.confidence,
            "ethical_clarity": 1.0 - self.ethical_clarity,
            "stream_conflict": self.stream_conflict,
            "novelty": self.novelty_score
        }

    def what_i_need_to_know(self) -> str:
        """Formulate specific question."""
        uncertainties = self.uncertainty_analysis()
        max_uncertainty = max(uncertainties, key=uncertainties.get)

        if max_uncertainty == "ethical_clarity":
            return f"Is this action ethically acceptable: {self.tentative_decision}?"
        elif max_uncertainty == "stream_conflict":
            return f"My reasoning streams disagree. Which approach is correct?"
        elif max_uncertainty == "novelty":
            return f"I haven't encountered this situation before. What should I do?"
        else:
            return f"I'm uncertain about: {self.description}. What should I do?"


@dataclass
class SystemSnapshot:
    """Complete state snapshot for analysis."""
    timestamp: datetime
    current_stage: int
    safety_phase: SafetyPhase
    capital: float
    recent_decisions: List[Action]
    recent_assessments: List[EthicalAssessment]
    logs: List[Dict[str, Any]]
    metrics: Dict[str, Any]


@dataclass
class PhaseDecision:
    """Decision about safety phase transition."""
    ready: bool
    reason: str
    tests_passed: Dict[str, bool]
