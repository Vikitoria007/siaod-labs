from __future__ import annotations

import json
import random
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from algorithms import array_sum, array_max, count_equal_pairs, binpow
from benchmark import benchmark
from data_gen import SIZES, KINDS, make_all

VARIANT = 20
OUT = Path("results")
OUT.mkdir(exist_ok=True)


def run_arrays(variant: int) -> dict:
    data = make_all(variant)
    out: dict = {
        "variant": variant,
        "seed": 30 + variant,
        "sizes": list(SIZES),
        "data": {},
    }

    for kind in KINDS:
        out["data"][kind] = {"sum": [], "max": [], "pairs": []}
        for n in SIZES:
            arr = data[kind][n]
            out["data"][kind]["sum"].append(benchmark(array_sum, arr))
            out["data"][kind]["max"].append(benchmark(array_max, arr))
            out["data"][kind]["pairs"].append(benchmark(count_equal_pairs, arr))
        print(f"[{kind}] done")
    return out


def run_binpow(variant: int) -> dict:
    seed = 30 + variant
    rnd = random.Random(seed)

    mod = 10**9 + 7
    a = rnd.randrange(2, mod)
    bits = list(range(15, 30))
    times = []

    def binpow_repeat(a_, b_, mod_, n_iter=5000):
        for _ in range(n_iter):
            binpow(a_, b_, mod_)

    for k in bits:
        b = 1 << k
        t = benchmark(binpow_repeat, a, b, mod, 5000, repeats=5)
        times.append(t / 5000)
    return {"a": a, "mod": mod, "k": bits, "times": times}

def plot_loglog(data: dict) -> None:
    sizes = np.array(data["sizes"])
    fig, ax = plt.subplots(figsize=(9, 6))
    markers = {"sum": "o", "max": "s", "pairs": "^"}
    for kind in KINDS:
        for name in ("sum", "max", "pairs"):
            t = np.array(data["data"][kind][name])
            ax.loglog(sizes, t, marker=markers[name], label=f"{name}-{kind}")
    ax.set_xlabel("n (log scale)")
    ax.set_ylabel("t, s (log scale)")
    ax.set_title(f"Variant {data['variant']}: log-log, seed={data['seed']}")
    ax.grid(True, which="both", ls=":")
    ax.legend(fontsize=7, ncol=2, loc="upper left")
    fig.tight_layout()
    fig.savefig(OUT / "arrays_loglog.png", dpi=150)
    plt.close(fig)


def plot_binpow(res: dict) -> None:
    k = np.array(res["k"])
    t = np.array(res["times"])
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(k, t, "o-", label="binpow(mod)")
    coef = np.polyfit(k, t, 1)
    ax.plot(k, np.polyval(coef, k), "--",
            label=f"linear fit: slope={coef[0]:.2e}")
    ax.set_xlabel("log2 b")
    ax.set_ylabel("t, s")
    ax.set_title(f"binpow: t vs log2 b, mod={res['mod']}")
    ax.grid(True, ls=":")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "binpow_t_vs_log2b.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    res_arrays = run_arrays(VARIANT)
    (OUT / "arrays.json").write_text(
        json.dumps(res_arrays, indent=2), encoding="utf-8"
    )
    plot_loglog(res_arrays)

    res_binpow = run_binpow(VARIANT)
    (OUT / "binpow.json").write_text(
        json.dumps(res_binpow, indent=2), encoding="utf-8"
    )
    plot_binpow(res_binpow)
    print("done:", OUT.resolve())