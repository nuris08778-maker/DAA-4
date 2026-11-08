"""Assignment 4 algorithms. Every function is stateless (all working data is local),
iterative where depth can be large, and uses no built-in substring search."""
import sys


# ------------------------------------------------------------------ Part 1: LCS
def lcs(request):
    a, b = request['a'], request['b']
    n, m = len(a), len(b)
    if n == 0 or m == 0:
        return {'length': 0, 'sequence': ''}
    # dp[i][j] = LCS length of a[:i] and b[:j]; row/column 0 are the empty-prefix base cases.
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        prev, cur, ai = dp[i - 1], dp[i], a[i - 1]
        for j in range(1, m + 1):
            if ai == b[j - 1]:
                cur[j] = prev[j - 1] + 1
            else:
                up, left = prev[j], cur[j - 1]
                cur[j] = up if up >= left else left
    out = []
    i, j = n, m
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            out.append(a[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    out.reverse()
    return {'length': dp[n][m], 'sequence': ''.join(out)}


# ------------------------------------------------------------------ Part 2: merge (interval DP)
def merge(request):
    sizes = request['sizes']
    n = len(sizes)
    if n <= 1:
        return {'cost': 0, 'plan': []}
    pre = [0] * (n + 1)
    for i, s in enumerate(sizes):
        pre[i + 1] = pre[i] + s
    # cost[l][r] = minimal total cost of merging blocks l..r into one; split[l][r] = last left end k.
    cost = [[0] * n for _ in range(n)]
    split = [[0] * n for _ in range(n)]
    for length in range(2, n + 1):
        for l in range(0, n - length + 1):
            r = l + length - 1
            best, bk = None, l
            cl = cost[l]
            for k in range(l, r):
                v = cl[k] + cost[k + 1][r]
                if best is None or v < best:
                    best, bk = v, k
            cost[l][r] = best + pre[r + 1] - pre[l]
            split[l][r] = bk
    # Post-order (children before parent) with an explicit stack.
    plan = []
    stack = [(0, n - 1, False)]
    while stack:
        l, r, done = stack.pop()
        if l == r:
            continue
        k = split[l][r]
        if done:
            plan.append([l, k, r])
        else:
            stack.append((l, r, True))
            stack.append((k + 1, r, False))
            stack.append((l, k, False))
    return {'cost': cost[0][n - 1], 'plan': plan}


# ------------------------------------------------------------------ Part 3: tree MWIS
def tree(request):
    n = request['n']
    if n == 0:
        return {'weight': 0, 'selected': []}
    w = request['weights']
    adj = [[] for _ in range(n)]
    for u, v in request['edges']:
        adj[u].append(v)
        adj[v].append(u)
    parent = [-1] * n
    order = [0]
    seen = [False] * n
    seen[0] = True
    for u in order:                       # BFS order: parents precede children
        for v in adj[u]:
            if not seen[v]:
                seen[v] = True
                parent[v] = u
                order.append(v)
    take = list(w)                        # best weight in subtree if v is selected
    skip = [0] * n                        # best weight in subtree if v is not selected
    for v in reversed(order):             # children are finished before their parent
        p = parent[v]
        if p >= 0:
            take[p] += skip[v]
            skip[p] += take[v] if take[v] > skip[v] else skip[v]
    chosen = [False] * n
    blocked = [False] * n                 # parent selected -> v must be skipped
    selected = []
    for v in order:                       # top-down reconstruction
        if not blocked[v] and take[v] > skip[v]:
            chosen[v] = True
            selected.append(v)
            for c in adj[v]:
                if c != parent[v]:
                    blocked[c] = True
    return {'weight': max(take[0], skip[0]), 'selected': selected}


# ------------------------------------------------------------------ Part 4: exact search
def naive(request):
    t, p = request['text'], request['pattern']
    n, m = len(t), len(p)
    if m == 0:
        return {'positions': list(range(n + 1))}
    res = []
    for i in range(n - m + 1):
        j = 0
        while j < m and t[i + j] == p[j]:
            j += 1
        if j == m:
            res.append(i)
    return {'positions': res}


def kmp(request):
    t, p = request['text'], request['pattern']
    n, m = len(t), len(p)
    if m == 0:
        return {'positions': list(range(n + 1))}
    pi = [0] * m                          # pi[i] = longest proper border of p[:i+1]
    k = 0
    for i in range(1, m):
        while k and p[i] != p[k]:
            k = pi[k - 1]
        if p[i] == p[k]:
            k += 1
        pi[i] = k
    res = []
    k = 0
    for i in range(n):
        c = t[i]
        while k and c != p[k]:
            k = pi[k - 1]
        if c == p[k]:
            k += 1
        if k == m:
            res.append(i - m + 1)
            k = pi[k - 1]                 # fall back so overlapping starts are kept
    return {'positions': res}


def rk(request):
    t, p = request['text'], request['pattern']
    n, m = len(t), len(p)
    if m == 0:
        return {'positions': list(range(n + 1))}
    if m > n:
        return {'positions': []}
    B, MOD = 31, 101
    high = 1
    for _ in range(m - 1):
        high = high * B % MOD             # B^(m-1): weight of the leftmost character
    hp = ht = 0
    for i in range(m):
        hp = (hp * B + ord(p[i])) % MOD
        ht = (ht * B + ord(t[i])) % MOD
    res = []
    for i in range(n - m + 1):
        if hp == ht and t[i:i + m] == p:  # equal hash is only a candidate: verify characters
            res.append(i)
        if i + m < n:
            ht = ((ht - ord(t[i]) * high) * B + ord(t[i + m])) % MOD   # Python % is non-negative
    return {'positions': res}


# ------------------------------------------------------------------ Part 5: suffix array + Kasai
def suffix(request):
    s = request['text']
    n = len(s)
    if n == 0:
        return {'sa': [], 'lcp': [], 'repeated': ''}
    rank = [ord(c) for c in s]
    sa = list(range(n))
    k = 1
    while True:
        # sort by (rank[i], rank[i+k]) packed into one integer; missing second key = 0 < any rank+1
        r1 = [x + 1 for x in rank]
        key = [r1[i] * (n + 200) + (r1[i + k] if i + k < n else 0) for i in range(n)]
        sa.sort(key=key.__getitem__)
        new = [0] * n
        r = 0
        for idx in range(1, n):
            if key[sa[idx]] != key[sa[idx - 1]]:
                r += 1
            new[sa[idx]] = r
        rank = new
        if r == n - 1 or k >= n:
            break
        k <<= 1
    # Kasai: lcp[rank[i]] compares suffix i with its predecessor in sa
    lcp = [0] * n
    h = 0
    for i in range(n):
        ri = rank[i]
        if ri > 0:
            j = sa[ri - 1]
            while i + h < n and j + h < n and s[i + h] == s[j + h]:
                h += 1
            lcp[ri] = h
            if h:
                h -= 1
        else:
            h = 0
    best, pos = 0, 0
    for i in range(1, n):
        if lcp[i] > best:
            best, pos = lcp[i], sa[i]
    return {'sa': sa, 'lcp': lcp, 'repeated': s[pos:pos + best] if best else ''}


# ------------------------------------------------------------------ Part 6: Aho-Corasick
def aho(request):
    patterns, texts = request['patterns'], request['texts']
    p = len(patterns)
    child = [{}]
    term = [0] * p
    for idx, pat in enumerate(patterns):
        v = 0
        for c in pat:
            nxt = child[v].get(c)
            if nxt is None:
                nxt = len(child)
                child[v][c] = nxt
                child.append({})
            v = nxt
        term[idx] = v
    S = len(child)
    fail = [0] * S
    bfs = []
    for c, u in child[0].items():
        bfs.append(u)
    for v in bfs:                         # BFS: fail[v] is shallower and already known
        for c, u in child[v].items():
            f = fail[v]
            while f and c not in child[f]:
                f = fail[f]
            fu = child[f].get(c, 0)
            fail[u] = fu if fu != u else 0
            bfs.append(u)
    out = []
    for text in texts:
        cnt = [0] * S                     # fresh state for each independent text
        v = 0
        for c in text:
            while v and c not in child[v]:
                v = fail[v]
            v = child[v].get(c, 0)
            cnt[v] += 1
        for v in reversed(bfs):           # deepest first: push visits along failure links
            c = cnt[v]
            if c:
                cnt[fail[v]] += c
        out.append([cnt[term[i]] for i in range(p)])
    return {'counts': out}
