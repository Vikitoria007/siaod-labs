from __future__ import annotations

import gc
import time
from collections.abc import Callable
from typing import Any


def benchmark(
    func: Callable[..., Any],
    *args: Any,
    repeats: int = 5,
    warmup: int = 1,
) -> float:
    
    for _ in range(warmup):
        func(*args)

    times: list[float] = []
    for _ in range(repeats):
        gc.collect()
        gc.disable()
        t0 = time.perf_counter()
        func(*args)
        t1 = time.perf_counter()
        gc.enable()
        times.append(t1 - t0)

    times.sort()
    return times[len(times) // 2]
