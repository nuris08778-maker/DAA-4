"""Own tests for Assignment 4 (Python). Run from the repository root:

    python -m unittest discover -s tests/student -v

Small cases are compared with independently written brute-force oracles (different
method from the implementation). Witnesses (LCS sequence, merge plan, tree set,
repeated substring) are checked for VALIDITY, so any other optimal answer passes too.
"""
import itertools
import json
import os
import random
import subprocess
import sys
import time
import unittest
from functools import lru_cache

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, 'Python', 'source')
sys.path.insert(0, SRC)
import algorithms as A  # noqa: E402

ALPHA = 'ab'


def rs(rng, n, alpha=ALPHA):
    return ''.join(rng.choice(alpha) for _ in range(n))


def is_subseq(s, t):
    it = iter(t)
    return all(c in it for c in s)


# ----------------------------------------------------------------- oracles
def lcs_len_brute(a, b):                      # exhaustive over subsequences of the shorter string
    if len(a) > len(b):
        a, b = b, a
    for k in range(len(a), -1, -1):
        for idx in itertools.combinations(range(len(a)), k):
            if is_subseq(''.join(a[i] for i in idx), b):
                return k
    return 0


def merge_brute(sizes):                       # try EVERY adjacent pair on the current block list
    @lru_cache(None)
    def go(blocks):
        if len(blocks) <= 1:
            return 0
        return min(blocks[i] + blocks[i + 1] + go(blocks[:i] + (blocks[i] + blocks[i + 1],) + blocks[i + 2:])
                   for i in range(len(blocks) - 1))
    return go(tuple(sizes))


def check_plan(tc, sizes, res):
    n = len(sizes)
    if n <= 1:
        tc.assertEqual(res, {'cost': 0, 'plan': []})
        return
    blocks = {(i, i): sizes[i] for i in range(n)}      # current blocks: interval -> size
    total = 0
    self_plan = res['plan']
    tc.assertEqual(len(self_plan), n - 1)
    for l, k, r in self_plan:
        tc.assertIn((l, k), blocks)                    # both children exist NOW (chronological)
        tc.assertIn((k + 1, r), blocks)
        s = blocks.pop((l, k)) + blocks.pop((k + 1, r))
        total += s
        blocks[(l, r)] = s
    tc.assertEqual(list(blocks), [(0, n - 1)])
    tc.assertEqual(total, res['cost'])


def tree_brute(n, w, edges):
    best = 0
    for mask in range(1 << n):
        if any((mask >> u) & 1 and (mask >> v) & 1 for u, v in edges):
            continue
        best = max(best, sum(w[i] for i in range(n) if (mask >> i) & 1))
    return best


def check_tree(tc, req, res):
    sel = res['selected']
    tc.assertEqual(len(sel), len(set(sel)))
    s = set(sel)
    tc.assertTrue(all(0 <= v < req['n'] for v in s))
    for u, v in req['edges']:
        tc.assertFalse(u in s and v in s)
    tc.assertEqual(sum(req['weights'][v] for v in s), res['weight'])


def find_all(t, p):                           # oracle for search: str.find in a loop
    if p == '':
        return list(range(len(t) + 1))
    out, i = [], t.find(p)
    while i != -1:
        out.append(i)
        i = t.find(p, i + 1)
    return out


def sa_brute(s):
    return sorted(range(len(s)), key=lambda i: s[i:])


def lcp_brute(s, sa):
    out = [0] * len(sa)
    for i in range(1, len(sa)):
        a, b = s[sa[i - 1]:], s[sa[i]:]
        k = 0
        while k < min(len(a), len(b)) and a[k] == b[k]:
            k += 1
        out[i] = k
    return out


def longest_repeat_len(s):
    best = 0
    for i in range(len(s)):
        for j in range(i + 1, len(s)):
            k = 0
            while j + k < len(s) and s[i + k] == s[j + k]:
                k += 1
            best = max(best, k)
    return best


def aho_brute(patterns, texts):
    return [[len(find_all(t, p)) for p in patterns] for t in texts]


