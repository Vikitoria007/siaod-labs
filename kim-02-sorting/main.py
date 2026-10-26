from __future__ import annotations

import argparse
import random
import statistics
import sys
import time
import traceback
import matplotlib.pyplot as plt
import math


def bubble_sort(a: list) -> tuple[list, int, int]:
    a = list(a)
    n = len(a)
    comparisons = 0
    swaps = 0
    for i in range(n):
        swapped = False
        for j in range(n - i - 1):
            comparisons += 1
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swaps += 1
                swapped = True
        if not swapped:
            break
    return a, comparisons, swaps

def insertion_sort(a: list) -> tuple[list, int, int]:
    a = list(a)
    comparisons = 0
    moves = 0
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0:
            comparisons += 1
            if a[j] > key:
                a[j + 1] = a[j]
                moves += 1
                j -= 1
            else:
                break
        a[j + 1] = key
        moves += 1
    return a, comparisons, moves

def selection_sort(a: list) -> tuple[list, int, int]:
    a = list(a)
    n = len(a)
    comparisons = 0
    swaps = 0
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            comparisons += 1
            if a[j] < a[min_idx]:
                min_idx = j
        if min_idx != i:
            a[i], a[min_idx] = a[min_idx], a[i]
            swaps += 1
    return a, comparisons, swaps

def quick_sort(a: list, rng: random.Random | None = None) -> list:
    if rng is None:
        rng = random.Random()
    a = list(a)

    def _quick_sort(arr, lo, hi):
        if lo < hi:
            pivot_idx = rng.randrange(lo, hi + 1)
            arr[lo], arr[pivot_idx] = arr[pivot_idx], arr[lo]
            pivot = arr[lo]
            i = lo + 1
            for j in range(lo + 1, hi + 1):
                if arr[j] < pivot:
                    arr[i], arr[j] = arr[j], arr[i]
                    i += 1
            arr[lo], arr[i - 1] = arr[i - 1], arr[lo]
            _quick_sort(arr, lo, i - 2)
            _quick_sort(arr, i, hi)

    _quick_sort(a, 0, len(a) - 1)
    return a

def stability_demo() -> None:
    print("\nДемонстрация стабильности (ключ, метка):")
    data = [(2, "a"), (1, "b"), (2, "c"), (1, "d")]

    def sort_pairs(pairs, sort_func):
        pass

    def bubble_stable(arr):
        arr = list(arr)
        n = len(arr)
        for i in range(n):
            for j in range(n - i - 1):
                if arr[j][0] > arr[j+1][0]:
                    arr[j], arr[j+1] = arr[j+1], arr[j]
        return arr

    def insertion_stable(arr):
        arr = list(arr)
        for i in range(1, len(arr)):
            key = arr[i]
            j = i - 1
            while j >= 0 and arr[j][0] > key[0]:
                arr[j+1] = arr[j]
                j -= 1
            arr[j+1] = key
        return arr

    def selection_unstable(arr):
        arr = list(arr)
        n = len(arr)
        for i in range(n):
            min_idx = i
            for j in range(i+1, n):
                if arr[j][0] < arr[min_idx][0]:
                    min_idx = j
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
        return arr

    def quick_unstable(arr, rng=None):
        if rng is None: rng = random.Random(0)
        arr = list(arr)
        def _qs(a, lo, hi):
            if lo < hi:
                p = rng.randrange(lo, hi + 1)
                a[lo], a[p] = a[p], a[lo]
                pivot = a[lo][0]
                i = lo + 1
                for j in range(lo + 1, hi + 1):
                    if a[j][0] < pivot:
                        a[i], a[j] = a[j], a[i]
                        i += 1
                a[lo], a[i-1] = a[i-1], a[lo]
                _qs(a, lo, i-2)
                _qs(a, i, hi)
        _qs(arr, 0, len(arr)-1)
        return arr

    print(f"  Исходный: {data}")
    print(f"  Пузырёк (стабильный): {bubble_stable(data)}")
    print(f"  Вставки (стабильный): {insertion_stable(data)}")
    print(f"  Выбором (нестабильный): {selection_unstable(data)}")
    print(f"  QuickSort (нестабильный): {quick_unstable(data)}")


def make_inputs(n: int, seed: int) -> dict[str, list[int]]:
    rng = random.Random(seed + n)
    data = [rng.randint(-1_000_000, 1_000_000) for _ in range(n)]
    return {
        "упорядоченный": sorted(data),
        "случайный": data,
        "обратный": sorted(data, reverse=True),
    }

