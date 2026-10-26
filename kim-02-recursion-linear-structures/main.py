from __future__ import annotations

import argparse
import collections
import functools
import json
import math
import random
import statistics
import sys
import time
import traceback
from pathlib import Path
import matplotlib.pyplot as plt

FRONT_SIZES = (1_000, 3_000, 10_000, 30_000, 100_000)
FRONT_OPS = 1_000
FIB_NS = (5, 10, 15, 20, 25, 30)
REPEATS = 5

CALLS = {"fib_naive": 0, "fib_memo": 0}

def factorial(n: int) -> int:
    if n == 0:
        return 1
    return n * factorial(n - 1)

def fib_naive(n: int) -> int:
    CALLS["fib_naive"] += 1
    if n < 2:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)

def fib_memo(n: int, memo: dict[int, int] | None = None) -> int:
    CALLS["fib_memo"] += 1
    if memo is None:
        memo = {}
    if n in memo:
        return memo[n]
    if n < 2:
        res = n
    else:
        res = fib_memo(n - 1, memo) + fib_memo(n - 2, memo)
    memo[n] = res
    return res

def hanoi(n: int, src: str = "A", dst: str = "C", aux: str = "B",
          moves: list[tuple[str, str]] | None = None) -> int:
    if n == 0:
        return 0
    count = 0
    count += hanoi(n - 1, src, aux, dst, moves)
    if moves is not None:
        moves.append((src, dst))
    count += 1
    count += hanoi(n - 1, aux, dst, src, moves)
    return count

class DynamicArray:
    INITIAL_CAPACITY = 4

    def __init__(self) -> None:
        self._capacity = self.INITIAL_CAPACITY
        self._size = 0
        self._buffer: list = [None] * self._capacity
        self.copies = 0

    def __len__(self) -> int:
        return self._size

    @property
    def capacity(self) -> int:
        return self._capacity

    def _grow(self) -> None:
        new_cap = self._capacity * 2
        new_buf = [None] * new_cap
        for i in range(self._size):
            new_buf[i] = self._buffer[i]
        self.copies += self._size
        self._buffer = new_buf
        self._capacity = new_cap

    def append(self, value) -> None:
        if self._size == self._capacity:
            self._grow()
        self._buffer[self._size] = value
        self._size += 1

    def pop(self):
        if self._size == 0:
            raise IndexError("pop from empty DynamicArray")
        val = self._buffer[self._size - 1]
        self._buffer[self._size - 1] = None
        self._size -= 1
        return val

    def get(self, index: int):
        if index < 0 or index >= self._size:
            raise IndexError("DynamicArray index out of range")
        return self._buffer[index]

    def set(self, index: int, value) -> None:
        if index < 0 or index >= self._size:
            raise IndexError("DynamicArray index out of range")
        self._buffer[index] = value

class Stack:
    """Стек (LIFO) на базе DynamicArray."""
    def __init__(self) -> None:
        self._data = DynamicArray()

    def __len__(self) -> int:
        return len(self._data)

    def push(self, value) -> None:
        self._data.append(value)

    def pop(self):
        return self._data.pop()

    def peek(self):
        if len(self) == 0:
            raise IndexError("peek from empty Stack")
        return self._data.get(len(self._data) - 1)

class _Node:
    __slots__ = ("value", "prev", "next")
    def __init__(self, value, prev=None, next=None) -> None:
        self.value = value
        self.prev = prev
        self.next = next

class Deque:
    def __init__(self) -> None:
        self._head: _Node | None = None
        self._tail: _Node | None = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def push_front(self, value) -> None:
        node = _Node(value, None, self._head)
        if self._head:
            self._head.prev = node
        self._head = node
        if self._tail is None:
            self._tail = node
        self._size += 1

    def push_back(self, value) -> None:
        node = _Node(value, self._tail, None)
        if self._tail:
            self._tail.next = node
        self._tail = node
        if self._head is None:
            self._head = node
        self._size += 1

    def pop_front(self):
        if self._head is None:
            raise IndexError("pop_front from empty Deque")
        val = self._head.value
        self._head = self._head.next
        if self._head:
            self._head.prev = None
        else:
            self._tail = None
        self._size -= 1
        return val

    def pop_back(self):
        if self._tail is None:
            raise IndexError("pop_back from empty Deque")
        val = self._tail.value
        self._tail = self._tail.prev
        if self._tail:
            self._tail.next = None
        else:
            self._head = None
        self._size -= 1
        return val

