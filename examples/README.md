# SARAI Examples & Demonstrations

**Author:** John Fizer  
**Date:** 2026-05-03

---

## Overview

This directory contains examples and demonstrations showing SARAI's cognitive architecture in action.

---

## Quick Start

```bash
# Run the practical integration example:
python practical_decision_advisor.py

# Or run individual demonstrations:
python 01_jepa_demonstration.py
python 02_router_demonstration.py
python 03_commit_demonstration.py
python 04_review_demonstration.py
```

---

## Files

### **Practical Integration** ⭐ START HERE

**`practical_decision_advisor.py`** - Real-world AI Decision Advisor
- **What it shows:** Complete SARAI integration in a practical application
- **Use case:** Personal AI that helps users make decisions and learns from outcomes
- **Features:**
  - Natural language input
  - Context-aware advice generation
  - Prediction with confidence scores
  - Feedback loop and learning
  - Trust score evolution
  - Session statistics

**Expected output:**
```
USER REQUEST:
I received a job offer with 30% higher salary...

🧠 WORLD MODEL STATE:
   Uncertainty: 0.65
   Novelty: 0.61
   Stakes: 0.90

🎯 COGNITIVE ACTIVATION:
   Active archetypes: Analysis, Structure, Relationship

💡 ADVICE:
Create a detailed pros/cons list for each option...

🔮 PREDICTION:
   You'll feel confident in your decision within 1-2 weeks
   Confidence: 82%

📝 COMMITMENT CREATED:
   ID: commit_1234
```

**Runtime:** ~2 minutes (interactive with pauses)

---

### **Individual Module Demonstrations**

**`01_jepa_demonstration.py`** - JEPA World Model
- Shows latent state tracking and prediction
- Demonstrates surprise signal calculation
- ~30 seconds runtime

**`02_router_demonstration.py`** - Relevance Router
- Shows archetype activation across different stages
- Demonstrates context-driven attention allocation
- ~1 minute runtime

**`03_commit_demonstration.py`** - Commit Law FSM
- Complete FSM lifecycle: EXPLORE → EVALUATE → COMMIT → EXECUTE → REVIEW
- Shows immutable commit records and audit trails
- ~30 seconds runtime

**`04_review_demonstration.py`** - Review & Accountability
- Prediction vs outcome comparison
- Trust score updates based on accuracy
- ~30 seconds runtime

---

### **Comprehensive Examples**

**`full_cognitive_cycle.py`** - Complete End-to-End Flow
- All 10 phases of SARAI's cognitive cycle
- Realistic user scenario (job decision advice)
- Shows integration of all modules
- ~1 minute runtime

**`decision_making_with_commitments.py`** - Learning from Outcomes
- 5 different decision scenarios
- Shows prediction accuracy tracking
- Demonstrates trust score evolution
- Accountability report generation
- ~1 minute runtime

**`multi_stage_progression.py`** - Developmental Evolution
- Shows stages 1, 3, 6, 8, 10, 12
- Same scenario interpreted differently at each stage
- Demonstrates dynamic stage transitions
- ~1 minute runtime

---

## What You'll See

### **Terminal Output**

All examples produce formatted terminal output showing:

```
================================================================================
PHASE/SECTION NAME
================================================================================

📊 Data visualization (with bars, numbers)
💭 Reasoning and explanations
✅ Success indicators
⚠️  Warnings or important notes
🔮 Predictions
📝 Commitments
🔎 Reviews

Statistics tables and summaries
```

### **Key Metrics Displayed**

- **JEPA:** Prediction error, surprise, state features
- **Router:** Archetype weights, active modules, compute budget
- **Commit Law:** FSM state, commit IDs, integrity hashes
- **Review:** Trust scores, accuracy rates, contradiction detection

---

## Running Examples

### **Interactive Mode** (Practical Advisor)

```bash
python practical_decision_advisor.py
```

Follow the prompts. Press Enter to advance through scenarios.

### **Automated Mode** (All others)

```bash
python <example_name>.py
```

No interaction needed. Output appears automatically.

### **Modify for Your Use**

Edit the scenario variables in each file:

```python
# In practical_decision_advisor.py
user_input = "Your decision scenario here..."

context = {
    'stakes': 0.9,      # 0-1, how important is this?
    'urgency': 0.6,     # 0-1, time pressure?
    'reversible': False # Can decision be undone?
}
```

---

## Expected Results

### **Demonstrations** (01-04)
- Focused output showing single module behavior
- Statistics and visualizations
- ~10-50 lines of output per section

### **Working Examples** (full_cognitive_cycle, decision_making, multi_stage)
- Comprehensive output showing complete flows
- Multiple phases/scenarios
- Statistics and reports
- ~100-300 lines of output

### **Practical Integration** (practical_decision_advisor)
- Real application behavior
- Natural language interaction
- Advice generation
- Learning demonstration
- Session summary
- ~50-100 lines per scenario

---

## Integration Patterns

These examples demonstrate three integration patterns:

### **1. Module-by-Module** (Demonstrations 01-04)
```python
# Use individual SARAI components
jepa = JEPAWorldModel(...)
state = jepa.update(observation)
features = jepa.get_state_features()
```

### **2. Complete Pipeline** (Comprehensive Examples)
```python
# Chain all components together
perception → JEPA → Router → Reasoning → Commit → Review
```

### **3. Application Wrapper** (Practical Advisor)
```python
# Wrap SARAI in application-specific interface
class MyApplication:
    def __init__(self):
        self.jepa = JEPAWorldModel(...)
        self.router = RelevanceRouter(...)
        # ...

    async def process(self, user_input):
        # SARAI cognitive cycle
        # Application-specific logic
        return result
```

---

## Building Your Own Application

Use `practical_decision_advisor.py` as a template:

1. **Initialize SARAI components** (JEPA, Router, CommitLaw, ReviewSystem)
2. **Create application-specific interface** (your domain logic)
3. **Encode inputs** (text → embeddings)
4. **Run cognitive cycle:**
   - Update JEPA with observations
   - Activate relevant archetypes via Router
   - Generate reasoning (LLM/custom logic)
   - Make commitments via CommitLaw
   - Collect feedback and review outcomes
5. **Learn and adapt** (trust scores, stage progression)

Replace the mock methods (`_encode_text`, `_generate_reasoning`, etc.) with:
- Real embedding models (OpenAI, sentence-transformers)
- Real LLMs (Claude API, GPT-4, local models)
- Domain-specific logic

---

## Dependencies

All examples require:
- Python 3.8+
- NumPy
- PyTorch
- SARAI Phase 1 modules

---

## Next Steps

1. **Run the practical advisor** to see SARAI in action
2. **Study the code** to understand integration patterns
3. **Modify scenarios** to test different situations
4. **Build your own application** using the patterns shown

---

## Support

- Full system documentation: `/docs/`
- API reference: Module docstrings
- Tests: `/tests/` (shows expected behavior)
- Progress tracking: `/PHASE1_PROGRESS.md`

---

**Ready to run?**

```bash
python practical_decision_advisor.py
```

**Watch SARAI make decisions, predict outcomes, and learn from feedback!** 🚀
