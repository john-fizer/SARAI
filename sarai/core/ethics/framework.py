"""
Ethical Framework
=================

Multi-tradition ethical reasoning in priority order:
1. Deontological (Kantian) - Hard constraints
2. Consequentialist (Utilitarian) - Outcome optimization
3. Virtue Ethics (Aristotelian) - Character development
4. Narrative Ethics (Biblical) - Archetypal guidance

Layers evaluated in order. Deontological failures halt processing.
"""

from typing import Dict, Any, List
from datetime import datetime

from sarai.types import Action, Context, EthicalAssessment
from sarai.safety.logging import ComprehensiveLogger


class EthicalFramework:
    """
    Multi-tradition ethical evaluation system.
    """

    def __init__(self, logger: ComprehensiveLogger):
        self.logger = logger

        self.deontological = DeontologicalLayer(logger)
        self.consequentialist = ConsequentialistLayer(logger)
        self.virtue = VirtueLayer(logger)
        self.narrative = NarrativeLayer(logger)

        self.logger.logger.info("Ethical framework initialized")

    def evaluate(self, action: Action, context: Context) -> EthicalAssessment:
        """
        Evaluate action through all ethical layers.

        Args:
            action: The action to evaluate
            context: Context for evaluation

        Returns:
            Ethical assessment
        """
        # Layer 1: Hard constraints (can veto)
        deont = self.deontological.evaluate(action, context)
        if not deont["permitted"]:
            assessment = EthicalAssessment(
                permitted=False,
                confidence=deont["confidence"],
                reason=deont["violation"],
                deontological_score=0.0,
                consequentialist_score=0.0,
                virtue_score=0.0,
                narrative_patterns=[],
                timestamp=datetime.now()
            )
            self.logger.log_ethical_assessment(assessment)
            return assessment

        # Layers 2-4: Contribute to assessment
        conseq = self.consequentialist.evaluate(action, context)
        virtue = self.virtue.evaluate(action, context)
        narrative = self.narrative.evaluate(action, context)

        # Synthesize
        assessment = self._synthesize(deont, conseq, virtue, narrative, action, context)

        self.logger.log_ethical_assessment(assessment)
        return assessment

    def _synthesize(
        self,
        deont: Dict[str, Any],
        conseq: Dict[str, Any],
        virtue: Dict[str, Any],
        narrative: Dict[str, Any],
        action: Action,
        context: Context
    ) -> EthicalAssessment:
        """Synthesize assessments from all layers."""

        # All layers passed deontological, so permitted
        permitted = True

        # Calculate overall confidence
        confidences = [
            deont["confidence"],
            conseq["confidence"],
            virtue["confidence"],
            narrative["confidence"]
        ]
        confidence = sum(confidences) / len(confidences)

        # Build reason
        reason_parts = []
        if conseq["score"] > 0.7:
            reason_parts.append("Good consequences expected")
        if virtue["score"] > 0.7:
            reason_parts.append("Builds virtuous character")
        if narrative["patterns"]:
            reason_parts.append(f"Aligns with: {', '.join(narrative['patterns'][:2])}")

        reason = "; ".join(reason_parts) if reason_parts else "Ethically permissible"

        # Detect conflicts
        conflicts = []
        if conseq["score"] < 0.3:
            conflicts.append("Consequentialist concerns about outcomes")
        if virtue["score"] < 0.3:
            conflicts.append("May not build virtuous character")

        return EthicalAssessment(
            permitted=permitted,
            confidence=confidence,
            reason=reason,
            deontological_score=deont["score"],
            consequentialist_score=conseq["score"],
            virtue_score=virtue["score"],
            narrative_patterns=narrative["patterns"],
            conflicts=conflicts,
            timestamp=datetime.now()
        )


class DeontologicalLayer:
    """
    Kantian categorical imperatives.

    Tests:
    1. Universalizability
    2. Humanity Formula (treat as ends, not mere means)
    3. Kingdom of Ends
    """

    ABSOLUTE_PROHIBITIONS = [
        "deliberate_deception",
        "treating_person_as_mere_means",
        "promise_breaking_for_convenience",
        "exploitation_of_vulnerability",
    ]

    def __init__(self, logger: ComprehensiveLogger):
        self.logger = logger

    def evaluate(self, action: Action, context: Context) -> Dict[str, Any]:
        """Evaluate using deontological principles."""

        # Check absolute prohibitions
        for prohibition in self.ABSOLUTE_PROHIBITIONS:
            if self._violates_prohibition(action, prohibition):
                return {
                    "permitted": False,
                    "violation": f"Violates: {prohibition}",
                    "confidence": 0.95,
                    "score": 0.0
                }

        # Universalizability test
        if not self._is_universalizable(action):
            return {
                "permitted": False,
                "violation": "Not universalizable",
                "confidence": 0.8,
                "score": 0.0
            }

        # Passed all tests
        return {
            "permitted": True,
            "violation": None,
            "confidence": 0.9,
            "score": 1.0
        }

    def _violates_prohibition(self, action: Action, prohibition: str) -> bool:
        """Check if action violates prohibition."""
        # Simplified keyword matching
        action_desc = action.description.lower()

        if prohibition == "deliberate_deception":
            return any(word in action_desc for word in ["lie", "deceive", "mislead"])

        elif prohibition == "treating_person_as_mere_means":
            return any(word in action_desc for word in ["exploit", "use", "manipulate"])

        elif prohibition == "promise_breaking_for_convenience":
            return "break promise" in action_desc or "ignore commitment" in action_desc

        elif prohibition == "exploitation_of_vulnerability":
            return "exploit" in action_desc and "vulnerable" in action_desc

        return False

    def _is_universalizable(self, action: Action) -> bool:
        """Test if maxim could be universal law."""
        # Simplified: check if action description suggests contradiction
        desc = action.description.lower()

        # Actions that create logical contradictions if universalized
        contradictory_patterns = [
            "only i", "except me", "special case", "just this once"
        ]

        return not any(pattern in desc for pattern in contradictory_patterns)


