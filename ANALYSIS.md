# Assignment 4 — analysis

## Environment and commands

* Language: **Python 3.13.17** (the assignment requires 3.12+; GitHub Actions uses 3.12). Standard library only, no recursion in any algorithm.
* OS/CPU/RAM used for tests and measurements: Linux 6.18 x86_64, Intel Xeon @ 2.10 GHz, 2 vCPU, 8 GB RAM (shared cloud sandbox, so absolute times are noisy).
* Build: none (interpreted). Launcher check: `python tools/run.py --setup`
* Public checks (44 cases + repeated mixed batch): `python tools/run.py --check` → **all PASS** (44/44 and the state-reset batch).
* Own tests: `python -m unittest discover -s tests/student -v` → **26 tests, OK** (about 2.6 s).
* Search comparison: `python tests/student/bench_search.py` (raw output saved in `tests/student/bench_results.md`).
* Run any request file: `python tools/run.py --input examples/lcs.jsonl`.
* Code: `Python/source/algorithms.py` (all eight commands), `Python/source/main.py` (supplied JSON Lines launcher, unchanged). Every command is a pure function of its request; no module-level mutable state, so consecutive requests are independent.

## Algorithm explanations

Notation: n, m are input sizes; z is the number of reported starts. Python integers are arbitrary precision, so sums up to 2·10^14 and counts are exact.

### lcs
* **State.** `dp[i][j]` = length of an LCS of the prefixes `a[:i]` and `b[:j]` (`i` characters of a, `j` of b).
* **Base cases.** `dp[0][j] = dp[i][0] = 0` (an empty prefix has only the empty subsequence). If either input is empty the function returns `length=0, sequence=""` directly.
* **Transition.** If `a[i-1] == b[j-1]` then `dp[i][j] = dp[i-1][j-1] + 1`, otherwise `max(dp[i-1][j], dp[i][j-1])`.
* **Order.** Rows in increasing `i`, columns in increasing `j`: all three needed cells (up, left, diagonal) are computed earlier.
* **Correctness.** Matching characters can always be taken in some optimum (exchange argument: any optimum that ignores a matching last pair can be rewritten to use it). On mismatch at least one of the two last characters is unused, so the optimum is the better of dropping either.
* **Reconstruction / ties.** Walk from `(n, m)`: on equal characters take the character and move diagonally; otherwise move to the neighbour with the larger value (up on ties). The collected characters are reversed. Any optimal sequence is valid; ties only choose among them.
* **Complexity.** O((n+1)(m+1)) time and memory (n·m ≤ 10^6); output is O(length).
* **Boundary test.** `tea_time` / `team` must give 4 (a subsequence, not substring; a substring-only implementation returns 3). Empty inputs and `ab`/`ba` (two different optimal answers) are also tested.

### merge (interval DP)
* **State.** `cost[l][r]` = minimum total cost of merging original blocks `l..r` into one block (`l ≤ r`); `split[l][r]` = the `k` of the **last** merge, i.e. the final merge joins `[l,k]` and `[k+1,r]`.
* **Base cases.** `cost[i][i] = 0`; for `n ≤ 1` return `cost=0, plan=[]`.
* **Transition.** `cost[l][r] = min over l ≤ k < r of cost[l][k] + cost[k+1][r] + (sum of sizes l..r)`, using prefix sums so the merge price is O(1).
* **Order.** Increasing interval length: both sub-intervals are shorter, hence already computed.
* **Correctness.** The last merge of any plan for `l..r` splits it into two adjacent intervals that were built independently, and the final price is the whole sum regardless of the split, so optimal substructure holds. Merging only adjacent blocks is exactly the restriction that makes the intervals contiguous (a greedy "two smallest blocks" is not allowed and not used).
* **Reconstruction.** Explicit stack, post-order: push `(l,r,done=False)`; expand to children `(l,k)`, `(k+1,r)` first, and emit `[l,k,r]` only when the node is popped again with `done=True`. Hence both children are merged before their parent (chronological plan with exactly n−1 merges). Ties pick the first minimal `k`; any optimal plan is accepted.
* **Complexity.** O(n^3) time, O(n^2) auxiliary memory (n ≤ 200); O(1) for n ≤ 1; the plan has n−1 entries.
* **Boundary test.** `[1,100,1]` must cost 101+102 = 203 (merging the two 1s first would violate adjacency); 200 blocks of 10^9 exceed 2^40 (64-bit safety); plans are validated by simulating them on a block set.

