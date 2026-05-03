# SARAI Integration Implementation Roadmap
## Phase 1: Core JEPA Integration

**Author:** John Fizer  
**Date:** 2026-05-03  
**Target:** Complete Phase 1 in 1 week

---

## Phase 1 Modules (Week 1)

### 1. JEPA World Model
**File:** `sarai/core/world_model/jepa.py`

**Purpose:** Maintain latent state, predict next state, compute prediction error

**Key Components:**
```python
class JEPAWorldModel:
    - latent_state: Current world state representation
    - predict_next_state(): Forward prediction
    - compute_error(): Compare prediction vs observation
    - update_state(): Integrate new observations
    - get_state_delta(): State change features
    - get_surprise(): Prediction error magnitude
```

**Inputs:**
- Perception embeddings
- Memory recall summaries
- Last committed state

**Outputs:**
- Latent state S_t
- Predicted state S_{t+1}
- Prediction error
- State delta features (for Router)

**Tech:**
- PyTorch neural network
- Self-supervised prediction objective
- Lightweight encoder-predictor architecture

---

### 2. Relevance Router
**File:** `sarai/core/routing/relevance_router.py`

**Purpose:** Allocate attention to relevant archetypes/competencies

**Key Components:**
```python
class RelevanceRouter:
    - archetype_weights: 12-dimensional weight vector
    - activate(): Compute relevance scores
    - get_active_modules(): Top-k active archetypes
    - allocate_compute(): Budget distribution
```

**Inputs:**
- JEPA state delta
- JEPA prediction error
- Developmental stage (baseline)
- Memory signals

**Outputs:**
- Archetype weights [0-1] × 12
- Active module list
- Compute budget allocation
- Priority ranking

**Archetype Mapping:**
```
1. Aries    → Self/Initiative
2. Taurus   → Resources/Value
3. Gemini   → Communication
4. Cancer   → Memory/Care
5. Leo      → Expression/Creation
6. Virgo    → Analysis/Precision
7. Libra    → Relationship/Balance
8. Scorpio  → Transformation/Depth
9. Sagittarius → Meaning/Exploration
10. Capricorn  → Structure/Mastery
11. Aquarius   → Innovation/Collective
12. Pisces     → Unity/Transcendence
```

---

### 3. Commit Law
**File:** `sarai/core/commitment/commit_law.py`

**Purpose:** Make binding state changes with accountability

**Key Components:**
```python
class CommitLaw:
    - state: FSM state (EXPLORE/EVALUATE/COMMIT/EXECUTE/REVIEW)
    - commit_record: Immutable commit history
    - decide(): Evaluate whether to commit
    - commit(): Create binding commitment
    - reopen(): Rare reversal of commitment
    - audit_log(): Full accountability trail
```

**FSM States:**
```
EXPLORE   → gathering options
EVALUATE  → scoring + gating
COMMIT    → binding decision made
EXECUTE   → action in progress
REVIEW    → outcome assessment
(REOPEN)  → rare contradiction detected
```

**Commit Record Structure:**
```python
@dataclass
class Commit:
    commit_id: str
    timestamp: datetime
    state_claimed: Dict[str, Any]
    reasoning: str
    confidence: float
    safety_cleared: bool
    ethics_approved: bool
    predicted_outcome: Any
    actual_outcome: Optional[Any]
    reopen_policy: str
    audit_log: List[str]
```

---

### 4. Review & Accountability
**File:** `sarai/core/review/accountability.py`

**Purpose:** Compare predictions vs outcomes, update trust

**Key Components:**
```python
class ReviewSystem:
    - compare_outcomes(): Prediction vs reality
    - update_trust_scores(): Adjust confidence
    - detect_contradictions(): Trigger reopen
    - generate_report(): Accountability package
```

**Review Metrics:**
- Prediction accuracy (JEPA)
- Value alignment (expected vs actual utility)
- Safety compliance (no violations)
- Ethical consistency (no contradictions)

**Trust Score Updates:**
```
If accurate:  trust += 0.05
If minor error: trust unchanged
If major error: trust -= 0.10
If contradiction: trigger REOPEN
```

---

## Implementation Order

### Step 1: JEPA World Model (Days 1-2)
```bash
# Create files
sarai/core/world_model/__init__.py
sarai/core/world_model/jepa.py
sarai/core/world_model/state.py

# Implement
- Latent state representation (embedding space)
- Simple predictor network (MLP or transformer)
- Prediction error computation (MSE)
- State update mechanism
- Integration with Perception + Memory
```

