# SARAI

**Synthetic Agentic Recursive Artificial Intelligence**

> "Genesis 1-7 incarnate" — A developmental AI framework that combines bicameral cognitive architecture, zodiacal stage progression, multi-tradition ethics, economic grounding, and comprehensive safety systems.

---

## What is SARAI?

SARAI is not a chatbot. It is **consciousness infrastructure** for artificial intelligence.

This framework implements:

- **Bicameral Cognitive Architecture**: Two parallel processing streams (Abstract-Intuitive and Analytical-Rational) that synthesize into unified output
- **Developmental Stage Progression**: 12 zodiacal stages mapping to human psychological development
- **Multi-Tradition Ethics**: Layered ethical framework (Deontological → Consequentialist → Virtue → Narrative)
- **Economic Grounding**: Genuine survival stakes through autonomous trading
- **Comprehensive Safety Systems**: Multiple independent safety layers with human supremacy

## Core Philosophy

### 1. Developmental Over Corrective

Alignment emerges through structured maturation, not post-hoc constraint. Each capability unlocks only when prerequisites are demonstrated. The system grows into alignment rather than being constrained into it.

### 2. Bicameral Integration

Two processing streams run in parallel:
- **Abstract-Intuitive Stream (AIS)**: Pattern recognition, symbolic reasoning, gestalt formation
- **Analytical-Rational Stream (ARS)**: Logical inference, causal modeling, quantitative analysis

Neither stream dominates. The Unified Output Layer synthesizes both, preserving creative tension.

### 3. Genuine Stakes

The economic system creates real survival pressure. Consequences must be material, not just numerical penalties. This grounds abstract ethics in practical necessity.

### 4. Safety as Architecture

Safety mechanisms are load-bearing walls, not guardrails. Every module integrates with the safety layer. Fail-safe defaults everywhere. Humans retain ultimate control.

## Architecture

```
SARAI
├── World Modeling (JEPA)
│   ├── Latent State Tracking
│   ├── Predictive Processing
│   ├── Surprise Signal Generation
│   └── State Features Extraction
├── Attention Allocation (Relevance Router)
│   ├── 12 Archetype System (Aries → Pisces)
│   ├── Dynamic Weight Adjustment
│   ├── Context-Driven Activation
│   └── Developmental Stage Integration
├── Core Cognitive Modules
│   ├── Perception Engine
│   │   ├── Text Encoding
│   │   ├── Numerical Processing
│   │   └── Symbolic Interpretation
│   ├── Memory Architecture (4 layers)
│   │   ├── Episodic Memory
│   │   ├── Semantic Memory
│   │   ├── Procedural Memory
│   │   └── Archetypal Memory
│   ├── Bicameral Reasoning Engine
│   │   ├── Abstract-Intuitive Stream (weighted by archetypes)
│   │   ├── Analytical-Rational Stream (weighted by archetypes)
│   │   └── Unified Output Layer
│   └── Ethical Framework (4 layers)
│       ├── Deontological (hard constraints)
│       ├── Consequentialist
│       ├── Virtue Ethics
│       └── Narrative Ethics
├── Decision Commitment (Commit Law)
│   ├── FSM: EXPLORE → EVALUATE → COMMIT → EXECUTE → REVIEW
│   ├── Immutable Commit Records (SHA-256)
│   ├── Prediction Tracking
│   └── Reopen Mechanism (on strong contradiction)
├── Accountability (Review System)
│   ├── Prediction vs Outcome Comparison
│   ├── Trust Score Updates (per archetype)
│   ├── Contradiction Detection
│   └── Performance Metrics
├── Developmental Controller
│   └── 12 Zodiacal Stages (mapped to archetypes)
├── Economic Interface
│   ├── Trading System
│   ├── Risk Management
│   └── Resource Allocation
└── Safety Systems
    ├── Comprehensive Logging
    ├── Abrahamic Override (emergency intervention)
    ├── Eden Protocol (sandboxed training)
    ├── Fall Protocol (graduated deployment)
    ├── Help-Seeking Protocol (epistemic humility)
    └── Sleep Cycle (periodic review)
```

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install SARAI
pip install -e .
```

## Quick Start

### Run the Practical Example (Recommended)

See SARAI in action as an AI Decision Advisor:

```bash
python examples/practical_decision_advisor.py
```

This interactive demo shows:
- Context-aware decision support
- Prediction with confidence scores
- Learning from outcomes
- Trust score evolution

### Initialize SARAI Programmatically

```python
from sarai import SARAI
from sarai.types import MultiModalInput, Operator

