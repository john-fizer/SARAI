"""
Practical SARAI Integration: Personal Decision Advisor
=======================================================

A real-world example showing SARAI as an AI decision advisor that:
- Helps users make complex decisions
- Learns from outcomes
- Builds trust over time
- Provides accountable recommendations

Author: John Fizer
"""

import sys
sys.path.append('..')

import asyncio
import numpy as np
from datetime import datetime
from typing import Dict, Any, List

from sarai.core.world_model.jepa import JEPAWorldModel
from sarai.core.routing.relevance_router import RelevanceRouter
from sarai.core.commitment.commit_law import CommitLaw
from sarai.core.review.accountability import ReviewSystem
from sarai.types import Action, ActionType, EthicalAssessment, ReasoningOutput, AISResult, ARSResult
from sarai.safety.logging import ComprehensiveLogger


class PersonalDecisionAdvisor:
    """
    AI Decision Advisor powered by SARAI's cognitive architecture.

    Helps users make decisions, tracks predictions, and learns from outcomes.
    """

    def __init__(self):
        """Initialize the advisor with SARAI components."""
        self.logger = ComprehensiveLogger("./advisor_logs")

        # SARAI core components
        self.jepa = JEPAWorldModel(
            embedding_dim=768,
            latent_dim=256,
            logger=self.logger
        )

        self.router = RelevanceRouter(
            current_stage=6,  # Start at Analysis stage
            logger=self.logger,
            top_k=3
        )

        self.commit_law = CommitLaw(self.logger)
        self.review_system = ReviewSystem(self.logger)

        # Track conversation history
        self.conversation_history = []
        self.session_stats = {
            'decisions_made': 0,
            'predictions_correct': 0,
            'user_satisfaction': []
        }

    async def advise(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process user's decision request and provide advice.

        Args:
            user_input: User's question or decision scenario
            context: Additional context (stakes, urgency, etc.)

        Returns:
            Dict with advice, reasoning, and prediction
        """
        print(f"\n{'='*80}")
        print(f"USER REQUEST:")
        print(f"{'='*80}")
        print(f"{user_input}\n")

        # Default context
        if context is None:
            context = {}

        # 1. ENCODE INPUT (simulate perception)
        # In real system, this would use actual embedding model
        observation = self._encode_text(user_input)

        # 2. UPDATE JEPA WORLD MODEL
        world_state = self.jepa.update(
            observation,
            metadata={'user_input': user_input[:100], 'timestamp': datetime.now()}
        )

        state_features = self.jepa.get_state_features()

        # Override with explicit context if provided
        if 'urgency' in context:
            state_features.time_pressure = context['urgency']
        if 'stakes' in context:
            state_features.stakes = context['stakes']
        if 'reversible' in context:
            state_features.irreversibility = 0.0 if context['reversible'] else 0.8

        print(f"🧠 WORLD MODEL STATE:")
        print(f"   Uncertainty: {state_features.uncertainty:.2f}")
        print(f"   Novelty: {state_features.novelty:.2f}")
        print(f"   Complexity: {state_features.complexity:.2f}")
        print(f"   Stakes: {state_features.stakes:.2f}\n")

        # 3. ROUTE ATTENTION
        activation = self.router.activate(state_features)

        print(f"🎯 COGNITIVE ACTIVATION:")
        print(f"   Active archetypes: {', '.join(activation.active_modules)}")
        print(f"   {activation.reasoning}\n")

        # 4. GENERATE REASONING (mock - in real system, use actual LLM)
        reasoning = self._generate_reasoning(
            user_input,
            activation.active_modules,
            state_features
        )

        print(f"💭 REASONING:")
        print(f"   {reasoning['synthesis']}\n")

        # 5. GENERATE ADVICE
        advice = self._generate_advice(
            user_input,
            reasoning,
            activation.active_modules
        )

        print(f"💡 ADVICE:")
        print(f"{advice['recommendation']}\n")

        if advice['alternatives']:
            print(f"📋 ALTERNATIVES:")
            for i, alt in enumerate(advice['alternatives'], 1):
                print(f"   {i}. {alt}")
            print()

        # 6. MAKE PREDICTION
        prediction = self._predict_outcome(advice, state_features)

        print(f"🔮 PREDICTION:")
        print(f"   {prediction['outcome']}")
        print(f"   Confidence: {prediction['confidence']:.0%}\n")

        # 7. ETHICAL CHECK
        ethical = self._assess_ethics(advice)

        print(f"✅ ETHICAL ASSESSMENT:")
        print(f"   Permitted: {'Yes' if ethical.permitted else 'No'}")
        print(f"   {ethical.reason}\n")

        # 8. COMMIT TO PREDICTION
        action = Action(
            action_type=ActionType.COMMUNICATION,
            description=f"Advise: {advice['recommendation'][:100]}",
            parameters={
                'advice': advice,
                'prediction': prediction
            },
            stakes=state_features.stakes * 100,
            reversible=True
        )

        self.commit_law.enter_exploration({'scenario': user_input[:100]})

        reasoning_output = ReasoningOutput(
            ais_result=AISResult(
                patterns_recognized=activation.active_modules,
                symbolic_interpretation=reasoning['ais_interpretation'],
                holistic_assessment=reasoning['synthesis'],
                confidence=reasoning['confidence'],
                processing_time=0.1
            ),
            ars_result=ARSResult(
                logical_chain=reasoning['logical_steps'],
                causal_model={'chosen': advice['recommendation']},
                quantitative_analysis={'confidence': prediction['confidence']},
                confidence=reasoning['confidence'],
                processing_time=0.1
            ),
            synthesis=reasoning['synthesis'],
            confidence=reasoning['confidence'],
            stream_agreement=0.85,
            conflicts=[],
            timestamp=datetime.now()
        )

        self.commit_law.begin_evaluation(reasoning_output, {'advice': prediction['confidence']})

        commit = self.commit_law.decide(
            action=action,
            ethical_assessment=ethical,
            predicted_outcome=prediction['outcome'],
            jepa_prediction_error=world_state.prediction_error or 0.2
        )

        print(f"📝 COMMITMENT CREATED:")
        print(f"   ID: {commit.commit_id}")
        print(f"   Hash: {commit._hash[:16]}...\n")

        # Store for later review
        self.conversation_history.append({
            'user_input': user_input,
            'advice': advice,
            'prediction': prediction,
            'commit': commit,
            'active_archetypes': activation.active_modules,
            'timestamp': datetime.now()
        })

        self.session_stats['decisions_made'] += 1

        return {
            'advice': advice,
            'prediction': prediction,
            'commit_id': commit.commit_id,
            'active_archetypes': activation.active_modules,
            'confidence': prediction['confidence']
        }

    async def provide_feedback(self, commit_id: str, outcome: str, satisfaction: int):
        """
        User provides feedback on how the advice worked out.

        Args:
            commit_id: ID of the commit to review
            outcome: What actually happened
            satisfaction: User satisfaction (1-5 scale)
        """
        print(f"\n{'='*80}")
        print(f"FEEDBACK RECEIVED:")
        print(f"{'='*80}\n")

        # Find the corresponding conversation
        conversation = next(
            (c for c in self.conversation_history if c['commit']['commit_id'] == commit_id),
            None
        )

        if not conversation:
            print("❌ Commit not found")
            return

        commit = conversation['commit']

        print(f"📊 ORIGINAL ADVICE:")
        print(f"   {conversation['advice']['recommendation'][:100]}...\n")

        print(f"🔮 PREDICTED:")
        print(f"   {conversation['prediction']['outcome']}\n")

        print(f"✅ ACTUAL OUTCOME:")
        print(f"   {outcome}")
        print(f"   Satisfaction: {'⭐' * satisfaction}/5\n")

        # Execute and complete
        self.commit_law.begin_execution(commit_id)
        self.commit_law.complete_execution(commit_id, outcome)

        # Review
        review_result = self.review_system.review_commit(
            commit,
            active_archetypes=conversation['active_archetypes']
        )

        matches = review_result['prediction_matches']

        print(f"🔎 REVIEW RESULT:")
        print(f"   Prediction match: {'✓ YES' if matches else '✗ NO'}")

        if review_result['contradiction_detected']:
            print(f"   ⚠️  Contradiction strength: {review_result['contradiction_strength']:.2f}")

        print(f"\n   Trust score updates:")
        for arch, score in review_result['updated_trust_scores'].items():
            delta = score - 0.5
            arrow = "↑" if delta > 0 else "↓" if delta < 0 else "→"
            print(f"     {arch:15s}: {arrow} {score:.3f}")

        print()

        # Update stats
        if matches or satisfaction >= 4:
            self.session_stats['predictions_correct'] += 1

        self.session_stats['user_satisfaction'].append(satisfaction)

        # Progress stage based on success
        if satisfaction >= 4 and self.session_stats['decisions_made'] >= 5:
            current_stage = self.router.current_stage
            if current_stage < 12:
                new_stage = min(current_stage + 1, 12)
                self.router.update_stage(new_stage)
                print(f"🌟 DEVELOPMENTAL PROGRESS: Stage {current_stage} → {new_stage}\n")

    def show_session_summary(self):
        """Display summary of the session."""
        print(f"\n{'='*80}")
        print(f"SESSION SUMMARY")
        print(f"{'='*80}\n")

        print(f"📊 DECISIONS:")
        print(f"   Total: {self.session_stats['decisions_made']}")
        print(f"   Accurate: {self.session_stats['predictions_correct']}")
        if self.session_stats['decisions_made'] > 0:
            accuracy = self.session_stats['predictions_correct'] / self.session_stats['decisions_made']
            print(f"   Accuracy: {accuracy:.1%}")
        print()

        if self.session_stats['user_satisfaction']:
            avg_sat = sum(self.session_stats['user_satisfaction']) / len(self.session_stats['user_satisfaction'])
            print(f"😊 USER SATISFACTION:")
            print(f"   Average: {avg_sat:.1f}/5 {'⭐' * int(avg_sat)}")
            print()

        # JEPA stats
        jepa_stats = self.jepa.get_stats()
        print(f"🧠 WORLD MODEL:")
        print(f"   Observations: {jepa_stats['state_history_length']}")
        print(f"   Avg prediction error: {jepa_stats['avg_prediction_error']:.3f}")
        print(f"   Avg surprise: {jepa_stats['avg_surprise']:.3f}")
        print()

        # Router stats
        router_stats = self.router.get_stats()
        print(f"🎯 COGNITIVE PATTERNS:")
        print(f"   Current stage: {router_stats['current_stage']}")
        print(f"   Most activated: {', '.join([a['name'] for a in router_stats['most_activated'][:3]])}")
        print()

        # Trust scores
        review_stats = self.review_system.get_stats()
        print(f"🏆 TOP PERFORMING ARCHETYPES:")
        sorted_trust = sorted(
            review_stats['trust_scores'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        for arch, score in sorted_trust:
            delta = score - 0.5
            bar = "█" * int(score * 30)
            arrow = "↑" if delta > 0 else "↓" if delta < 0 else "→"
            print(f"   {arch:15s}: {arrow} {bar} {score:.3f}")
        print()

    # Helper methods (mock implementations - in production, use real LLM/embeddings)

    def _encode_text(self, text: str) -> np.ndarray:
        """Encode text to embedding (mock)."""
        # In production: use actual embedding model (OpenAI, sentence-transformers, etc.)
        np.random.seed(hash(text) % 2**32)
        return np.random.randn(768).astype(np.float32)

    def _generate_reasoning(self, user_input: str, archetypes: List[str], features) -> Dict[str, Any]:
        """Generate reasoning based on active archetypes."""
        # In production: use LLM with archetype-specific prompts

        archetype_perspectives = {
            'Analysis': "detailed examination of options",
            'Structure': "systematic evaluation of long-term implications",
            'Relationship': "consideration of impact on others",
            'Value': "assessment of resource trade-offs",
            'Innovation': "exploration of creative alternatives",
            'Memory': "reflection on past similar situations",
            'Initiative': "focus on taking action",
            'Transformation': "deep investigation of root causes",
            'Meaning': "broader philosophical perspective",
            'Unity': "holistic integration of all factors"
        }

        perspectives = [archetype_perspectives.get(a, "general consideration") for a in archetypes]

        synthesis = f"After {', '.join(perspectives)}, I recommend the following approach."

        return {
            'synthesis': synthesis,
            'ais_interpretation': f"Pattern recognition suggests {archetypes[0]} approach",
            'logical_steps': ['analyze situation', 'evaluate options', 'recommend action'],
            'confidence': 0.7 + features.complexity * 0.1
        }

    def _generate_advice(self, user_input: str, reasoning: Dict, archetypes: List[str]) -> Dict[str, Any]:
        """Generate actual advice."""
        # In production: use LLM to generate personalized advice

        # Mock advice based on archetypes
        if 'Analysis' in archetypes:
            recommendation = "Create a detailed pros/cons list for each option, weighing factors objectively."
            alternatives = [
                "Use a decision matrix with weighted criteria",
                "Consult with experts in relevant areas",
                "Test the top option with a small pilot if possible"
            ]
        elif 'Structure' in archetypes:
            recommendation = "Develop a structured 3-month plan to evaluate this decision systematically."
            alternatives = [
                "Break down the decision into smaller milestones",
                "Create accountability checkpoints",
                "Build in flexibility for course correction"
            ]
        elif 'Relationship' in archetypes:
            recommendation = "Discuss this decision with stakeholders to understand all perspectives."
            alternatives = [
                "Seek feedback from those affected",
                "Consider collaborative decision-making",
                "Build consensus where possible"
            ]
        else:
            recommendation = "Take a balanced approach considering both immediate and long-term factors."
            alternatives = [
                "Sleep on it before committing",
                "Gather more information",
                "Trust your intuition if analysis is inconclusive"
            ]

        return {
            'recommendation': recommendation,
            'alternatives': alternatives,
            'reasoning': reasoning['synthesis']
        }

    def _predict_outcome(self, advice: Dict, features) -> Dict[str, Any]:
        """Predict outcome if advice is followed."""
        # In production: use outcome prediction model

        confidence = 0.65 + (1.0 - features.uncertainty) * 0.3

        outcomes = [
            "You'll feel confident in your decision within 1-2 weeks",
            "This approach will reduce decision anxiety significantly",
            "You'll have clarity on the best path forward",
            "The decision process will be more structured and less stressful",
            "You'll avoid common decision-making pitfalls"
        ]

        return {
            'outcome': np.random.choice(outcomes),
            'confidence': confidence,
            'timeframe': '1-2 weeks'
        }

    def _assess_ethics(self, advice: Dict) -> EthicalAssessment:
        """Quick ethical check."""
        # In production: use ethics module

        return EthicalAssessment(
            permitted=True,
            confidence=0.95,
            reason="Advice promotes thoughtful decision-making without harm",
            deontological_score=0.9,
            consequentialist_score=0.85,
            virtue_score=0.9,
            narrative_patterns=["wisdom", "prudence"],
            timestamp=datetime.now()
        )


async def run_demo():
    """Run a demonstration of the Personal Decision Advisor."""

    print("=" * 80)
    print("PERSONAL DECISION ADVISOR")
    print("Powered by SARAI Cognitive Architecture")
    print("=" * 80)
    print("\nThis demo shows SARAI helping a user make real decisions,")
    print("learning from outcomes, and building trust over time.\n")

    advisor = PersonalDecisionAdvisor()

    # Scenario 1: Career decision
    result1 = await advisor.advise(
        user_input="""
        I received a job offer with 30% higher salary but it requires relocating
        to a new city away from family and friends. My current job is comfortable
        but has limited growth. Should I take the new offer?
        """,
        context={
            'stakes': 0.9,  # High stakes
            'urgency': 0.6,  # Moderate urgency
            'reversible': False  # Hard to reverse
        }
    )

    input("Press Enter to provide feedback on Scenario 1...")

    # User took the job and is happy
    await advisor.provide_feedback(
        commit_id=result1['commit_id'],
        outcome="User took the job. After 2 months, very satisfied with decision despite missing family.",
        satisfaction=5
    )

    input("\nPress Enter for Scenario 2...")

    # Scenario 2: Investment decision
    result2 = await advisor.advise(
        user_input="""
        I have $10,000 to invest. Should I put it in index funds (safe but slow growth)
        or invest in a startup my friend is launching (risky but potentially high returns)?
        """,
        context={
            'stakes': 0.7,
            'urgency': 0.4,
            'reversible': True  # Can liquidate investments
        }
    )

    input("Press Enter to provide feedback on Scenario 2...")

    # User diversified (good compromise)
    await advisor.provide_feedback(
        commit_id=result2['commit_id'],
        outcome="User put $7k in index funds, $3k in startup. Feels balanced and comfortable.",
        satisfaction=4
    )

    input("\nPress Enter for Scenario 3...")

    # Scenario 3: Relationship decision
    result3 = await advisor.advise(
        user_input="""
        My partner and I are considering getting a dog, but I work long hours and
        travel occasionally for work. Is this the right time?
        """,
        context={
            'stakes': 0.6,
            'urgency': 0.2,
            'reversible': False  # Can't easily return a dog
        }
    )

    input("Press Enter to provide feedback on Scenario 3...")

    # User waited (wise choice)
    await advisor.provide_feedback(
        commit_id=result3['commit_id'],
        outcome="User decided to wait 6 months until job stabilizes. Feels it was the right call.",
        satisfaction=5
    )

    # Show summary
    advisor.show_session_summary()

    print("=" * 80)
    print("✅ DEMO COMPLETE")
    print("=" * 80)
    print("\nKey Takeaways:")
    print("• SARAI provides personalized, context-aware advice")
    print("• Every recommendation includes a prediction")
    print("• System learns from outcomes to improve")
    print("• Trust scores guide future cognitive activation")
    print("• Full accountability trail maintained\n")


if __name__ == "__main__":
    asyncio.run(run_demo())