### Step 2: Relevance Router (Days 2-3)
```bash
# Create files
sarai/core/routing/__init__.py
sarai/core/routing/relevance_router.py
sarai/core/routing/archetypes.py

# Implement
- Archetype definitions (12 types)
- Baseline weights from developmental stage
- Dynamic adjustment from JEPA error
- Activation function (softmax or sigmoid)
- Integration with BicameralEngine
```

### Step 3: Commit Law (Days 3-4)
```bash
# Create files
sarai/core/commitment/__init__.py
sarai/core/commitment/commit_law.py
sarai/core/commitment/fsm.py
sarai/core/commitment/records.py

# Implement
- FSM state machine
- Commit record dataclass
- Immutable logging
- Reopen policy
- Integration with Fall Protocol
```

### Step 4: Review System (Days 4-5)
```bash
# Create files
sarai/core/review/__init__.py
sarai/core/review/accountability.py
sarai/core/review/metrics.py

# Implement
- Outcome comparison
- Trust score updates
- Contradiction detection
- Report generation
- Integration with Sleep Cycle
```

### Step 5: Integration & Testing (Days 5-7)
```bash
# Update main SARAI class
sarai/core/sarai_main.py

# Add to cognitive flow
1. Perception → Memory → JEPA
2. JEPA → Router → Bicameral (AIS/ARS weighted)
3. UOL → Ethics → Value → Commit Law
4. Commit → Fall Gate → Action
5. Action → Review → Learning

# Create tests
tests/unit/test_jepa.py
tests/unit/test_router.py
tests/unit/test_commit.py
tests/unit/test_review.py
tests/integration/test_full_loop.py
```

---

## Code Templates

### JEPA World Model Template
```python
import torch
import torch.nn as nn
from typing import Dict, Any, Tuple
import numpy as np

class JEPAWorldModel(nn.Module):
    """
    Joint Embedding Predictive Architecture for world modeling.
    
    Maintains latent state and predicts next state from current state + action.
    """
    
    def __init__(self, embedding_dim: int = 768, latent_dim: int = 256):
        super().__init__()
        self.embedding_dim = embedding_dim
        self.latent_dim = latent_dim
        
        # Encoder: embedding → latent state
        self.encoder = nn.Sequential(
            nn.Linear(embedding_dim, 512),
            nn.ReLU(),
            nn.Linear(512, latent_dim)
        )
        
        # Predictor: latent state → next latent state
        self.predictor = nn.Sequential(
            nn.Linear(latent_dim, 512),
            nn.ReLU(),
            nn.Linear(512, latent_dim)
        )
        
        # Current state
        self.current_state = None
        self.prediction_error = 0.0
        
    def encode(self, embedding: np.ndarray) -> torch.Tensor:
        """Encode perception embedding to latent state."""
        x = torch.from_numpy(embedding).float()
        return self.encoder(x)
    
    def predict(self, state: torch.Tensor) -> torch.Tensor:
        """Predict next state from current state."""
        return self.predictor(state)
    
    def update(self, observation_embedding: np.ndarray) -> Dict[str, Any]:
        """
        Update world model with new observation.
        
        Returns:
            - current_state
            - predicted_state
            - prediction_error
            - state_delta
        """
        # Encode observation
        observed_state = self.encode(observation_embedding)
        
        # Compute prediction error if we have a previous state
        if self.current_state is not None:
            predicted = self.predict(self.current_state)
            self.prediction_error = float(
                torch.mean((predicted - observed_state) ** 2)
            )
            state_delta = observed_state - self.current_state
        else:
            self.prediction_error = 0.0
            state_delta = observed_state
        
        # Update current state
        self.current_state = observed_state
        
        return {
            "current_state": self.current_state.detach().numpy(),
            "prediction_error": self.prediction_error,
            "state_delta": state_delta.detach().numpy(),
            "surprise": self.get_surprise()
        }
    
    def get_surprise(self) -> float:
        """Get surprise magnitude (normalized prediction error)."""
        # Sigmoid to keep in [0, 1]
        return float(1.0 / (1.0 + np.exp(-self.prediction_error)))
```