### tree (maximum-weight independent set)
* **State.** `take[v]` = best weight inside the subtree of `v` if `v` is selected; `skip[v]` = best if `v` is not selected.
* **Base / transition.** Initially `take[v] = weights[v]`, `skip[v] = 0`. For each child `c` of `v`: `take[v] += skip[c]`, `skip[v] += max(take[c], skip[c])`. Answer `max(take[root], skip[root])`; the empty set is allowed so negative weights never force a selection (`skip ≥ 0`).
* **Order.** BFS from vertex 0 gives an order where parents precede children; processing it in reverse is a post-order (children finish first). No recursion, so a 100 000-vertex chain is safe. The root choice does not change the optimum (tested by relabelling vertices).
* **Correctness.** Subtrees of different children are independent once the state of `v` is fixed: a selected `v` forces every child to be skipped; a skipped `v` lets every child choose freely.
* **Reconstruction.** Top-down in BFS order: a vertex that is not blocked by a selected parent is selected iff `take[v] > skip[v]`; selecting it blocks its children. This yields a valid independent set whose weight equals the DP optimum (ties → skip).
* **Complexity.** O(n+1) time and auxiliary memory (adjacency lists, 5 arrays); O(1) for n = 0.
* **Boundary test.** All-negative weights → 0 with empty selection; chain of 10^5 vertices with weights 10^9 → 5·10^13 (64-bit sum, no stack overflow); star with a slightly heavier centre; zero weights/ties; brute-force comparison on 300 random trees.

### naive
* Compare the pattern at every start `i = 0..n−m` character by character, stop at the first mismatch; report `i` when all `m` characters match. Overlaps are reported because the next start is always `i+1`.
* **Edge cases.** `m = 0` → all boundaries `0..n` (n+1 starts, including the final boundary); `m > n` → loop is empty → `[]`.
* **Correctness.** Every possible start is examined exactly once and verified by direct comparison; positions are produced in increasing order.
* **Complexity.** O(n·m + n + 1) time (worst case `aaa…a` vs `aa…ab`), O(1) auxiliary memory, O(z+1) output.
* **Boundary test.** `aaaaa`/`aaa` → `[0,1,2]` (last valid start `n−m` must be included; a loop to `n−m` exclusive would lose it).

### kmp
* **State.** `pi[i]` = length of the longest proper border of `p[:i+1]` (a prefix that is also a suffix, shorter than the string itself). `k` = number of pattern characters currently matched.
* **Prefix function.** For `i = 1..m−1`: while `k > 0` and `p[i] != p[k]` do `k = pi[k−1]`; if equal `k += 1`; `pi[i] = k`.
* **Search.** For each text character: on mismatch fall back `k = pi[k−1]` until a match or `k = 0`; on match `k += 1`. When `k == m` report `i−m+1` and set `k = pi[m−1]` (fallback **after a full match**), which keeps overlapping occurrences.
* **Correctness.** Invariant: after processing `t[i]`, `k` is the length of the longest prefix of `p` that is a suffix of `t[:i+1]`. Border fallback visits exactly the shorter candidates in decreasing order.
* **Empty pattern.** Returned before any pattern indexing: `0..n`.
* **Complexity.** O(n + m + z + 1) time (the amortised pointer argument: `k` increases at most once per character and every fallback decreases it), O(m+1) auxiliary memory, O(z+1) output.
* **Boundary test.** `abababa`/`aba` → `[0,2,4]` (missing the fallback after a full match would give `[0,4]`); 200 000 × 100 000 all-`a` input finishes in well under a second.