ALGORITHMS = {
    "bubble_sort": lambda a: bubble_sort(a)[0],
    "insertion_sort": lambda a: insertion_sort(a)[0],
    "selection_sort": lambda a: selection_sort(a)[0],
    "quick_sort": lambda a: quick_sort(a, random.Random(0)),
}

def is_sorted(a: list) -> bool:
    return all(a[i] <= a[i + 1] for i in range(len(a) - 1))

class SelfCheckError(Exception):
    pass

def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SelfCheckError(message)

def check_algorithm(fn) -> None:
    boundary = [[], [7], [5, 5, 5, 5], [1, 2, 3, 4, 5], [5, 4, 3, 2, 1]]
    for a in boundary:
        res = fn(list(a))
        expect(isinstance(res, list), f"возвращён {type(res).__name__}, а не список")
        expect(is_sorted(res), f"нарушен порядок на {a}: получено {res}")
        expect(sorted(res) == sorted(a), f"не перестановка входа {a}: получено {res}")

    rng = random.Random(0)
    for _ in range(300):
        a = [rng.randint(-100, 100) for _ in range(rng.randint(0, 80))]
        res = fn(list(a))
        expect(res == sorted(a), f"расходится с sorted() на {a}: получено {res}")

def check_counters() -> None:
    _, comparisons, _ = selection_sort([3, 1, 2, 5, 4])
    expect(comparisons == 10, f"selection_sort: неверный счётчик сравнений — {comparisons}, ожидалось 10")

def self_check() -> None:
    checks = [(name, lambda fn=fn: check_algorithm(fn)) for name, fn in ALGORITHMS.items()]
    checks.append(("счётчики", check_counters))
    failed = 0
    print("self_check:")
    for name, check in checks:
        try:
            check()
        except Exception as e:
            print(f"  {name}: ОШИБКА — {e}")
            failed += 1
        else:
            print(f"  {name}: OK")
    if failed:
        raise SystemExit(f"self_check: не пройдено разделов — {failed}")
    print("self_check: OK")


SIZES_QUADRATIC = [500, 1_000, 2_000, 4_000, 8_000]
SIZES_QUICK = [1_000, 3_000, 10_000, 30_000, 100_000]
REPEATS = 5

def bench(fn, data: list) -> float:
    fn(list(data))
    times = []
    for _ in range(REPEATS):
        arg = list(data)
        t0 = time.perf_counter()
        fn(arg)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)

def run_benchmarks(seed: int) -> dict:
    plans = [
        ("bubble_sort", ALGORITHMS["bubble_sort"], SIZES_QUADRATIC),
        ("insertion_sort", ALGORITHMS["insertion_sort"], SIZES_QUADRATIC),
        ("selection_sort", ALGORITHMS["selection_sort"], SIZES_QUADRATIC),
        ("quick_sort", lambda a: quick_sort(a, random.Random(seed)), SIZES_QUICK),
    ]
    results = {}
    for name, fn, sizes in plans:
        print(f"\n{name}:")
        results[name] = {}
        for cls in ("упорядоченный", "случайный", "обратный"):
            results[name][cls] = []
            for n in sizes:
                data = make_inputs(n, seed)[cls]
                t = bench(fn, data)
                results[name][cls].append((n, t))
                print(f"  n={n:>7}  вход={cls:<13} t={t:.6f} c")
    return results

def plot_results(results: dict) -> None:
    plt.figure(figsize=(10, 6))
    markers = {"bubble_sort": "o", "insertion_sort": "s", "selection_sort": "^", "quick_sort": "D"}
    for name, cls_data in results.items():
        for cls, points in cls_data.items():
            ns = [p[0] for p in points]
            ts = [p[1] for p in points]
            plt.loglog(ns, ts, marker=markers[name], label=f"{name} / {cls}")
    plt.xlabel("n (log)")
    plt.ylabel("t (log)")
    plt.title("Сравнение сортировок")
    plt.grid(True, which="both")
    plt.legend(fontsize=8)
    plt.savefig("sorting_loglog.png", dpi=150)
    plt.close()
    print("\nГрафик сохранён в sorting_loglog.png")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", type=int, required=True)
    args = ap.parse_args()
    seed = 30 + args.variant
    random.seed(seed)
    
    self_check()
    stability_demo()
    results = run_benchmarks(seed)
    plot_results(results)

if __name__ == "__main__":
    main()
