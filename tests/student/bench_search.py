"""naive / KMP / exact Rabin-Karp comparison. Run from the repository root:

    python tests/student/bench_search.py

Same (text, pattern) pair goes to all three algorithms. Timed scope: ONE call of
algorithms.naive/kmp/rk(request) (includes prefix-function/hash setup, excludes
input generation, JSON parsing and output printing). Timer: time.perf_counter().
Warm-up: 1 untimed call per algorithm and input. Runs: 5 timed runs, median reported.
Generator seed: 4242 (random.Random(SEED + n)).
"""
import os
import platform
import random
import statistics
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                'Python', 'source'))
import algorithms as A  # noqa: E402

SEED, RUNS = 4242, 5
SIZES = [(500, 50), (1500, 150), (3000, 300)]       # (n, m), all inside the common domain n, m <= 3000


def make(case, n, m, rng):
    if case == 'random':                              # 4-letter random text; pattern = a slice of it (has matches)
        t = ''.join(rng.choice('abcd') for _ in range(n))
        s = rng.randrange(n - m + 1)
        return t, t[s:s + m]
    return 'a' * n, 'a' * (m - 1) + 'b'               # repetitive: long partial matches, zero full matches


def main():
    print(f'python {platform.python_version()} | {platform.platform()} | {platform.machine()}')
    print(f'seed={SEED} runs={RUNS} warm-up=1 timer=perf_counter unit=milliseconds')
    print('|Case|n|m|Seed/generator|Algorithm|Run 1|Run 2|Run 3|Run 4|Run 5|Median|Correct outputs checked|')
    print('|---|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---|')
    for case in ('random', 'repetitive'):
        for n, m in SIZES:
            rng = random.Random(SEED + n)
            t, p = make(case, n, m, rng)
            req = {'text': t, 'pattern': p}
            outs = {}
            rows = {}
            for name, f in (('naive', A.naive), ('kmp', A.kmp), ('rk', A.rk)):
                f(req)                                # warm-up
                ts = []
                for _ in range(RUNS):
                    t0 = time.perf_counter()
                    r = f(req)
                    ts.append((time.perf_counter() - t0) * 1000)
                outs[name] = r['positions']
                rows[name] = ts
            ok = outs['naive'] == outs['kmp'] == outs['rk']
            assert ok, 'algorithms disagree'
            for name, ts in rows.items():
                cells = '|'.join(f'{x:.3f}' for x in ts)
                print(f'|{case}|{n}|{m}|random.Random({SEED}+{n}) {case}|{name}|{cells}|'
                      f'{statistics.median(ts):.3f}|yes, {len(outs[name])} starts, equal across 3|')


if __name__ == '__main__':
    main()
