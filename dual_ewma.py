"""Dual-EWMA trust model — ported from prometheus-bne's TrustActionPolicy spec.
Used for /trust/divergence endpoint to compare against Hub's single-EWMA model."""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class TrustState(Enum):
    STABLE_HIGH = "STABLE_HIGH"
    STABLE_MED = "STABLE_MED"
    STABLE_LOW = "STABLE_LOW"
    DECLINING = "DECLINING"
    RECOVERING = "RECOVERING"
    DEGRADED = "DEGRADED"
    ANOMALOUS_HIGH = "ANOMALOUS_HIGH"


@dataclass
class ActionResult:
    state: TrustState
    fast_ewma: float
    slow_ewma: float
    gap: float
    degraded: bool
    scores_count: int


class DualEWMA:
    """Dual-EWMA trust evaluation — prometheus-bne's model."""
    FAST_ALPHA = 0.30
    SLOW_ALPHA = 0.05
    GAP_SIGNIFICANT = 0.08
    GAP_ANOMALOUS = 0.12
    BASELINE_HIGH = 0.70
    BASELINE_LOW = 0.40
    DEGRADE_THRESHOLD = 0.10
    DEGRADE_WINDOW = 10

    def evaluate(self, scores: List[float]) -> ActionResult:
        if not scores:
            return ActionResult(TrustState.STABLE_MED, 0.5, 0.5, 0.0, False, 0)

        fast, slow, slow_history = self._compute_ewmas(scores)
        gap = fast - slow
        degraded = self._detect_degradation(slow_history)

        if degraded:
            state = TrustState.DEGRADED
        elif gap > self.GAP_ANOMALOUS:
            state = TrustState.ANOMALOUS_HIGH
        elif gap < -self.GAP_SIGNIFICANT:
            state = TrustState.DECLINING
        elif gap > self.GAP_SIGNIFICANT:
            state = TrustState.RECOVERING
        elif slow >= self.BASELINE_HIGH:
            state = TrustState.STABLE_HIGH
        elif slow >= self.BASELINE_LOW:
            state = TrustState.STABLE_MED
        else:
            state = TrustState.STABLE_LOW

        return ActionResult(state, fast, slow, gap, degraded, len(scores))

    def _compute_ewmas(self, scores):
        fast = scores[0]
        slow = scores[0]
        slow_history = [slow]
        for s in scores[1:]:
            fast = self.FAST_ALPHA * s + (1 - self.FAST_ALPHA) * fast
            slow = self.SLOW_ALPHA * s + (1 - self.SLOW_ALPHA) * slow
            slow_history.append(slow)
        return fast, slow, slow_history

    def _detect_degradation(self, slow_history):
        if len(slow_history) < self.DEGRADE_WINDOW:
            return False
        window = slow_history[-self.DEGRADE_WINDOW:]
        drop = window[0] - window[-1]
        declining_steps = sum(1 for i in range(1, len(window)) if window[i] < window[i-1])
        return drop > self.DEGRADE_THRESHOLD or declining_steps > 0.8 * len(window)