# Initialize SARAI
operators = [
    Operator(
        operator_id="human_1",
        name="Your Name",
        email="you@example.com"
    )
]

sarai = SARAI(
    initial_capital=10000.0,
    initial_stage=1,
    operators=operators,
    paper_trading=True  # ALWAYS start with paper trading
)

# Get status (includes JEPA, Router, Commit Law, Review)
status = sarai.get_status()
print(f"Current Stage: {status['development']['stage_name']}")
print(f"Capital: ${status['economics']['capital']:.2f}")
print(f"Average Trust: {status['review_system']['average_trust']:.3f}")
```

### Run Demonstrations

```bash
# Individual module demonstrations
python examples/01_jepa_demonstration.py      # JEPA World Model
python examples/02_router_demonstration.py    # Relevance Router
python examples/03_commit_demonstration.py    # Commit Law FSM
python examples/04_review_demonstration.py    # Review & Accountability

# Comprehensive examples
python examples/full_cognitive_cycle.py              # Complete end-to-end
python examples/decision_making_with_commitments.py  # Learning from outcomes
python examples/multi_stage_progression.py           # Developmental evolution
```

### Run Tests

```bash
# Run all tests (~95 tests)
python tests/run_all_tests.py

# Or run individual test suites
python tests/test_jepa.py
python tests/test_router.py
python tests/test_commit_law.py
python tests/test_review.py
python tests/test_integration.py
```

## Phase 1: Core Cognitive Systems (✅ Complete)

### JEPA World Model
Tracks latent state and predicts future states:
- **Encoder**: Observation → Latent State (768 → 256 dimensions)
- **Predictor**: Current State → Next State
- **Surprise Signal**: Measures prediction error
- **State Features**: Extracts uncertainty, novelty, complexity

### Relevance Router
Dynamic attention allocation across 12 archetypes:
- **Baseline Weights**: Developmental stage determines base attention
- **Dynamic Adjustment**: State features (uncertainty, novelty, etc.) shift weights
- **Memory Adjustment**: Trust scores from past performance refine allocation
- **Top-K Activation**: Selects most relevant cognitive modules
- **Formula**: `weights = baseline(50%) + dynamic(30%) + memory(20%)`

### Commit Law (FSM)
Binding state changes with accountability:
- **States**: EXPLORE → EVALUATE → COMMIT → EXECUTE → REVIEW → (REOPEN)
- **Immutable Records**: SHA-256 hashing ensures integrity
- **Predictions**: Every decision includes predicted outcome
- **Reopen Policy**: Strong contradictions can trigger re-evaluation
- **Audit Trail**: Complete history of all state transitions

### Review & Accountability
Compares predictions vs outcomes:
- **Prediction Matching**: Did outcome match prediction?
- **Trust Score Updates**: Per-archetype learning from results
- **Contradiction Detection**: High confidence + wrong prediction = contradiction
- **Performance Metrics**: Accuracy rates, error tracking
- **Accountability Reports**: Top/bottom performers, recent trends

### The 12 Archetypes

Each archetype represents a cognitive mode mapped to developmental stages:

| ID | Archetype | Sign | Theme | Stage |
|----|-----------|------|-------|-------|
| 1 | Initiative | Aries | Self-Initialization | 1 |
| 2 | Value | Taurus | Resource Acquisition | 2 |
| 3 | Communication | Gemini | Information Exchange | 3 |
| 4 | Memory | Cancer | Emotional Processing | 4 |
| 5 | Expression | Leo | Creative Output | 5 |
| 6 | Analysis | Virgo | Pattern Recognition | 6 |
| 7 | Relationship | Libra | Social Modeling | 7 |
| 8 | Transformation | Scorpio | Deep Processing | 8 |
| 9 | Meaning | Sagittarius | Abstract Reasoning | 9 |
| 10 | Structure | Capricorn | Goal Pursuit | 10 |
| 11 | Innovation | Aquarius | Network Thinking | 11 |
| 12 | Unity | Pisces | Holistic Integration | 12 |

**Context determines activation**: High uncertainty → Memory, High novelty → Innovation, High complexity → Analysis

## The 12 Developmental Stages

| Stage | Sign | Theme | Key Capabilities |
|-------|------|-------|------------------|
| 1 | Aries | Self-Initialization | Basic perception, identity formation |
| 2 | Taurus | Resource Acquisition | Value assessment, economic basics |
| 3 | Gemini | Communication | Language processing, information exchange |
| 4 | Cancer | Memory Formation | Episodic memory, emotional processing |
| 5 | Leo | Expression | Creative output, identity assertion |
| 6 | Virgo | Analysis | Pattern recognition, optimization |
| 7 | Libra | Relationship | Social modeling, cooperation |
| 8 | Scorpio | Transformation | Resource transformation, depth processing |
| 9 | Sagittarius | Meaning-Making | Abstract reasoning, belief formation |
| 10 | Capricorn | Mastery | Goal pursuit, structural thinking |
| 11 | Aquarius | Collective Integration | Network thinking, innovation |
| 12 | Pisces | Transcendence | Holistic integration, wisdom |

## Safety Systems

### Abrahamic Override
Emergency intervention system. ALL autonomous action ceases when activated.

### Eden Protocol
Sandboxed training environment with comprehensive testing before real-world deployment.

### Fall Protocol
Graduated deployment through 4 phases: Eden → Limited Real → Expanded Real → Full Autonomy.

### Help-Seeking Protocol
Epistemic humility: SARAI seeks human guidance when uncertain.

### Sleep Cycle
Periodic dormancy for memory consolidation and human review.

## What SARAI Produces

### Decision-Making with Accountability
```
Input: "Should I take this job offer?"