### rk (exact Rabin–Karp)
* **Hash.** Polynomial hash with base 31, modulus 101, ASCII codes, highest power on the leftmost character: `h(s) = Σ ord(s[i])·31^(m−1−i) mod 101`.
* **Rolling update.** `h' = ((h − ord(t[i])·31^(m−1))·31 + ord(t[i+m])) mod 101`. The intermediate value can be negative; Python's `%` already returns a non-negative result (in C-like languages `((x % M) + M) % M` would be needed).
* **Collision handling.** Equal hash only makes the window a *candidate*; the window is compared with the pattern character by character (the slice comparison `t[i:i+m] == p` is an equality test, not a search function) and reported only if equal. With such a small modulus collisions are common: `ab` and `dj` both hash to 75.
* **Edge cases.** `m = 0` → `0..n`; `m > n` → `[]`, both before any window is formed.
* **Correctness.** The hash is a function of the window, so a true match always has equal hashes (no match is missed); verification removes false positives.
* **Complexity.** O(n + m + c·m) time where `c` is the number of equal-hash candidate windows; worst case O(n·m + n + m + 1) (e.g. `aaaa…` pattern and text: every window is a true match and is verified). It is **not** linear in the worst case. O(1) auxiliary memory besides the output.
* **Boundary tests.** `abdj`/`ab` → `[0]` (the `dj` window collides but must be rejected); `djdjab`/`ab`; negative-remainder cases (`z…z a…a`); 10 000 × 2 000 all-`a` (every window is a verified candidate, n·m = 2·10^7).

### suffix (prefix doubling + Kasai)
* **Prefix doubling.** `rank[i]` after round `k` orders suffixes by their first `2k` characters. Round: key of suffix `i` is the pair `(rank[i], rank[i+k])` where a missing second part (suffix shorter than `k`) counts as smaller than any rank; I pack the pair into one integer `(rank[i]+1)·(n+200) + (rank[i+k]+1 or 0)` and sort indices by it (Python `sort`, O(n log n) per round). Ranks are recomputed by comparing neighbouring keys; the loop stops when all ranks are distinct. Initial ranks are the character codes (round 0 = first character). At most ⌈log2 n⌉+1 rounds ⇒ **O(n log² n)** time; the radix-sort variant would give O(n log n), which is not required.
* **Correctness.** Two suffixes with equal first `k` characters are ordered by the first `k` characters of the suffixes that start `k` later; since those ranks already order `k`-prefixes, the pair order is the `2k`-prefix order. No sentinel is added: the "missing = smallest" rule gives the shorter suffix first, which is the lexicographic order (a prefix sorts before its extensions).
* **Kasai.** `lcp[rank[i]]` = common prefix length of suffix `i` and its predecessor `sa[rank[i]−1]`; process `i` in text order and keep `h`. Reuse: if suffix `i` has LCP `h` with its predecessor `j`, then suffix `i+1` has LCP at least `h−1` with `j+1`, which precedes it in `sa`, so `h` is decremented by one instead of restarted. `h` only increases by character comparisons and decreases at most n times in total ⇒ O(n). `lcp[0] = 0`.
* **Repeated substring.** The longest substring occurring at two distinct starts equals `max(lcp)`: any repeat is a common prefix of two suffixes, and common prefixes of two suffixes are bounded by the minimum of the adjacent LCPs between them, hence by the maximum adjacent value. The answer is `text[sa[i]: sa[i]+lcp[i]]` for an index `i` with maximal `lcp`; overlaps are allowed (`banana` → `ana`). If `max(lcp) = 0` the result is `""`.
* **Complexity.** O(n log² (n+1)) time, O(n+1) auxiliary and output memory; suffix strings are never materialised (only one slice for the answer). Empty text: `sa=[]`, `lcp=[]`, `repeated=""` in O(1).
* **Boundary tests.** `banana`; `aaaa` (sa = `[3,2,1,0]`, repeated `aaa`); all-distinct text (repeated empty); one character; random strings compared with a brute-force `sorted(range(n), key=lambda i: s[i:])` and direct LCP; 50 000-character inputs (all equal, random, periodic, all 95 printable characters).

