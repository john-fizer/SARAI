"""
Review & Accountability for SARAI
==================================

Compares predictions vs outcomes and maintains trust scores.

The accountability loop:
1. Commitment makes prediction
2. Action executes
3. Review compares predicted vs actual
4. Trust scores update
5. Contradictions trigger reopen
"""

from sarai.core.review.accountability import ReviewSystem
from sarai.core.review.metrics import ReviewMetrics, TrustScore

__all__ = ["ReviewSystem", "ReviewMetrics", "TrustScore"]