# ----------------------------------------------------------------- tests
class TestLCS(unittest.TestCase):
    def test_edges(self):
        self.assertEqual(A.lcs({'a': '', 'b': ''}), {'length': 0, 'sequence': ''})
        self.assertEqual(A.lcs({'a': 'abc', 'b': ''}), {'length': 0, 'sequence': ''})
        self.assertEqual(A.lcs({'a': '', 'b': 'abc'}), {'length': 0, 'sequence': ''})

    def test_subsequence_not_substring(self):
        r = A.lcs({'a': 'tea_time', 'b': 'team'})
        self.assertEqual(r['length'], 4)                # a substring-only solution would give 3
        self.assertEqual(r['sequence'], 'team')

    def test_alternative_optima(self):
        r = A.lcs({'a': 'ab', 'b': 'ba'})               # 'a' and 'b' are both optimal
        self.assertEqual(r['length'], 1)
        self.assertIn(r['sequence'], ('a', 'b'))

    def test_random_vs_brute(self):
        rng = random.Random(1)
        for _ in range(300):
            a, b = rs(rng, rng.randint(0, 8), 'abc'), rs(rng, rng.randint(0, 8), 'abc')
            r = A.lcs({'a': a, 'b': b})
            self.assertEqual(r['length'], lcs_len_brute(a, b))
            self.assertEqual(len(r['sequence']), r['length'])
            self.assertTrue(is_subseq(r['sequence'], a) and is_subseq(r['sequence'], b))

    def test_scale(self):
        rng = random.Random(2)
        a, b = rs(rng, 1000, 'abcd'), rs(rng, 1000, 'abcd')
        r = A.lcs({'a': a, 'b': b})
        self.assertTrue(is_subseq(r['sequence'], a) and is_subseq(r['sequence'], b))
        self.assertEqual(len(r['sequence']), r['length'])
        self.assertEqual(A.lcs({'a': 'x' * 1000, 'b': 'x' * 1000})['length'], 1000)


class TestMerge(unittest.TestCase):
    def test_small_cases(self):
        self.assertEqual(A.merge({'sizes': []}), {'cost': 0, 'plan': []})
        self.assertEqual(A.merge({'sizes': [7]}), {'cost': 0, 'plan': []})
        r = A.merge({'sizes': [2, 3, 4]})
        self.assertEqual(r['cost'], 14)                 # (2+3)+9 = 14; (3+4)+9 = 16
        check_plan(self, [2, 3, 4], r)

    def test_adjacent_not_arbitrary(self):
        sizes = [1, 100, 1]                              # arbitrary pairing would merge the two 1s first
        r = A.merge({'sizes': sizes})
        self.assertEqual(r['cost'], 101 + 102)
        check_plan(self, sizes, r)

    def test_zeros_and_ties(self):
        for sizes in ([0, 0, 0, 0], [5, 5, 5, 5]):
            r = A.merge({'sizes': sizes})
            self.assertEqual(r['cost'], merge_brute(sizes))
            check_plan(self, sizes, r)

    def test_random_vs_brute(self):
        rng = random.Random(3)
        for _ in range(200):
            sizes = [rng.randint(0, 9) for _ in range(rng.randint(0, 7))]
            r = A.merge({'sizes': sizes})
            self.assertEqual(r['cost'], merge_brute(sizes), sizes)
            check_plan(self, sizes, r)

    def test_scale_large_cost(self):
        sizes = [10 ** 9] * 200
        t = time.time()
        r = A.merge({'sizes': sizes})
        self.assertLess(time.time() - t, 15)
        check_plan(self, sizes, r)
        self.assertGreater(r['cost'], 2 ** 40)           # needs 64-bit arithmetic
        rng = random.Random(4)
        sizes = [rng.randint(0, 10 ** 9) for _ in range(200)]
        check_plan(self, sizes, A.merge({'sizes': sizes}))


