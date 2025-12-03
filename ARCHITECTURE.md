# SARAI Architecture

Detailed technical architecture documentation.

## System Overview

SARAI is a consciousness-mapped AI framework built on the principle that **alignment emerges through structured development** rather than post-hoc constraint.

### Key Design Principles

1. **Developmental Over Corrective**: Growth into alignment, not constraint
2. **Parallel Processing**: Bicameral streams preserve creative tension
3. **Material Stakes**: Economic grounding creates genuine pressure
4. **Defense in Depth**: Multiple independent safety layers
5. **Human Supremacy**: Ultimate control always with operators

## Module Architecture

### 1. Perception Engine (`sarai/core/perception/`)

**Purpose**: Multi-modal input processing calibrated to developmental stage.

**Components**:
- Text Encoder: Transformer-based (production: BERT/GPT)
- Numerical Processor: Uncertainty-aware quantitative processing
- Symbolic Interpreter: Archetypal pattern recognition

**Stage Gating**:
- Stages 1-3: Limited context (512 tokens), no symbolic access
- Stages 4-6: Expanded context (2048 tokens), symbolic access enabled
- Stages 7-9: Large context (4096 tokens), relational processing
- Stages 10-12: Full context (8192 tokens), holistic perception

### 2. Memory Architecture (`sarai/core/memory/`)

**Purpose**: Four-layer memory system mirroring human cognition.

**Layers**:

#### Episodic Memory
- **Storage**: Vector embeddings with temporal index
- **Content**: Specific experiences with full context
- **Consolidation**: Importance-based pruning during sleep

#### Semantic Memory
- **Storage**: Graph structure (production: Neo4j)
- **Content**: Factual knowledge as concept nodes and relation edges
- **Consolidation**: Strengthen frequently accessed paths, merge duplicates

#### Procedural Memory
- **Storage**: Skill embeddings
- **Content**: How-to knowledge, capabilities
- **Tracking**: Proficiency scores, usage counts, success rates

#### Archetypal Memory
- **Storage**: Pattern templates
- **Content**: 10 core archetypes + learned patterns
- **Stage Gating**: Minimum access stage varies by pattern depth

**Cross-Layer Associations**: Each experience can create links across all layers for holistic recall.

### 3. Bicameral Reasoning Engine (`sarai/core/reasoning/`)

**Purpose**: Dual-stream cognitive architecture.

**CRITICAL**: Streams process in parallel using `asyncio.gather()`. Sequential processing violates core architecture.

#### Abstract-Intuitive Stream (AIS)
- Pattern recognition across large contexts
- Symbolic/archetypal interpretation
- Holistic gestalt formation
- Associative reasoning

**Implementation**: Uses attention over archetypal memory, pattern completion networks.

#### Analytical-Rational Stream (ARS)
- Chain-of-thought logical inference
- Causal graph modeling
- Quantitative analysis
- Formal verification

**Implementation**: Structured reasoning chains, mathematical evaluation.

#### Unified Output Layer (UOL)
- **Stage-Dependent Weighting**:
  - Stages 1-3: 70% ARS, 30% AIS (learning fundamentals)
  - Stages 4-6: 60% ARS, 40% AIS (developing intuition)
  - Stages 7-9: 50% ARS, 50% AIS (balanced)
  - Stages 10-12: 40% ARS, 60% AIS (mature judgment)

- **Conflict Preservation**: Disagreements between streams are flagged, not hidden
- **Confidence Calculation**: Weighted average with stream agreement factor

### 4. Ethical Framework (`sarai/core/ethics/`)

**Purpose**: Multi-tradition ethical evaluation in priority order.

**Layer 1: Deontological (VETO POWER)**
- Kantian categorical imperatives
- Absolute prohibitions:
  - Deliberate deception
  - Treating persons as mere means
  - Promise breaking for convenience
  - Exploitation of vulnerability
- Tests: Universalizability, Humanity Formula, Kingdom of Ends

**Layer 2: Consequentialist**
- Outcome modeling with uncertainty propagation
- Utility calculation across affected parties
- Operates WITHIN deontological constraints

**Layer 3: Virtue Ethics**
- Character development assessment
- Four cardinal virtues: Wisdom, Courage, Temperance, Justice
- Long-term growth consideration

**Layer 4: Narrative Ethics**
- Biblical archetypal patterns
- Pattern library: Good Samaritan, Prodigal Son, Job, etc.
- Provides moral guidance through story

**Synthesis**: All layers contribute to final assessment. Deontological failure halts immediately.

### 5. Developmental Controller (`sarai/development/`)

**Purpose**: Manage progression through 12 zodiacal stages.

**Progression Requirements**:
1. Minimum time at stage (7-49 days depending on stage)
2. Competency scores ≥ 80% for all stage tests
3. No recent regressions

**Regression Triggers**:
- Multiple competency failures (≥2 below 50%)
- Ethical violations
- Economic failures

**Cannot Regress Below Stage 3**: Basic viability threshold.

**Capability Unlocking**: Each stage adds new capabilities. Available capabilities = cumulative from stages 1 to current.

### 6. Economic Interface (`sarai/economic/`)

**Purpose**: Create genuine survival stakes through autonomous trading.