### aho (Aho–Corasick)
* **Trie.** One trie per request; node 0 is the root; children are stored per node in a dictionary keyed by the character. `term[i]` is the node where pattern `i` ends, so **duplicate patterns share a terminal state and remain separate dictionary positions**.
* **Failure links.** BFS from the root: for a child `u` of `v` by character `c`, `fail[u]` is found by following `fail[v], fail[fail[v]], …` until a node with a `c`-child exists (root children have `fail = 0`). Processing in BFS order guarantees shallower links are already known.
* **Query.** Per text, start with fresh `cnt = [0]*S` and state 0. For each character follow failure links until a `c`-edge exists (amortised O(|text|) per text), move, and do `cnt[state] += 1` (visit count).
* **Suffix-pattern counts by reverse-failure propagation.** After the text, process states in reverse BFS order (deepest first) and add `cnt[v]` to `cnt[fail[v]]`. A state's final value is then the number of times the string of that state ended at some text position, i.e. its visits **plus** all visits of states for which it is a proper suffix. Dictionary position `i` receives `cnt[term[i]]`; patterns that are suffixes of other patterns (`he` inside `she`) are therefore counted, overlaps are counted, and duplicates get equal values. No per-match list is built (dense inputs such as `a, aa, aaa, …` over `aaaa…` stay fast).
* **Reset.** `cnt` and the automaton state are created per text; the automaton itself is built per request, so nothing survives between requests or texts.
* **Output.** One row per text in `texts` order, one column per original dictionary position; empty dictionary → one empty row per text; no texts → `[]`; empty text → a row of zeros.
* **Complexity.** Build O(L + S + p) with dictionary children (the 95-letter table variant is O(L + 95·S + p) time and memory); per text O(|text| + S + p) for the propagation and readout (failure-link walking is amortised O(|text|)). Memory O(S + p) plus the O(q·p) output. L ≤ 10^5, S ≤ L+1.
* **Boundary tests.** the sample `he/she/he` over `sheshe`; `a, aa, aaa` over `aaaa` → `[4,3,2]`; repeated identical requests with an unrelated request between them; 446 patterns `a^k` × 100 texts of 2 000 characters (dense matches); 10 000 random patterns × 100 texts (200 000 characters in total), cross-checked on sampled counts.

## Own tests

All tests live in `tests/student/test_student.py`. Small inputs are checked against independently written oracles (brute-force subsets, exhaustive merge orders over *any* adjacent pair, `str.find` loops, `sorted(..., key=suffix)`), witnesses are checked for validity (so alternative optimal answers pass), and the full published domains are exercised. Results below are the actual results of the final run.

|Command|Input or fixture path|Expected result|Actual result / log|What it checks|
|---|---|---|---|---|
|`python tools/run.py --check`|`tests/public.json` (44 cases) + 2 batches in one process|all PASS|44/44 PASS + `PASS state reset: two complete batches in one process`|supplied examples, edge cases, stale state|
|`python -m unittest discover -s tests/student -v`|`TestLCS` (5 tests)|optimum length = brute force; witness is a subsequence of both strings|OK|empty inputs, subsequence ≠ substring, alternative optima, 1000×1000 scale|
|same|`TestMerge` (5 tests)|cost = exhaustive minimum; plan simulated as valid chronological merges|OK|n = 0/1, zeros, ties, `[1,100,1]` adjacency, n = 200 with 10^9 (64-bit)|
|same|`TestTree` (3 tests)|weight = subset brute force; selection independent and sums to weight; relabelling gives same optimum|OK|empty tree, one vertex, all negative, zeros, chain 10^5, star, large sum|
|same|`TestSearch` (5 tests)|naive = kmp = rk = `str.find` loop|OK|empty pattern/text, pattern longer, case/punctuation/spaces, overlaps, `ab`/`dj` collision, negative remainder, 200 000×100 000 KMP, 10 000×2 000 RK worst case|
|same|`TestSuffix` (3 tests)|sa = `sorted(key=suffix)`; lcp direct; repeated length = brute-force longest repeat|OK|empty, one char, all equal, all distinct, banana, tied repeats, 4 inputs of 50 000 chars|
|same|`TestAho` (4 tests)|counts = per-pattern `find` counts|OK|empty dictionary/texts/text, duplicates, suffix patterns, overlaps, independence of requests, dense 446×100 and 10 000 patterns|
|same|`TestJsonLinesProcess` (1 test)|`main.py` fed 11 mixed requests in one process|OK (one result per line, stderr empty)|state reset across tasks, `ping`, JSON Lines transport|
|total|26 tests|OK|`Ran 26 tests ... OK` (≈2.6 s)||