class TestTree(unittest.TestCase):
    def run_tree(self, n, w, edges):
        req = {'task': 'tree', 'n': n, 'weights': w, 'edges': edges}
        res = A.tree(req)
        check_tree(self, req, res)
        return res

    def test_small(self):
        self.assertEqual(A.tree({'n': 0, 'weights': [], 'edges': []}), {'weight': 0, 'selected': []})
        self.assertEqual(self.run_tree(1, [5], [])['weight'], 5)
        self.assertEqual(self.run_tree(1, [-5], [])['weight'], 0)         # empty set allowed
        self.assertEqual(self.run_tree(3, [-1, -2, -3], [[0, 1], [1, 2]])['weight'], 0)
        self.assertEqual(self.run_tree(3, [4, 9, 6], [[0, 1], [1, 2]])['weight'], 10)
        self.assertEqual(self.run_tree(2, [0, 0], [[0, 1]])['weight'], 0)  # zero / tie

    def test_random_vs_brute_and_root_independence(self):
        rng = random.Random(5)
        for _ in range(300):
            n = rng.randint(1, 10)
            w = [rng.randint(-5, 9) for _ in range(n)]
            edges = [[rng.randrange(i), i] for i in range(1, n)]
            rng.shuffle(edges)
            perm = list(range(n))
            rng.shuffle(perm)                                              # relabel vertices
            w2 = [0] * n
            for i in range(n):
                w2[perm[i]] = w[i]
            e2 = [[perm[u], perm[v]] for u, v in edges]
            r1 = self.run_tree(n, w, edges)
            r2 = self.run_tree(n, w2, e2)
            self.assertEqual(r1['weight'], tree_brute(n, w, edges))
            self.assertEqual(r1['weight'], r2['weight'])

    def test_deep_chain_and_star_large_sum(self):
        n = 100000
        chain = [[i, i + 1] for i in range(n - 1)]
        r = self.run_tree(n, [10 ** 9] * n, chain)
        self.assertEqual(r['weight'], 50000 * 10 ** 9)                      # 5e13 > 32 bits
        star = [[0, i] for i in range(1, n)]
        w = [10 ** 9] * n
        w[0] = 10 ** 9 + 5
        r = self.run_tree(n, w, star)
        self.assertEqual(r['weight'], (n - 1) * 10 ** 9)


class TestSearch(unittest.TestCase):
    def all3(self, t, p):
        req = {'text': t, 'pattern': p}
        a, b, c = A.naive(req)['positions'], A.kmp(req)['positions'], A.rk(req)['positions']
        return a, b, c

    def test_fixed(self):
        cases = [('', ''), ('abc', ''), ('', 'a'), ('ab', 'abc'), ('aaaaa', 'aaa'), ('abababa', 'aba'),
                 ('Hello, hello! HELLO', 'hello'), ('a b  c', ' '), ('a.b.c', '.'), ('aaa', 'aaaa'),
                 ('abc', 'abc')]
        for t, p in cases:
            exp = find_all(t, p)
            self.assertEqual(self.all3(t, p), (exp, exp, exp), (t, p))
        self.assertEqual(A.naive({'text': 'abc', 'pattern': ''})['positions'], [0, 1, 2, 3])  # final boundary

    def test_rk_collision(self):
        # 'ab' and 'dj' both hash to 75 (base 31, mod 101): equal hash is only a candidate.
        self.assertEqual(A.rk({'text': 'abdj', 'pattern': 'ab'})['positions'], [0])
        self.assertEqual(A.rk({'text': 'abdj', 'pattern': 'dj'})['positions'], [2])
        self.assertEqual(A.rk({'text': 'djdjab', 'pattern': 'ab'})['positions'], [4])

    def test_rk_negative_remainder(self):
        # text chars much larger than pattern chars force (ht - c*high) < 0 before the modulo
        t = 'z' * 20 + 'a' * 20 + 'zazaza'
        for p in ('aaa', 'zaz', 'a'):
            self.assertEqual(A.rk({'text': t, 'pattern': p})['positions'], find_all(t, p))

    def test_random_common_domain(self):
        rng = random.Random(6)
        for _ in range(400):
            t, p = rs(rng, rng.randint(0, 25), 'ab'), rs(rng, rng.randint(0, 5), 'ab')
            exp = find_all(t, p)
            self.assertEqual(self.all3(t, p), (exp, exp, exp), (t, p))

    def test_scale(self):
        n = 200000
        t, p = 'a' * n, 'a' * 100000
        exp = list(range(n - 100000 + 1))
        t0 = time.time()
        self.assertEqual(A.kmp({'text': t, 'pattern': p})['positions'], exp)
        self.assertLess(time.time() - t0, 10)
        rng = random.Random(7)
        t = rs(rng, 200000, 'abc')
        self.assertEqual(A.kmp({'text': t, 'pattern': 'abcab'})['positions'], find_all(t, 'abcab'))
        self.assertEqual(A.kmp({'text': t, 'pattern': ''})['positions'], list(range(200001)))
        # rk worst case: every window is a verified candidate, n*m = 20e6
        t, p = 'a' * 10000, 'a' * 2000
        t0 = time.time()
        self.assertEqual(A.rk({'text': t, 'pattern': p})['positions'], list(range(8001)))
        self.assertLess(time.time() - t0, 10)


