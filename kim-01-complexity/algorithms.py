from __future__ import annotations

from typing import Sequence


def array_sum(arr: Sequence[int]) -> int:
    total = 0
    for x in arr:
        total += x
    return total


def array_max(arr: Sequence[int]) -> int:
    if not arr:
        raise ValueError("array_max() arg is an empty sequence")
    m = arr[0]
    for x in arr:
        if x > m:
            m = x
    return m


def count_equal_pairs(arr: Sequence[int]) -> int:
    n = len(arr)
    count = 0
    for i in range(n):
        ai = arr[i]
        for j in range(i + 1, n):
            if ai == arr[j]:
                count += 1
    return count


def binpow(a: int, b: int, mod: int | None = None) -> int:
    if b < 0:
        raise ValueError("negative exponent not supported")
    result = 1
    if mod is not None:
        a %= mod
    while b > 0:
        if b & 1:
            result = result * a
            if mod is not None:
                result %= mod
        a = a * a
        if mod is not None:
            a %= mod
        b >>= 1
    return result