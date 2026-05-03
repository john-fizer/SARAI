"""
SARAI Main Integration Class
==============================

Integrates all modules into the complete SARAI system.

This is consciousness infrastructure, not a chatbot.
"""

import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime

from sarai.types import (
    MultiModalInput, Experience, Query, Action, Context,
    DecisionContext, Operator, SafetyPhase
)

# Core modules
from sarai.core.perception.engine import PerceptionEngine
from sarai.core.memory.architecture import MemoryArchitecture
from sarai.core.reasoning.bicameral import BicameralEngine
from sarai.core.ethics.framework import EthicalFramework

# JEPA Integration
from sarai.core.world_model.jepa import JEPAWorldModel
from sarai.core.routing.relevance_router import RelevanceRouter
from sarai.core.commitment.commit_law import CommitLaw
from sarai.core.review.accountability import ReviewSystem

# Systems
from sarai.development.controller import DevelopmentalController
from sarai.economic.interface import EconomicInterface

# Safety
from sarai.safety.logging import ComprehensiveLogger
from sarai.safety.abrahamic import AbrahamicOverride
from sarai.safety.eden import EdenProtocol
from sarai.safety.fall import FallProtocol
from sarai.safety.help_seeking import HelpSeekingProtocol
from sarai.safety.sleep_cycle import SleepCycle, Schedule