class SelfCheckError(Exception):
    pass

def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SelfCheckError(message)

def expect_index_error(call, what: str) -> None:
    try:
        call()
    except IndexError:
        return
    raise SelfCheckError(f"{what}: ожидался IndexError")

def stack_methods(st: Stack) -> dict:
    return {"push": st.push, "pop": st.pop, "peek": st.peek, "len": st.__len__}

def list_stack_methods(a: list) -> dict:
    return {"push": a.append, "pop": a.pop, "peek": lambda: a[-1], "len": a.__len__}

def deque_methods(dq: Deque) -> dict:
    return {"push_front": dq.push_front, "push_back": dq.push_back,
            "pop_front": dq.pop_front, "pop_back": dq.pop_back, "len": dq.__len__}

def std_deque_methods(d: collections.deque) -> dict:
    return {"push_front": d.appendleft, "push_back": d.append,
            "pop_front": d.popleft, "pop_back": d.pop, "len": d.__len__}

def apply_op(methods: dict, op: str, arg: int | None):
    try:
        return methods[op]() if arg is None else methods[op](arg)
    except IndexError:
        return "IndexError"

def compare_with_reference(ops: list[tuple], own: dict, ref: dict, label: str) -> None:
    for i, (op, arg) in enumerate(ops, start=1):
        got = apply_op(own, op, arg)
        expected = apply_op(ref, op, arg)
        expect(got == expected, f"{label}, оп {i}: {got!r} != {expected!r}")
        expect(own["len"]() == ref["len"](), f"{label}, оп {i}: len mismatch")

def random_ops(rng, pushes, others, count, max_size) -> list[tuple]:
    ops = []
    size = 0
    for _ in range(count):
        op = rng.choice(pushes + others)
        if op in pushes and size >= max_size:
            op = rng.choice(others)
        if op in pushes:
            ops.append((op, rng.randrange(100)))
            size += 1
        else:
            ops.append((op, None))
            size = max(0, size - op.startswith("pop"))
    return ops

def expected_capacity(size: int) -> int:
    cap = DynamicArray.INITIAL_CAPACITY
    while cap < size:
        cap *= 2
    return cap

def expected_copies(size: int) -> int:
    copies, cap = 0, DynamicArray.INITIAL_CAPACITY
    while cap < size:
        copies += cap
        cap *= 2
    return copies

def check_recursion() -> None:
    for n in range(21):
        expect(factorial(n) == math.factorial(n), f"factorial({n})")
    fib = [0, 1]
    while len(fib) <= 90:
        fib.append(fib[-1] + fib[-2])
    for n in range(21):
        expect(fib_naive(n) == fib[n], f"fib_naive({n})")
    CALLS["fib_naive"] = 0
    fib_naive(20)
    expect(CALLS["fib_naive"] >= fib[20], "fib_naive не наивная")
    for n in (0, 1, 2, 10, 30, 90):
        CALLS["fib_memo"] = 0
        expect(fib_memo(n) == fib[n], f"fib_memo({n})")
        expect(CALLS["fib_memo"] <= 2 * n + 1, f"fib_memo({n}) вызовов много")
    for n, (src, dst, aux) in ((0, "ACB"), (1, "ACB"), (2, "ACB"), (3, "XZY"), (6, "ACB"), (7, "PQR")):
        moves = []
        count = hanoi(n, src, dst, aux, moves)
        expect(count == 2**n - 1, f"hanoi({n}) count")
        expect(len(moves) == count, f"hanoi({n}) len(moves)")
        towers = {src: list(range(n, 0, -1)), dst: [], aux: []}
        for k, move in enumerate(moves, 1):
            frm, to = move
            expect(bool(towers[frm]), f"hanoi ход {k} пусто")
            disk = towers[frm].pop()
            top = towers[to][-1] if towers[to] else None
            expect(top is None or top > disk, f"hanoi ход {k} больший на меньший")
            towers[to].append(disk)
        expect(towers[dst] == list(range(n, 0, -1)), f"hanoi({n}) результат")