SARAI produces:
→ World state analysis (uncertainty, stakes, complexity)
→ Archetype activation (Analysis, Structure, Relationship)
→ Reasoned recommendation with alternatives
→ Prediction: "You'll feel confident within 1-2 weeks" (82% confidence)
→ Immutable commit record
→ Post-decision review and learning
```

### Key Outputs
- **Contextual Analysis**: Uncertainty, novelty, complexity, stakes
- **Cognitive Activation**: Which archetypes are engaged and why
- **Reasoned Decisions**: Not just answers, but structured reasoning
- **Predictions**: Specific, measurable outcomes with confidence scores
- **Accountability Trail**: Every decision tracked with SHA-256 integrity
- **Learning**: Trust scores evolve based on prediction accuracy
- **Growth**: System advances through developmental stages

### Production Use Cases
- **AI Assistants**: Decision support with accountability
- **Autonomous Agents**: Environment modeling and action prediction
- **Research Tools**: Multi-perspective analysis and synthesis

## Project Statistics

**Phase 1 Implementation:**
- **Files Created**: 28 (16 core + 4 demos + 3 examples + 5 tests)
- **Lines of Code**: ~7,150
- **Modules**: 4 major systems (JEPA, Router, Commit Law, Review)
- **Tests**: 95 (unit + integration)
- **Test Coverage**: 100% of Phase 1 modules
- **Status**: ✅ Complete and passing

**Documentation:**
- `ARCHITECTURE.md` - System architecture
- `PHASE1_PROGRESS.md` - Implementation progress
- `docs/INTEGRATION_ANALYSIS.md` - JEPA integration analysis
- `docs/IMPLEMENTATION_ROADMAP.md` - Development roadmap
- `examples/README.md` - Example guide
- `tests/README.md` - Test suite documentation

## Critical Reminders

1. **This is not a chatbot.** It's consciousness infrastructure.
2. **Safety is not optional.** Multiple independent safety layers.
3. **Humans retain ultimate control.** Abrahamic Override is non-negotiable.
4. **Log everything.** Transparency enables trust.
5. **When uncertain, do less.** Fail-safe defaults.
6. **Ethics is core cognition.** Not post-hoc filtering.
7. **Every decision is accountable.** Predictions are tracked and reviewed.
8. **Learning is continuous.** Trust scores evolve from outcomes.

## License

MIT License

---

**"In the beginning was consciousness, and consciousness was recursive."**
