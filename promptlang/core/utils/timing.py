"""Timing utilities for stage profiling."""

import time
from contextlib import contextmanager
from typing import Dict, Optional


class TimingContext:
    """Context manager for tracking stage timings."""

    def __init__(self):
        self.timings: Dict[str, float] = {}
        self._start_times: Dict[str, float] = {}

    def start(self, stage: str) -> None:
        """Start timing a stage."""
        self._start_times[stage] = time.perf_counter()

    def stop(self, stage: str) -> float:
        """Stop timing a stage and return elapsed milliseconds."""
        if stage not in self._start_times:
            return 0.0
        elapsed = time.perf_counter() - self._start_times[stage]
        elapsed_ms = elapsed * 1000
        self.timings[stage] = elapsed_ms
        del self._start_times[stage]
        return elapsed_ms

    @contextmanager
    def stage(self, stage_name: str):
        """Context manager for timing a stage."""
        self.start(stage_name)
        try:
            yield
        finally:
            self.stop(stage_name)

    def get_timings(self) -> Dict[str, float]:
        """Get all recorded timings."""
        return self.timings.copy()


def current_timestamp_ms() -> int:
    """Get current timestamp in milliseconds."""
    return int(time.time() * 1000)