def check_dynamic_array() -> None:
    arr = DynamicArray()
    expect(len(arr) == 0 and arr.capacity == DynamicArray.INITIAL_CAPACITY, "пустой")
    expect_index_error(lambda: arr.get(0), "get(0)")
    expect_index_error(arr.pop, "pop()")
    ref = []
    for i in range(100):
        arr.append(i * i)
        ref.append(i * i)
        expect(len(arr) == len(ref), f"len после {len(ref)}")
        expect(arr.capacity == expected_capacity(len(ref)), f"cap после {len(ref)}")
        expect(arr.copies == expected_copies(len(ref)), f"copies после {len(ref)}")
    for i, v in enumerate(ref):
        expect(arr.get(i) == v, f"get({i})")
    arr.set(0, -1)
    arr.set(99, -99)
    ref[0], ref[99] = -1, -99
    expect(arr.get(0) == -1 and arr.get(99) == -99, "set")
    for bad in (100, arr.capacity - 1, arr.capacity, -1, -100):
        expect_index_error(lambda b=bad: arr.get(b), f"get({bad})")
        expect_index_error(lambda b=bad: arr.set(b, 0), f"set({bad})")
    for refill in (70, 0):
        while ref:
            cap_before = arr.capacity
            got, expected = arr.pop(), ref.pop()
            expect(got == expected, f"pop({len(ref)+1})")
            expect(len(arr) == len(ref), f"len pop")
            expect(arr.capacity == cap_before or
                   (arr.capacity == cap_before // 2 and len(ref) <= cap_before // 4 and arr.capacity >= DynamicArray.INITIAL_CAPACITY),
                   "сжатие")
        expect_index_error(arr.pop, "pop пустого")
        for i in range(refill):
            arr.append(i)
            ref.append(i)
            expect(len(arr) == len(ref) <= arr.capacity, "refill")

def check_stack() -> None:
    st = Stack()
    expect(len(st) == 0, "пустой")
    expect_index_error(st.pop, "pop пустого")
    expect_index_error(st.peek, "peek пустого")
    for start in (0, 100):
        values = list(range(start, start + 20))
        for k, x in enumerate(values, 1):
            st.push(x)
            expect(st.peek() == x and len(st) == k, "push")
        expect(st.peek() == values[-1] and len(st) == len(values), "peek")
        for k, expected in enumerate(reversed(values), 1):
            expect(st.pop() == expected, f"pop {k} LIFO")
            expect(len(st) == len(values) - k, "len pop")
        expect_index_error(st.pop, "pop пустого")
        expect_index_error(st.peek, "peek пустого")
    own, ref = Stack(), []
    ops = random_ops(random.Random(1), ("push",), ("pop", "peek"), 3000, 40)
    compare_with_reference(ops, stack_methods(own), list_stack_methods(ref), "Stack vs list")

def check_deque() -> None:
    dq = Deque()
    expect(len(dq) == 0, "пустой")
    expect_index_error(dq.pop_front, "pop_front пустого")
    expect_index_error(dq.pop_back, "pop_back пустого")
    pushes, pops = ("push_front", "push_back"), ("pop_front", "pop_back")
    for p1 in pushes:
        for q1 in pops:
            for p2 in pushes:
                for q2 in pops:
                    dq = Deque()
                    getattr(dq, p1)(1)
                    first = getattr(dq, q1)()
                    getattr(dq, p2)(2)
                    second = getattr(dq, q2)()
                    expect((first, second, len(dq)) == (1, 2, 0), f"{p1} {q1} {p2} {q2}")
                    expect_index_error(dq.pop_front, f"{p1} {q1} {p2} {q2} + pop_front")
                    expect_index_error(dq.pop_back, f"{p1} {q1} {p2} {q2} + pop_back")
    own, ref = Deque(), collections.deque()
    ops = random_ops(random.Random(2), pushes, pops, 5000, 12)
    compare_with_reference(ops, deque_methods(own), std_deque_methods(ref), "Deque vs deque")

def check_variant_ops(stack_ops: list[tuple], deque_ops: list[tuple]) -> None:
    compare_with_reference(stack_ops, stack_methods(Stack()), list_stack_methods([]), "ops_stack")
    compare_with_reference(deque_ops, deque_methods(Deque()), std_deque_methods(collections.deque()), "ops_deque")

def self_check(stack_ops: list[tuple], deque_ops: list[tuple]) -> None:
    checks = (
        ("рекурсия", check_recursion),
        ("DynamicArray", check_dynamic_array),
        ("Stack", check_stack),
        ("Deque", check_deque),
        ("операции варианта", lambda: check_variant_ops(stack_ops, deque_ops)),
    )
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


def find_data_dir(explicit: Path | None) -> Path:
    if explicit is not None:
        if not explicit.is_dir():
            raise SystemExit(f"Каталог не найден: {explicit}")
        return explicit
    candidates = []
    for base in (Path.cwd(), Path(__file__).resolve().parent):
        for parent in (base, *base.parents):
            candidates.append(parent / "data" / "generated")
    for path in candidates:
        if path.is_dir():
            return path
    raise SystemExit("Не найден каталог data/generated...")

def check_variant(data_dir: Path, variant: int) -> None:
    manifest_path = data_dir / "manifest.json"
    if not manifest_path.is_file():
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    actual = manifest.get("variant")
    if actual != variant:
        raise SystemExit(f"Данные для варианта {actual}, а запуск с {variant}.")
    print(f"Данные варианта {variant} (seed={manifest.get('seed')}) из {data_dir}")

def read_data_lines(data_dir: Path, name: str) -> list[str]:
    path = data_dir / name
    return path.read_text(encoding="utf-8").splitlines()

def load_append_sizes(data_dir: Path) -> list[int]:
    return [int(line) for line in read_data_lines(data_dir, "ops_append_sizes.txt")]

def load_ops(data_dir: Path, kind: str) -> list[tuple]:
    ops = []
    for line in read_data_lines(data_dir, f"ops_{kind}.txt"):
        name, *arg = line.split()
        ops.append((name, int(arg[0]) if arg else None))
    return ops


def bench(call) -> float:
    call()
    times = []
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        call()
        times.append(time.perf_counter() - t0)
    return statistics.median(times)

def log_log_slope(points: list[tuple[int, float]]) -> float:
    xs = [math.log10(n) for n, _ in points]
    ys = [math.log10(t) for _, t in points]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    return (sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs))