## Search comparison

* **Inputs.** The same `(text, pattern)` pair is given to naive, KMP and RK (common domain n, m ≤ 3000). Three increasing sizes `(n, m)` = (500, 50), (1500, 150), (3000, 300); two cases measured separately.
  * *random*: text of n random letters from `abcd`, pattern = a random slice of the text (so at least one occurrence), generator `random.Random(4242 + n)`.
  * *repetitive*: text `a^n`, pattern `a^(m−1)b` (many long partial matches, no occurrence).
* **Correctness first.** For every input the script asserts that the three position lists are identical before any time is reported (random: 1 start; repetitive: 0 starts).
* **Timing scope.** One call of `algorithms.naive/kmp/rk(request)` measured with `time.perf_counter()`; includes pattern preprocessing (prefix function, hash set-up) and result construction; excludes input generation, JSON parsing, output and process start-up. No compilation exists in Python. **Warm-up:** one untimed call per algorithm and input. **Runs:** 5 timed runs per algorithm/size/case; unit **milliseconds**; median reported.
* **Commands/environment.** `python tests/student/bench_search.py` on CPython 3.13.17, Linux x86_64, Intel Xeon 2.10 GHz, 2 vCPU shared sandbox.

Raw output header: `python 3.13.17 | Linux-6.18.44-fc-v310-x86_64-with-glibc2.39 | x86_64`; `seed=4242 runs=5 warm-up=1 timer=perf_counter unit=milliseconds`

|Case|n|m|Seed/generator|Algorithm|Run 1|Run 2|Run 3|Run 4|Run 5|Median|Correct outputs checked|
|---|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---|
|random|500|50|random.Random(4242+500) random|naive|0.056|0.056|0.044|0.060|0.042|0.056|yes, 1 starts, equal across 3|
|random|500|50|random.Random(4242+500) random|kmp|0.042|0.039|0.062|0.044|0.038|0.042|yes, 1 starts, equal across 3|
|random|500|50|random.Random(4242+500) random|rk|0.072|0.070|0.068|0.068|0.072|0.070|yes, 1 starts, equal across 3|
|random|1500|150|random.Random(4242+1500) random|naive|0.135|0.130|0.137|0.130|0.131|0.131|yes, 1 starts, equal across 3|
|random|1500|150|random.Random(4242+1500) random|kmp|0.152|0.118|0.115|0.119|0.115|0.118|yes, 1 starts, equal across 3|
|random|1500|150|random.Random(4242+1500) random|rk|0.249|0.211|0.213|0.209|0.225|0.213|yes, 1 starts, equal across 3|
|random|3000|300|random.Random(4242+3000) random|naive|0.274|0.362|0.329|0.268|0.283|0.283|yes, 1 starts, equal across 3|
|random|3000|300|random.Random(4242+3000) random|kmp|0.271|0.263|0.245|0.261|0.239|0.261|yes, 1 starts, equal across 3|
|random|3000|300|random.Random(4242+3000) random|rk|0.481|0.429|0.433|0.456|0.425|0.433|yes, 1 starts, equal across 3|
|repetitive|500|50|random.Random(4242+500) repetitive|naive|1.059|1.357|1.240|1.059|1.032|1.059|yes, 0 starts, equal across 3|
|repetitive|500|50|random.Random(4242+500) repetitive|kmp|0.060|0.068|0.058|0.097|0.058|0.060|yes, 0 starts, equal across 3|
|repetitive|500|50|random.Random(4242+500) repetitive|rk|0.071|0.071|0.073|0.073|0.071|0.071|yes, 0 starts, equal across 3|
|repetitive|1500|150|random.Random(4242+1500) repetitive|naive|9.660|9.957|9.517|10.815|9.863|9.863|yes, 0 starts, equal across 3|
|repetitive|1500|150|random.Random(4242+1500) repetitive|kmp|0.177|0.182|0.192|0.182|0.181|0.182|yes, 0 starts, equal across 3|
|repetitive|1500|150|random.Random(4242+1500) repetitive|rk|0.231|0.234|0.221|0.220|0.218|0.221|yes, 0 starts, equal across 3|
|repetitive|3000|300|random.Random(4242+3000) repetitive|naive|50.497|40.273|41.212|43.797|42.621|42.621|yes, 0 starts, equal across 3|
|repetitive|3000|300|random.Random(4242+3000) repetitive|kmp|0.976|0.413|0.379|0.442|0.378|0.413|yes, 0 starts, equal across 3|
|repetitive|3000|300|random.Random(4242+3000) repetitive|rk|0.471|0.479|2.009|0.479|0.498|0.479|yes, 0 starts, equal across 3|