class TestSuffix(unittest.TestCase):
    def check(self, s):
        r = A.suffix({'text': s})
        sa = sa_brute(s)
        self.assertEqual(r['sa'], sa, s)
        self.assertEqual(r['lcp'], lcp_brute(s, sa), s)
        L = longest_repeat_len(s)
        self.assertEqual(len(r['repeated']), L, s)
        if L:
            self.assertGreaterEqual(len(find_all(s, r['repeated'])), 2)    # occurs at two distinct starts

    def test_fixed(self):
        self.assertEqual(A.suffix({'text': ''}), {'sa': [], 'lcp': [], 'repeated': ''})
        self.assertEqual(A.suffix({'text': 'a'}), {'sa': [0], 'lcp': [0], 'repeated': ''})
        r = A.suffix({'text': 'banana'})
        self.assertEqual((r['sa'], r['lcp'], r['repeated']), ([5, 3, 1, 0, 4, 2], [0, 1, 3, 0, 0, 2], 'ana'))
        for s in ('aaaa', 'abcd', 'abab', 'aab', 'Ab aB', 'zzzz yyyy'):
            self.check(s)

    def test_random(self):
        rng = random.Random(8)
        for _ in range(400):
            self.check(rs(rng, rng.randint(0, 14), 'abc'))

    def test_scale(self):
        n = 50000
        rng = random.Random(9)
        for s in ('a' * n, rs(rng, n, 'ab'), ('abc' * n)[:n], ''.join(chr(32 + i % 95) for i in range(n))):
            t0 = time.time()
            r = A.suffix({'text': s})
            self.assertLess(time.time() - t0, 15)
            sa = r['sa']
            self.assertEqual(sorted(sa), list(range(n)))
            for i in range(1, n, 997):                    # spot-check order and lcp directly
                k = 0
                while k < 60 and sa[i - 1] + k < n and sa[i] + k < n and s[sa[i - 1] + k] == s[sa[i] + k]:
                    k += 1
                self.assertEqual(min(r['lcp'][i], 60), k)
            self.assertEqual(r['lcp'][0], 0)
        self.assertEqual(len(A.suffix({'text': 'a' * n})['repeated']), n - 1)