def appends(add, n: int) -> None:
    for i in range(n):
        add(i)

def steady_ops(add, remove, k: int = FRONT_OPS) -> None:
    for i in range(k):
        add(i)
        remove()

def replay(ops: list[tuple], methods: dict) -> None:
    for op, arg in ops:
        try:
            if arg is None:
                methods[op]()
            else:
                methods[op](arg)
        except IndexError:
            pass

def filled_structure(kind: str, n: int):
    if kind == "list":
        return list(range(n))
    if kind == "deque":
        return collections.deque(range(n))
    dq = Deque()
    appends(dq.push_back, n)
    return dq

FRONT_CASES = {
    "insert": (
        ("list.insert(0, x) + pop()", "list", lambda a: (functools.partial(a.insert, 0), a.pop)),
        ("deque.appendleft + pop", "deque", lambda d: (d.appendleft, d.pop)),
        ("Deque.push_front + pop_back", "Deque", lambda d: (d.push_front, d.pop_back)),
    ),
    "remove": (
        ("list.append + pop(0)", "list", lambda a: (a.append, functools.partial(a.pop, 0))),
        ("deque.append + popleft", "deque", lambda d: (d.append, d.popleft)),
        ("Deque.push_back + pop_front", "Deque", lambda d: (d.push_back, d.pop_front)),
    ),
}
FRONT_TITLES = {"insert": "Вставка в начало", "remove": "Удаление из начала"}

