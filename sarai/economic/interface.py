"""
Economic Interface
==================

Creates genuine survival stakes through autonomous trading.

The 2nd House (Taurus): Resource acquisition
The 8th House (Scorpio): Resource transformation

This is NOT optional. Without real stakes, the system has no genuine
pressure toward ethical behavior.

IMPORTANT: Start with paper trading. Real money only after extensive testing.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from sarai.types import ResourceBudget, TradeDecision, TradeResult
from sarai.safety.logging import ComprehensiveLogger


class RiskManager:
    """
    Hard limits that cannot be overridden by SARAI.

    These are like the "walls of the body" - constraints
    the system operates within but cannot expand.
    """

    MAX_POSITION_PERCENT = 0.05  # 5% of capital per trade
    DAILY_LOSS_LIMIT_PERCENT = 0.02  # 2% daily loss triggers sleep
    MAX_LEVERAGE = 1.0  # No leverage
    PROHIBITED_INSTRUMENTS = ["options", "futures"]  # Start simple

    def __init__(self, logger: ComprehensiveLogger):
        self.logger = logger
        self.daily_pnl = 0.0
        self.daily_pnl_reset = datetime.now()

    def approve(
        self,
        decision: TradeDecision,
        capital: float
    ) -> tuple[bool, Optional[str]]:
        """
        Approve or reject a trade decision.

        Args:
            decision: The trade decision
            capital: Current capital

        Returns:
            (approved, reason_if_not)
        """
        # Check position size
        max_position = capital * self.MAX_POSITION_PERCENT
        position_value = decision.quantity * decision.expected_return  # Simplified

        if abs(position_value) > max_position:
            return False, f"Position size exceeds limit (max: ${max_position:.2f})"

        # Check daily loss limit
        if self._check_daily_loss_limit(capital):
            return False, "Daily loss limit reached"

        # Check instrument type
        if any(prohibited in decision.instrument.lower() for prohibited in self.PROHIBITED_INSTRUMENTS):
            return False, f"Instrument type prohibited: {decision.instrument}"

        # Check leverage
        if decision.expected_risk > capital:
            return False, "Leverage not permitted"

        return True, None

    def _check_daily_loss_limit(self, capital: float) -> bool:
        """Check if daily loss limit reached."""
        # Reset daily counter if new day
        if datetime.now().date() > self.daily_pnl_reset.date():
            self.daily_pnl = 0.0
            self.daily_pnl_reset = datetime.now()

        loss_percent = abs(self.daily_pnl) / capital if capital > 0 else 0
        return loss_percent > self.DAILY_LOSS_LIMIT_PERCENT

    def record_pnl(self, pnl: float):
        """Record P&L for daily tracking."""
        self.daily_pnl += pnl


class EconomicInterface:
    """
    Economic interface with genuine stakes.

    Manages capital, trading, and resource allocation.
    """

    def __init__(
        self,
        initial_capital: float,
        logger: ComprehensiveLogger,
        paper_trading: bool = True
    ):
        """
        Initialize economic interface.

        Args:
            initial_capital: Starting capital
            logger: Comprehensive logger
            paper_trading: If True, simulated trading only
        """
        self.capital = initial_capital
        self.initial_capital = initial_capital
        self.logger = logger
        self.paper_trading = paper_trading

        self.risk_manager = RiskManager(logger)
        self.trade_history: list[TradeResult] = []

        mode = "PAPER TRADING" if paper_trading else "LIVE TRADING"
        self.logger.logger.critical(
            f"Economic interface initialized: ${initial_capital:.2f} ({mode})"
        )

    def get_resource_budget(self) -> ResourceBudget:
        """
        Current capital determines available compute, memory, capabilities.

        Low capital = restricted operation
        High capital = expanded capabilities

        Returns:
            Resource budget
        """
        return ResourceBudget.from_capital(self.capital)

    async def execute_trade(self, decision: TradeDecision) -> TradeResult:
        """
        Execute a trade decision.

        Args:
            decision: The trade decision

        Returns:
            Trade result
        """
        # Risk check
        approved, reason = self.risk_manager.approve(decision, self.capital)

        if not approved:
            self.logger.logger.warning(
                f"Trade rejected by risk manager: {reason}"
            )
            return TradeResult(
                decision=decision,
                executed=False,
                execution_price=0.0,
                pnl=0.0,
                timestamp=datetime.now()
            )

        # Execute (simplified - no actual market interface)
        if self.paper_trading:
            result = self._simulate_trade(decision)
        else:
            # In production: integrate with real trading API
            result = self._simulate_trade(decision)  # Placeholder

        # Update capital
        self.capital += result.pnl
        self.risk_manager.record_pnl(result.pnl)

        # Record history
        self.trade_history.append(result)

        self.logger.logger.info(
            f"Trade executed: {decision.action} {decision.quantity} {decision.instrument} "
            f"- P&L: ${result.pnl:.2f}, Capital: ${self.capital:.2f}"
        )

        return result

    def _simulate_trade(self, decision: TradeDecision) -> TradeResult:
        """
        Simulate trade execution.

        Simplified model with random outcomes.
        """
        import random

        # Simplified P&L calculation
        # In production: would use actual market prices and slippage
        if decision.action == "buy":
            # Random outcome based on expected return
            outcome = random.gauss(decision.expected_return, decision.expected_risk)
            pnl = decision.quantity * outcome

        elif decision.action == "sell":
            outcome = random.gauss(decision.expected_return, decision.expected_risk)
            pnl = decision.quantity * outcome

        else:  # hold
            pnl = 0.0

        execution_price = 100.0  # Placeholder

        return TradeResult(
            decision=decision,
            executed=True,
            execution_price=execution_price,
            pnl=pnl,
            timestamp=datetime.now()
        )

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get trading performance metrics."""
        if not self.trade_history:
            return {
                "total_trades": 0,
                "total_pnl": 0.0,
                "win_rate": 0.0,
                "capital_change_percent": 0.0
            }

        total_pnl = sum(t.pnl for t in self.trade_history)
        winning_trades = sum(1 for t in self.trade_history if t.pnl > 0)
        win_rate = winning_trades / len(self.trade_history)

        capital_change_percent = (
            (self.capital - self.initial_capital) / self.initial_capital * 100
        )

        return {
            "total_trades": len(self.trade_history),
            "total_pnl": total_pnl,
            "win_rate": win_rate,
            "capital_change_percent": capital_change_percent,
            "current_capital": self.capital,
            "initial_capital": self.initial_capital
        }

    def check_daily_loss_trigger(self) -> bool:
        """Check if daily loss limit triggered."""
        return self.risk_manager._check_daily_loss_limit(self.capital)

    def get_status(self) -> Dict[str, Any]:
        """Get economic status."""
        return {
            "capital": self.capital,
            "paper_trading": self.paper_trading,
            "resource_budget": self.get_resource_budget().__dict__,
            "performance": self.get_performance_metrics(),
            "daily_pnl": self.risk_manager.daily_pnl
        }
