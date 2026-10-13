from __future__ import annotations

import random

SEED_BASE = 30

SIZES: tuple[int, ...] = (1_000, 3_162, 10_000, 31_623)
KINDS: tuple[str, ...] = ("random", "sorted", "reversed", "equal")


def make_array(kind: str, n: int, seed: int) -> list[int]:
    rnd = random.Random(seed)
    if kind == "random":
        return [rnd.randrange(0, 10**6) for _ in range(n)]
    if kind == "sorted":
        return list(range(n))
    if kind == "reversed":
        return list(range(n, 0, -1))
    if kind == "equal":
        return [rnd.randrange(0, 10**6)] * n
    raise ValueError(f"unknown kind: {kind}")


def make_all(variant: int) -> dict[str, dict[int, list[int]]]:
    seed = SEED_BASE + variant
    return {
        kind: {n: make_array(kind, n, seed + i) for i, n in enumerate(SIZES)}
        for kind in KINDS
    }