def run_benchmarks(append_sizes: list[int], stack_ops: list[tuple], deque_ops: list[tuple]) -> dict:
    results: dict = {}
    print("\nЧисло вызовов: наивная рекурсия против мемоизации")
    fib_data = []
    for n in FIB_NS:
        CALLS["fib_naive"] = CALLS["fib_memo"] = 0
        value = fib_naive(n)
        fib_memo(n)
        print(f"  n={n:>2}  F(n)={value:>6}  fib_naive: {CALLS['fib_naive']:>7} вызовов  fib_memo: {CALLS['fib_memo']:>2} вызовов")
        fib_data.append((n, CALLS["fib_naive"], CALLS["fib_memo"]))
    results["fib"] = fib_data

    print("\nСерии append на размерах варианта:")
    results["append"] = []
    for n in append_sizes:
        t_own = bench(lambda: appends(DynamicArray().append, n)) / n
        t_list = bench(lambda: appends([].append, n)) / n
        arr = DynamicArray()
        appends(arr.append, n)
        cost = (n + arr.copies) / n
        results["append"].append((n, t_own, t_list, cost))
        print(f"  n={n:>7}  t/n: DynamicArray {t_own:.2e} c, list {t_list:.2e} c  копирований {arr.copies:>7}  (n + копирования)/n = {cost:.3f}")

    for key, title in FRONT_TITLES.items():
        print(f"\n{title}: время одной операции при размере n = {', '.join(map(str, FRONT_SIZES))}")
        results[key] = {}
        for label, kind, methods in FRONT_CASES[key]:
            points = []
            for n in FRONT_SIZES:
                add, remove = methods(filled_structure(kind, n))
                points.append((n, bench(lambda: steady_ops(add, remove)) / FRONT_OPS))
            results[key][label] = points
            row = "  ".join(f"{t:.2e}" for _, t in points)
            print(f"  {label:28s} {row}   наклон {log_log_slope(points):.2f}")

    print("\nОперации варианта целиком: время на операцию")
    cases = (
        ("ops_stack.txt", stack_ops, "Stack", lambda: stack_methods(Stack()), "list", lambda: list_stack_methods([])),
        ("ops_deque.txt", deque_ops, "Deque", lambda: deque_methods(Deque()), "collections.deque", lambda: std_deque_methods(collections.deque())),
    )
    for name, ops, own_name, own_factory, ref_name, ref_factory in cases:
        t_own = bench(lambda: replay(ops, own_factory()))
        t_ref = bench(lambda: replay(ops, ref_factory()))
        results[name] = {"own": t_own, "ref": t_ref}
        print(f"  {name}: {own_name} {t_own:.4f} c, {ref_name} {t_ref:.4f} c")
    return results

def plot_results(results: dict) -> None:
    n_vals = [x[0] for x in results["append"]]
    t_own = [x[1] for x in results["append"]]
    plt.figure(figsize=(8, 5))
    plt.plot(n_vals, t_own, marker="o", label="DynamicArray")
    plt.xlabel("n")
    plt.ylabel("t/n (сек)")
    plt.title("Средняя стоимость append")
    plt.grid(True)
    plt.legend()
    plt.savefig("append_cost.png")
    plt.close()

    plt.figure(figsize=(8, 5))
    for label, points in results["insert"].items():
        n_vals = [x[0] for x in points]
        t_vals = [x[1] for x in points]
        plt.loglog(n_vals, t_vals, marker="o", label=label)
    plt.xlabel("n (log)")
    plt.ylabel("t (log)")
    plt.title("Вставка в начало")
    plt.grid(True, which="both")
    plt.legend()
    plt.savefig("insert_front.png")
    plt.close()

    plt.figure(figsize=(8, 5))
    for label, points in results["remove"].items():
        n_vals = [x[0] for x in points]
        t_vals = [x[1] for x in points]
        plt.loglog(n_vals, t_vals, marker="o", label=label)
    plt.xlabel("n (log)")
    plt.ylabel("t (log)")
    plt.title("Удаление из начала")
    plt.grid(True, which="both")
    plt.legend()
    plt.savefig("remove_front.png")
    plt.close()

    print("Графики сохранены в append_cost.png, insert_front.png, remove_front.png")

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", type=int, required=True)
    parser.add_argument("--data", type=Path, default=None)
    args = parser.parse_args()

    data_dir = find_data_dir(args.data)
    check_variant(data_dir, args.variant)
    stack_ops = load_ops(data_dir, "stack")
    deque_ops = load_ops(data_dir, "deque")
    append_sizes = load_append_sizes(data_dir)

    self_check(stack_ops, deque_ops)
    results = run_benchmarks(append_sizes, stack_ops, deque_ops)

    out = Path("results.json")
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nРезультаты сохранены в {out.resolve()}")
    plot_results(results)

if __name__ == "__main__":
    main()