import time
from contextlib import contextmanager
from dataclasses import dataclass


@dataclass
class TimingResult:
    elapsed_seconds: float = 0.0


@contextmanager
def sync_timer():
    result = TimingResult()
    start = time.perf_counter()
    try:
        yield result
    finally:
        result.elapsed_seconds = time.perf_counter() - start


class AsyncTimer:
    def __init__(self):
        self.result = TimingResult()

    async def __aenter__(self):
        self._start = time.perf_counter()
        return self.result

    async def __aexit__(self, *exc):
        self.result.elapsed_seconds = time.perf_counter() - self._start