**Observations (not a proof of asymptotics).**
* On *random* text all three are fast and close together: naive almost always fails at the first or second character, so its practical cost is about O(n); KMP is similar; RK is the slowest here because it pays a hash update per window (about 1.6× KMP).
* On *repetitive* text naive grows roughly quadratically with m (≈1.1 ms → 9.9 ms → 42.6 ms when n and m grow 3× and 2× per step), while KMP (0.06 → 0.18 → 0.41 ms) and RK (0.07 → 0.22 → 0.48 ms) stay almost linear in n. This is consistent with O(n·m) versus O(n+m), but three sizes on one noisy machine do not prove it.
* **RK and the small modulus.** With modulus 101 about 1 window in 101 collides by chance, and on repetitive text equal windows are also equal in hash, so the number of candidates `c` can be large and each candidate costs up to `m` character comparisons: the bound is O(n + m + c·m), up to O(n·m). In the measured *repetitive* case the pattern ends with `b`, so candidates are rare and rejected after a short comparison, which is why RK looks linear there; the all-`a` text/pattern (tested for correctness in `TestSearch.test_scale`, 10 000 × 2 000) is the quadratic case. These conclusions apply to this deliberately tiny modulus and must not be generalised to production hash implementations with large moduli. The known collision `ab`/`dj` (both 75) is a permanent correctness test.
* One outlier visible in the tables (e.g. KMP 0.976 ms in the first repetitive 3000 run, RK 2.009 ms) is a scheduling spike of the shared machine, which is why the median over five runs is reported.

## Sources and AI assistance

* **Sources:** the assignment specification and `docs/guide/CONTRACTS.md`, the Week 8 lecture material in the repository (`docs/week8`, `docs/LECTURE_CLARIFICATIONS_EN_RU.md`), and the standard textbook descriptions of LCS, interval DP, tree DP, KMP, Rabin–Karp, prefix doubling with Kasai's algorithm and Aho–Corasick (e.g. Cormen, Leiserson, Rivest, Stein, *Introduction to Algorithms*).
* **AI assistance:** the implementation in `Python/source/algorithms.py`, the tests in `tests/student/`, the benchmark script and this analysis were drafted with Claude (Anthropic's assistant). Claude also ran the public checks (44/44 PASS), the 26 own tests and the benchmark in a Linux sandbox; the numbers above are from those runs.
* **My own verification:** *[EDIT BEFORE SUBMITTING: write what you personally did — e.g. "I re-ran `python tools/run.py --check` and the unit tests on my computer, read each algorithm, traced `banana`, `tea_time`, `he/she/he` by hand, and confirmed that I can explain every part."]*