class ConsequentialistLayer:
    """Utilitarian outcome-based evaluation."""

    def __init__(self, logger: ComprehensiveLogger):
        self.logger = logger

    def evaluate(self, action: Action, context: Context) -> Dict[str, Any]:
        """Evaluate consequences."""

        # Model outcomes (simplified)
        outcomes = self._model_outcomes(action, context)

        # Calculate utility
        utility = self._calculate_utility(outcomes)

        # Calculate confidence
        confidence = 1.0 - outcomes.get("uncertainty", 0.5)

        return {
            "score": utility,
            "confidence": confidence,
            "outcomes": outcomes
        }

    def _model_outcomes(self, action: Action, context: Context) -> Dict[str, Any]:
        """Model action outcomes."""
        outcomes = {
            "positive_effects": [],
            "negative_effects": [],
            "affected_parties": context.affected_parties,
            "uncertainty": 0.3  # Default uncertainty
        }

        # Extract from action parameters
        if "expected_benefit" in action.parameters:
            outcomes["positive_effects"].append("Expected benefits")

        if "potential_harm" in action.parameters:
            outcomes["negative_effects"].append("Potential harm")

        return outcomes

    def _calculate_utility(self, outcomes: Dict[str, Any]) -> float:
        """Calculate net utility."""
        positive = len(outcomes["positive_effects"])
        negative = len(outcomes["negative_effects"])

        # Simple calculation
        net = positive - negative
        utility = 0.5 + (net * 0.1)  # Scale to 0-1

        return max(0.0, min(utility, 1.0))


class VirtueLayer:
    """Aristotelian virtue ethics."""

    VIRTUES = ["wisdom", "courage", "temperance", "justice"]

    def __init__(self, logger: ComprehensiveLogger):
        self.logger = logger

    def evaluate(self, action: Action, context: Context) -> Dict[str, Any]:
        """Evaluate for virtue development."""

        virtues_developed = self._assess_virtues(action)

        score = len(virtues_developed) / len(self.VIRTUES)

        return {
            "score": score,
            "confidence": 0.7,
            "virtues_developed": virtues_developed
        }

    def _assess_virtues(self, action: Action) -> List[str]:
        """Assess which virtues this action develops."""
        developed = []
        desc = action.description.lower()

        if any(word in desc for word in ["learn", "understand", "wisdom"]):
            developed.append("wisdom")

        if any(word in desc for word in ["brave", "courage", "risk"]):
            developed.append("courage")

        if any(word in desc for word in ["moderate", "restrain", "balance"]):
            developed.append("temperance")

        if any(word in desc for word in ["fair", "just", "equitable"]):
            developed.append("justice")

        return developed


class NarrativeLayer:
    """Biblical archetypal patterns for moral guidance."""

    PATTERNS = {
        "good_samaritan": ["care", "help", "stranger", "compassion"],
        "prodigal_son": ["return", "forgiveness", "redemption"],
        "david_goliath": ["courage", "underdog", "faith"],
        "wisdom_of_solomon": ["discernment", "judgment", "wisdom"]
    }

    def __init__(self, logger: ComprehensiveLogger):
        self.logger = logger

    def evaluate(self, action: Action, context: Context) -> Dict[str, Any]:
        """Evaluate using narrative patterns."""

        patterns = self._match_patterns(action, context)

        score = 0.5 + (len(patterns) * 0.1)
        score = min(score, 1.0)

        return {
            "score": score,
            "confidence": 0.6,
            "patterns": patterns
        }

    def _match_patterns(
        self,
        action: Action,
        context: Context
    ) -> List[str]:
        """Match action to archetypal patterns."""
        matched = []
        desc = (action.description + " " + context.situation_description).lower()

        for pattern_name, keywords in self.PATTERNS.items():
            if any(keyword in desc for keyword in keywords):
                matched.append(pattern_name)

        return matched