class TestAho(unittest.TestCase):
    def test_fixed(self):
        self.assertEqual(A.aho({'patterns': ['he', 'she', 'he'], 'texts': ['sheshe', 'sheshe', '']}),
                         {'counts': [[2, 2, 2], [2, 2, 2], [0, 0, 0]]})
        self.assertEqual(A.aho({'patterns': [], 'texts': ['abc', '']}), {'counts': [[], []]})
        self.assertEqual(A.aho({'patterns': ['a'], 'texts': []}), {'counts': []})
        self.assertEqual(A.aho({'patterns': [], 'texts': []}), {'counts': []})
        self.assertEqual(A.aho({'patterns': ['a', 'aa', 'aaa'], 'texts': ['aaaa']}),
                         {'counts': [[4, 3, 2]]})                    # overlaps + suffix patterns

    def test_random_vs_brute(self):
        rng = random.Random(10)
        for _ in range(300):
            pats = [rs(rng, rng.randint(1, 4), 'ab') for _ in range(rng.randint(0, 6))]
            texts = [rs(rng, rng.randint(0, 12), 'ab') for _ in range(rng.randint(0, 4))]
            self.assertEqual(A.aho({'patterns': pats, 'texts': texts})['counts'], aho_brute(pats, texts))

    def test_state_independent_between_requests(self):
        req = {'patterns': ['ab', 'b'], 'texts': ['abab']}
        self.assertEqual(A.aho(req), A.aho(req))
        A.aho({'patterns': ['zzz'], 'texts': ['zzzzzz']})
        self.assertEqual(A.aho(req), {'counts': [[2, 2]]})

    def test_scale_dense_and_many_patterns(self):
        pats = ['a' * k for k in range(1, 447)]                      # total length ~ 99681 <= 100000
        text = 'a' * 2000
        texts = [text] * 100                                          # total text length 200000
        t0 = time.time()
        res = A.aho({'patterns': pats, 'texts': texts})['counts']
        self.assertLess(time.time() - t0, 15)
        row = [max(0, 2000 - k + 1) for k in range(1, 447)]
        self.assertTrue(all(r == row for r in res))
        rng = random.Random(11)
        pats = [rs(rng, 10, 'abcdefgh') for _ in range(10000)]       # 10000 patterns, 100000 chars
        texts = [rs(rng, 2000, 'abcdefgh') for _ in range(100)]
        t0 = time.time()
        res = A.aho({'patterns': pats, 'texts': texts})['counts']
        self.assertLess(time.time() - t0, 15)
        for ti in (0, 57):
            for pi in (0, 1, 9999):
                self.assertEqual(res[ti][pi], len(find_all(texts[ti], pats[pi])))


class TestJsonLinesProcess(unittest.TestCase):
    def test_mixed_batch_in_one_process(self):
        reqs = [{'task': 'ping'},
                {'task': 'aho', 'patterns': ['ab'], 'texts': ['abab']},
                {'task': 'lcs', 'a': 'abc', 'b': 'ac'},
                {'task': 'suffix', 'text': 'banana'},
                {'task': 'aho', 'patterns': ['ab'], 'texts': ['abab']},
                {'task': 'tree', 'n': 2, 'weights': [1, 2], 'edges': [[0, 1]]},
                {'task': 'rk', 'text': 'abdj', 'pattern': 'ab'},
                {'task': 'merge', 'sizes': [2, 3, 4]},
                {'task': 'kmp', 'text': 'aaa', 'pattern': ''},
                {'task': 'naive', 'text': 'aaa', 'pattern': 'aa'},
                {'task': 'ping'}]
        data = ''.join(json.dumps(r) + '\n' for r in reqs)
        p = subprocess.run([sys.executable, os.path.join(SRC, 'main.py')], input=data,
                           capture_output=True, text=True, timeout=60)
        self.assertEqual(p.returncode, 0, p.stderr)
        out = [json.loads(x) for x in p.stdout.splitlines()]
        self.assertEqual(len(out), len(reqs))
        self.assertEqual(out[0], {'status': 'ready'})
        self.assertEqual(out[1], out[4])
        self.assertEqual(out[1], {'counts': [[2]]})
        self.assertEqual(out[2]['length'], 2)
        self.assertEqual(out[5]['weight'], 2)
        self.assertEqual(out[6], {'positions': [0]})
        self.assertEqual(out[8], {'positions': [0, 1, 2, 3]})
        self.assertEqual(out[9], {'positions': [0, 1]})


if __name__ == '__main__':
    unittest.main()