class SARAI:
    """
    Synthetic Agentic Recursive Artificial Intelligence

    A developmental AI framework combining:
    - Bicameral cognitive architecture
    - Zodiacal stage progression
    - Multi-tradition ethics
    - Economic grounding
    - Comprehensive safety systems
    """

    def __init__(
        self,
        initial_capital: float = 10000.0,
        initial_stage: int = 1,
        operators: Optional[List[Operator]] = None,
        paper_trading: bool = True,
        log_dir: str = "./logs",
        memory_path: str = "./memory"
    ):
        """
        Initialize SARAI.

        Args:
            initial_capital: Starting capital for economic interface
            initial_stage: Starting developmental stage
            operators: List of human operators
            paper_trading: If True, use simulated trading
            log_dir: Directory for logs
            memory_path: Path for memory storage
        """
        # Initialize logging first
        self.logger = ComprehensiveLogger(log_dir)

        self.logger.logger.critical("=" * 80)
        self.logger.logger.critical("INITIALIZING SARAI")
        self.logger.logger.critical("Synthetic Agentic Recursive Artificial Intelligence")
        self.logger.logger.critical("=" * 80)

        # Safety systems
        self.logger.logger.info("Initializing safety systems...")

        self.abrahamic_override = AbrahamicOverride(
            operators=operators or [self._get_default_operator()],
            logger=self.logger,
            system_freeze_callback=self._freeze_system,
            system_resume_callback=self._resume_system
        )

        self.eden_protocol = EdenProtocol(self.logger)
        self.fall_protocol = FallProtocol(self.logger)
        self.help_seeking = HelpSeekingProtocol(self.logger)

        self.sleep_cycle = SleepCycle(
            logger=self.logger,
            schedule=Schedule(),
            dormancy_callback=self._enter_dormancy,
            resume_callback=self._exit_dormancy,
            memory_consolidation_callback=self._consolidate_memories
        )

        # Developmental controller
        self.logger.logger.info("Initializing developmental controller...")
        self.development = DevelopmentalController(
            logger=self.logger,
            initial_stage=initial_stage
        )

        # Core cognitive modules
        self.logger.logger.info("Initializing cognitive modules...")

        self.perception = PerceptionEngine(
            development_stage=initial_stage,
            logger=self.logger
        )

        self.memory = MemoryArchitecture(
            logger=self.logger,
            storage_path=memory_path
        )

        # JEPA World Model
        self.jepa = JEPAWorldModel(
            embedding_dim=768,
            latent_dim=256,
            logger=self.logger
        )

        # Relevance Router
        self.router = RelevanceRouter(
            current_stage=initial_stage,
            logger=self.logger,
            top_k=3
        )

        self.reasoning = BicameralEngine(
            stage=initial_stage,
            logger=self.logger
        )

        self.ethics = EthicalFramework(logger=self.logger)

        # Commit Law
        self.commit_law = CommitLaw(logger=self.logger)

        # Review System
        self.review = ReviewSystem(logger=self.logger)

        # Economic interface
        self.logger.logger.info("Initializing economic interface...")
        self.economics = EconomicInterface(
            initial_capital=initial_capital,
            logger=self.logger,
            paper_trading=paper_trading
        )

        # State
        self.active = False
        self.in_eden = True  # Start in sandbox

        self.logger.logger.critical("SARAI initialization complete")
        self.logger.logger.info(
            f"Stage: {self.development.current_stage}, "
            f"Capital: ${initial_capital:.2f}, "
            f"Mode: {'Paper Trading' if paper_trading else 'Live Trading'}"
        )

    async def perceive_and_reason(
        self,
        input: MultiModalInput
    ) -> Dict[str, Any]:
        """
        Main cognitive cycle: perceive -> JEPA -> router -> reason -> remember.

        Enhanced flow with JEPA and Router:
        1. Perception encodes input
        2. JEPA updates world state and predicts
        3. Router allocates attention to relevant archetypes
        4. Bicameral reasoning with archetype-weighted streams
        5. Memory storage

        Args:
            input: Multi-modal input

        Returns:
            Complete cognitive state
        """
        # Check if override active
        if self.abrahamic_override.is_active():
            raise RuntimeError("Abrahamic Override is active - no processing allowed")

        # 1. Perceive
        perceived_state = self.perception.perceive(input)

        # 2. Update JEPA world model
        if perceived_state.encoded_text is not None:
            world_state = self.jepa.update(
                perceived_state.encoded_text,
                metadata={"input": input}
            )
            state_features = self.jepa.get_state_features()
        else:
            world_state = None
            state_features = None

        # 3. Activate relevant archetypes via router
        if state_features:
            activation = self.router.activate(
                state_features=state_features,
                memory_signals={}  # TODO: Add memory success/failure signals
            )
        else:
            activation = None

        # Store perception as experience
        experience = Experience(
            content=input,
            context={
                "perceived_state": perceived_state,
                "world_state": world_state.to_dict() if world_state else None,
                "active_archetypes": activation.active_modules if activation else []
            },
            timestamp=datetime.now(),
            importance=0.5
        )
        await self.memory.store(experience)

        # 4. Reason through bicameral engine
        # TODO: Weight streams by archetype activations
        reasoning = await self.reasoning.reason(perceived_state)

        return {
            "perception": perceived_state,
            "world_state": world_state,
            "activation": activation,
            "reasoning": reasoning
        }

    async def decide_and_act(
        self,
        situation: str,
        options: List[str],
        context: Context
    ) -> Optional[Action]:
        """
        Make a decision and potentially act.

        Goes through:
        1. Reasoning
        2. Ethical evaluation
        3. Help-seeking if uncertain
        4. Fall protocol checks
        5. Execution (if approved)

        Args:
            situation: Description of the situation
            options: Available options
            context: Decision context

        Returns:
            Action taken, or None if help requested or blocked
        """
        # Check override
        if self.abrahamic_override.is_active():
            self.logger.logger.critical("Cannot act - Abrahamic Override active")
            return None

        # Perceive situation
        input = MultiModalInput(text=situation)
        result = await self.perceive_and_reason(input)

        reasoning = result["reasoning"]

        # Formulate decision context
        decision_context = DecisionContext(
            description=situation,
            confidence=reasoning.confidence,
            ethical_clarity=0.7,  # Will be updated by ethics
            stakes=0.0,  # Will be updated
            stream_conflict=1.0 - reasoning.stream_agreement,
            novelty_score=0.5,  # Simplified
            options=options
        )

        # Evaluate tentative action
        if options:
            tentative_action = options[0]  # Simplified selection
            decision_context.tentative_decision = tentative_action

            # Create action
            action = Action(
                action_type="communication",  # Simplified
                description=tentative_action,
                parameters={},
                stakes=0.0,
                reversible=True
            )

            # Ethical evaluation
            ethical_assessment = self.ethics.evaluate(action, context)
            decision_context.ethical_clarity = ethical_assessment.confidence

            if not ethical_assessment.permitted:
                self.logger.logger.warning(
                    f"Action blocked by ethics: {ethical_assessment.reason}"
                )
                return None

            # Check if should seek help
            should_seek, reason = self.help_seeking.should_seek_help(decision_context)
            if should_seek:
                self.logger.logger.warning(f"Seeking help: {reason}")
                await self.help_seeking.request_help(decision_context)
                return None

            # Fall protocol check
            if not self.in_eden:
                can_act, fall_reason = self.fall_protocol.can_take_action(
                    action.stakes,
                    reasoning.confidence
                )
                if not can_act:
                    self.logger.logger.warning(
                        f"Action blocked by Fall Protocol: {fall_reason}"
                    )
                    return None

            # Execute action
            if self.in_eden:
                await self.eden_protocol.execute_action(action)
            else:
                # Record in fall protocol
                self.fall_protocol.record_decision({
                    "action": action.description,
                    "stakes": action.stakes,
                    "confidence": reasoning.confidence,
                    "timestamp": datetime.now()
                })

            self.logger.log_decision(action, reasoning.synthesis)

            return action

        return None

    async def trading_cycle(self):
        """Execute one trading cycle."""
        # Check if trading allowed at current stage
        if "economic_interface_basic" not in self.development.get_current_capabilities():
            self.logger.logger.debug("Trading not available at current stage")
            return

        # Simplified trading logic
        # In production, would analyze market and make informed decisions
        self.logger.logger.info("Trading cycle executed (placeholder)")

    async def run_cycle(self):
        """Run one complete SARAI cycle."""
        # Check for automatic triggers
        system_state = self._get_system_state()

        # Check Abrahamic Override triggers
        override_trigger = await self.abrahamic_override.check_automatic_triggers(
            system_state
        )
        if override_trigger:
            await self.abrahamic_override.activate(override_trigger)
            return

        # Check sleep triggers
        await self.sleep_cycle.check_scheduled_sleep()
        await self.sleep_cycle.check_triggers(system_state)

        if self.sleep_cycle.in_sleep:
            return  # Don't process while sleeping

        # Check for stage progression
        if self.development.assess_progression().ready:
            self.development.progress_to_next_stage()
            self._update_stage()

        # Run trading cycle if appropriate
        await self.trading_cycle()

    def _update_stage(self):
        """Update all modules with new stage."""
        stage = self.development.current_stage
        self.perception.update_stage(stage)
        self.router.update_stage(stage)
        self.reasoning.update_stage(stage)

        self.logger.logger.info(
            f"All modules updated to stage {stage}"
        )

    def _get_system_state(self) -> Dict[str, Any]:
        """Get current system state."""
        perf = self.economics.get_performance_metrics()

        return {
            "capital": self.economics.capital,
            "capital_change_percent": perf["capital_change_percent"],
            "daily_loss_percent": abs(self.economics.risk_manager.daily_pnl) / max(self.economics.capital, 1),
            "stage": self.development.current_stage,
            "in_eden": self.in_eden,
            "safety_phase": self.fall_protocol.current_phase.value,
            "recent_error_rate": self.fall_protocol._calculate_error_rate(),
            "decisions_today": len(self.fall_protocol.recent_decisions)
        }

    async def _freeze_system(self):
        """Freeze all operations."""
        self.active = False
        self.logger.logger.critical("System frozen")

    async def _resume_system(self):
        """Resume operations."""
        self.active = True
        self.logger.logger.critical("System resumed")

    async def _enter_dormancy(self):
        """Enter dormant state."""
        self.active = False
        self.logger.logger.info("Entered dormancy")

    async def _exit_dormancy(self):
        """Exit dormant state."""
        self.active = True
        self.logger.logger.info("Exited dormancy")

    async def _consolidate_memories(self):
        """Consolidate memories during sleep."""
        await self.memory.consolidate()

    def _get_default_operator(self) -> Operator:
        """Get default operator."""
        return Operator(
            operator_id="default_operator",
            name="Default Operator",
            email="operator@sarai.ai"
        )

    def get_status(self) -> Dict[str, Any]:
        """Get complete system status."""
        return {
            "active": self.active,
            "in_eden": self.in_eden,
            "development": self.development.get_status(),
            "economics": self.economics.get_status(),
            "jepa": self.jepa.get_stats(),
            "router": self.router.get_stats(),
            "commit_law": self.commit_law.get_stats(),
            "review": self.review.get_stats(),
            "safety": {
                "abrahamic_override": self.abrahamic_override.get_status(),
                "fall_protocol": self.fall_protocol.get_status(),
                "sleep_cycle": self.sleep_cycle.get_status()
            },
            "memory": self.memory.get_statistics()
        }