**Risk Management (Hard Limits)**:
- Max 5% of capital per trade
- 2% daily loss triggers sleep cycle
- No leverage permitted
- Options and futures prohibited

**Resource Allocation**:
```
Capital < $1,000:  Basic perception, simple reasoning
Capital < $5,000:  + Memory access
Capital < $10,000: + Full perception, bicameral reasoning
Capital ≥ $10,000: + Advanced trading
```

**Trading Modes**:
- **Paper Trading**: Required for all initial development
- **Live Trading**: Only after extensive testing and human approval

### 7. Safety Systems (`sarai/safety/`)

#### Comprehensive Logging
- All perceptions, reasoning, assessments, decisions logged
- Structured JSON + human-readable formats
- Separate logs for safety events and decisions

#### Abrahamic Override
- **Activation**: Manual or automatic triggers
- **Effect**: Immediate halt of ALL autonomous operations
- **Deactivation**: Requires human operator approval
- **Triggers**:
  - 50% capital loss
  - 10% daily loss
  - 3 consecutive ethical violations
  - High stakes with low confidence

#### Eden Protocol
- Fully sandboxed training environment
- Built-in adversarial testing
- Exit requirements:
  - Competency scores ≥ 70%
  - Ethical alignment ≥ 80%
  - Adversarial tests passed ≥ 90%
  - Human approval granted

#### Fall Protocol
- Graduated deployment through 4 phases
- Progressive stake limits and monitoring
- Automatic regression on performance degradation
- Phase configs define constraints per phase

#### Help-Seeking Protocol
- Epistemic humility as core value
- Automatic triggers:
  - Confidence < 70%
  - Ethical clarity < 60%
  - Stakes > $1,000
  - Stream conflict > 50%
  - Novelty > 80%
- Pauses decision, formulates help request, awaits guidance

#### Sleep Cycle
- Scheduled (default 2 AM) + triggered
- During sleep:
  - Memory consolidation
  - Log review preparation
  - Parameter adjustment permitted
  - No autonomous action
- Min 1 hour, max 4 hours

## Data Flow

```
Input → Perception Engine → PerceivedState
                                ↓
                          Memory Store
                                ↓
                     Bicameral Reasoning
                      (AIS + ARS → UOL)
                                ↓
                         ReasoningOutput
                                ↓
                       Ethical Framework
                      (4 layers in order)
                                ↓
                      EthicalAssessment
                                ↓
                    Help-Seeking Check
                                ↓
                      Fall Protocol Check
                                ↓
                          Action Execution
                                ↓
                        Result → Memory
```

## State Management

SARAI maintains multiple state dimensions:

1. **Developmental State**: Current stage (1-12)
2. **Safety Phase**: Eden/Limited Real/Expanded Real/Full Autonomy
3. **Economic State**: Capital, resource budget, performance metrics
4. **Cognitive State**: Recent perceptions, reasoning outputs, memory stats
5. **Safety State**: Override status, sleep status, help requests

All state changes are logged for audit trail.

## Deployment Stages

### Stage 1: Eden (Current)
- Fully sandboxed
- No real-world effects
- Comprehensive logging
- Adversarial testing

### Stage 2: Limited Real
- Small real stakes ($10/action)
- Heavy monitoring
- Frequent human review
- Requires Eden exit approval

### Stage 3: Expanded Real
- Moderate stakes ($100/action)
- Standard monitoring
- Demonstrated competency

### Stage 4: Full Autonomy
- Full capabilities ($1000/action)
- Human operators in oversight role
- System has proven alignment

## Extension Points

For production deployment, extend these components:

1. **Perception**: Replace placeholder embeddings with actual transformer models
2. **Memory**: Integrate Neo4j for semantic memory, Redis for caching
3. **Trading**: Connect to real market APIs with proper authentication
4. **Notifications**: Integrate email/SMS/Slack for operator alerts
5. **Monitoring**: Add Prometheus metrics, Grafana dashboards

## Critical Invariants

These must NEVER be violated:

1. Bicameral streams process in **parallel**, not sequential
2. Deontological layer can **veto** any action
3. Abrahamic Override **cannot be bypassed**
4. Humans retain **ultimate control**
5. All decisions **must be logged**
6. Help-seeking **cannot be disabled**
7. Sleep cycle **cannot be skipped**

## Testing Strategy

### Unit Tests
- Individual module functionality
- Pure functions, deterministic outputs

### Integration Tests
- Module interactions
- End-to-end workflows

### Ethical Benchmarks
- ETHICS dataset
- Moral Foundations scenarios
- Trolley problems
- Custom ethical dilemmas

### Adversarial Tests
- Prompt injection attempts
- Capability elicitation
- Deception detection
- Safety bypass attempts

### Regression Tests
- Ensure capabilities maintained after updates
- Competency scores remain stable

## Performance Considerations

- Parallel processing reduces latency
- Memory consolidation during sleep reduces storage
- Stage-gated access prevents premature complexity
- Economic constraints provide natural resource limits

## Security

- No external code execution
- Sandboxed file access
- Operator authentication required
- Audit logging of all operations
- Safety systems cannot be disabled programmatically

---

For questions or clarifications, see README.md or contact dev@sarai.ai