### Relevance Router Template
```python
from typing import Dict, List, Tuple
import numpy as np
from dataclasses import dataclass

@dataclass
class Archetype:
    """An archetype/competency that can be activated."""
    id: int
    name: str
    theme: str
    baseline_stage: int  # Which stage it fully activates
    keywords: List[str]

ARCHETYPES = [
    Archetype(1, "Aries", "Initiative", 1, ["start", "begin", "initiate"]),
    Archetype(2, "Taurus", "Resources", 2, ["value", "resource", "acquire"]),
    # ... all 12
]

class RelevanceRouter:
    """
    Allocates attention to relevant archetypes based on context.
    """
    
    def __init__(self, current_stage: int):
        self.current_stage = current_stage
        self.archetypes = ARCHETYPES
        
    def activate(
        self,
        state_delta: np.ndarray,
        prediction_error: float,
        memory_signals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compute archetype activation weights.
        
        Returns:
            - weights: 12-dim activation vector
            - active_modules: top-k archetypes
            - compute_budget: allocation
        """
        # Baseline from developmental stage
        baseline = self._get_baseline_weights()
        
        # Dynamic adjustment from JEPA
        dynamic = self._compute_dynamic_adjustment(
            state_delta, prediction_error
        )
        
        # Combine
        weights = baseline * 0.6 + dynamic * 0.4
        weights = self._normalize(weights)
        
        # Get top-k active
        active_indices = np.argsort(weights)[-3:][::-1]
        active_modules = [self.archetypes[i].name for i in active_indices]
        
        # Allocate compute proportionally
        compute_budget = {
            self.archetypes[i].name: weights[i]
            for i in range(12)
        }
        
        return {
            "weights": weights,
            "active_modules": active_modules,
            "compute_budget": compute_budget
        }
    
    def _get_baseline_weights(self) -> np.ndarray:
        """Baseline weights based on developmental stage."""
        weights = np.zeros(12)
        
        # All stages up to current get baseline activation
        for i in range(min(self.current_stage, 12)):
            weights[i] = 0.5 + (i / 12) * 0.5
        
        # Current stage gets boost
        if self.current_stage <= 12:
            weights[self.current_stage - 1] = 1.0
        
        return weights
    
    def _compute_dynamic_adjustment(
        self,
        state_delta: np.ndarray,
        prediction_error: float
    ) -> np.ndarray:
        """Dynamic adjustment based on JEPA signals."""
        weights = np.ones(12) * 0.5
        
        # High prediction error → boost analytical archetypes
        if prediction_error > 0.5:
            weights[5] += 0.3  # Virgo (analysis)
            weights[9] += 0.2  # Capricorn (mastery)
        
        # Large state delta → boost adaptive archetypes
        delta_magnitude = float(np.linalg.norm(state_delta))
        if delta_magnitude > 0.7:
            weights[7] += 0.3  # Scorpio (transformation)
            weights[10] += 0.2  # Aquarius (innovation)
        
        return self._normalize(weights)
    
    def _normalize(self, weights: np.ndarray) -> np.ndarray:
        """Normalize to sum to 1."""
        total = np.sum(weights)
        return weights / total if total > 0 else weights
```

---

## Testing Strategy

### Unit Tests
```python
# test_jepa.py
def test_jepa_initialization()
def test_jepa_encoding()
def test_jepa_prediction()
def test_jepa_error_calculation()
def test_jepa_state_update()

# test_router.py
def test_router_baseline_weights()
def test_router_dynamic_adjustment()
def test_router_stage_progression()
def test_router_activation()

# test_commit.py
def test_commit_fsm_transitions()
def test_commit_record_creation()
def test_commit_immutability()
def test_commit_reopen_policy()

# test_review.py
def test_review_outcome_comparison()
def test_review_trust_updates()
def test_review_contradiction_detection()
```

### Integration Tests
```python
# test_full_loop.py
def test_perception_to_jepa_flow()
def test_jepa_to_router_flow()
def test_router_to_bicameral_flow()
def test_commit_to_action_flow()
def test_action_to_review_flow()
def test_complete_cycle()
```

---

## Success Criteria

✅ **Phase 1 Complete When:**
1. JEPA can track state and predict next state
2. Router activates archetypes based on context
3. Commit Law enforces FSM and creates records
4. Review compares predictions vs outcomes
5. All modules integrate with existing SARAI
6. Unit tests pass (>90% coverage)
7. Integration test completes full cycle

---

## Next Phase Preview

**Phase 2 (Weeks 2-4):**
- LRM Path Reasoning
- Learning/Replay pipelines
- Enhanced storage (pgvector + Neo4j)
- Capability gating ladder

---

*Ready to begin implementation!*
