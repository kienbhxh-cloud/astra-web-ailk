"""Bộ đếm |G_s| dạng đa thức trên Z[t] (co mạng tensor mức NHÓM, khử thành phần liên thông).

Tác giả gốc: Gemini, sản phẩm ASTRA-LO/GEMINI-PRODUCT-001 (20/11/2026), tệp
20261120_Gemini_ASTRA_LO_B_ETH_1_PolyTensor_and_Audit.py trên Drive. Trích nguyên văn lớp
GrammarRuleCounter và hàm đa thức; KTST nghiệm thu: 0 sai / 300 ngữ pháp ngẫu nhiên so với vét cạn,
khớp rule_count.count_rules_tensor ở F1-v0 s=1..7, chạy s=1..14 trong vài ms.
"""
import math
import time
from fractions import Fraction
from itertools import product


def poly_mul(a, b, max_deg=None):
    """Exact polynomial multiplication over Z[t] using arbitrary-precision ints."""
    la, lb = len(a), len(b)
    out_len = la + lb - 1
    if max_deg is not None:
        out_len = min(out_len, max_deg + 1)
    res = [0] * out_len
    for i, ai in enumerate(a):
        if ai == 0:
            continue
        limit = min(lb, out_len - i)
        for j in range(limit):
            res[i + j] += ai * b[j]
    while len(res) > 1 and res[-1] == 0:
        res.pop()
    return res


def poly_add(a, b):
    """Exact polynomial addition over Z[t]."""
    n = max(len(a), len(b))
    res = [0] * n
    for i in range(len(a)):
        res[i] += a[i]
    for i in range(len(b)):
        res[i] += b[i]
    while len(res) > 1 and res[-1] == 0:
        res.pop()
    return res


class GrammarRuleCounter:
    """
    Exact rule-space counter |G_s| over Z[t] via group-level factor graph
    contraction with connected-component decomposition and min-fill ordering.
    """
    def __init__(self, group_sizes, extra_exclusions=()):
        if not group_sizes or any((not isinstance(g, int)) or g <= 0 for g in group_sizes):
            raise ValueError("group_sizes must be a non-empty sequence of positive ints.")
        self.group_sizes = list(group_sizes)
        self.num_groups = len(self.group_sizes)
        self.num_features = sum(self.group_sizes)

        self.feat_to_group = {}
        idx = 0
        for g_id, g_sz in enumerate(self.group_sizes):
            for local_idx in range(1, g_sz + 1):
                self.feat_to_group[idx] = (g_id, local_idx)
                idx += 1

        self.forbidden_self = set()
        self.cross_pairs = set()
        for pair in extra_exclusions:
            if len(pair) != 2:
                raise ValueError(f"Invalid exclusion pair: {pair}")
            a, b = pair
            if not (isinstance(a, int) and isinstance(b, int)):
                raise TypeError(f"Feature indices must be ints, got {pair}")
            if not (0 <= a < self.num_features and 0 <= b < self.num_features):
                raise ValueError(
                    f"Exclusion index out of bounds [0, {self.num_features - 1}]: {pair}"
                )
            if a == b:
                self.forbidden_self.add(a)
            else:
                ga, la = self.feat_to_group[a]
                gb, lb = self.feat_to_group[b]
                if ga == gb:
                    continue
                if ga > gb:
                    ga, la, gb, lb = gb, lb, ga, la
                self.cross_pairs.add(((ga, la), (gb, lb)))

    def closed_form_poly(self, max_s=None):
        poly = [1]
        for g_id in range(self.num_groups):
            eff_sz = sum(
                1 for f_idx, (gid, _) in self.feat_to_group.items()
                if gid == g_id and f_idx not in self.forbidden_self
            )
            poly = poly_mul(poly, [1, eff_sz], max_deg=max_s)
        return poly

    def exact_generating_poly(self, max_s=None):
        t0 = time.perf_counter()
        if max_s is None:
            max_s = self.num_groups
        else:
            if not isinstance(max_s, int) or max_s < 1 or max_s > self.num_features:
                raise ValueError(f"max_s must be in [1, {self.num_features}], got {max_s}")
            max_s = min(max_s, self.num_groups)

        adj = {g: set() for g in range(self.num_groups)}
        pair_forbids = {}
        for (g1, l1), (g2, l2) in self.cross_pairs:
            adj[g1].add(g2)
            adj[g2].add(g1)
            pair_forbids.setdefault((g1, g2), set()).add((l1, l2))

        allowed_states = {}
        for g_id in range(self.num_groups):
            states = [0]
            for f_idx, (gid, l_idx) in self.feat_to_group.items():
                if gid == g_id and f_idx not in self.forbidden_self:
                    states.append(l_idx)
            allowed_states[g_id] = states

        visited = set()
        total_poly = [1]
        max_tensor_states = 1
        max_elim_width_groups = 1

        for g in range(self.num_groups):
            if g in visited:
                continue
            comp = []
            stack = [g]
            visited.add(g)
            while stack:
                u = stack.pop()
                comp.append(u)
                for nb in adj[u]:
                    if nb not in visited:
                        visited.add(nb)
                        stack.append(nb)
            comp.sort()

            if len(comp) == 1:
                u = comp[0]
                eff_sz = len(allowed_states[u]) - 1
                total_poly = poly_mul(total_poly, [1, eff_sz], max_deg=max_s)
                max_tensor_states = max(max_tensor_states, len(allowed_states[u]))
                continue

            tensors = []
            for u in comp:
                table = {
                    (st,): ([1] if st == 0 else [0, 1])
                    for st in allowed_states[u]
                }
                tensors.append(((u,), table))

            for (g1, g2), forb in pair_forbids.items():
                if g1 in comp and g2 in comp:
                    table = {}
                    for s1 in allowed_states[g1]:
                        for s2 in allowed_states[g2]:
                            if (s1, s2) not in forb:
                                table[(s1, s2)] = [1]
                    tensors.append(((g1, g2), table))

            remaining = set(comp)
            cur_adj = {u: set(adj[u]) for u in comp}

            while remaining:
                def elim_key(v):
                    nbs = list(cur_adj[v])
                    fill = 0
                    for i in range(len(nbs)):
                        for j in range(i + 1, len(nbs)):
                            if nbs[j] not in cur_adj[nbs[i]]:
                                fill += 1
                    state_cost = len(allowed_states[v])
                    for nb in nbs:
                        state_cost *= len(allowed_states[nb])
                    return (fill, state_cost, v)

                v = min(remaining, key=elim_key)
                remaining.remove(v)
                nbs = list(cur_adj[v])
                for i in range(len(nbs)):
                    cur_adj[nbs[i]].discard(v)
                    for j in range(i + 1, len(nbs)):
                        cur_adj[nbs[i]].add(nbs[j])
                        cur_adj[nbs[j]].add(nbs[i])

                involved = [t for t in tensors if v in t[0]]
                tensors = [t for t in tensors if v not in t[0]]
                all_vars = sorted({u for vars_t, _ in involved for u in vars_t})
                out_vars = tuple(u for u in all_vars if u != v)
                max_elim_width_groups = max(max_elim_width_groups, len(all_vars))
                prod_states = 1
                for u in all_vars:
                    prod_states *= len(allowed_states[u])
                max_tensor_states = max(max_tensor_states, prod_states)

                cur_vars, cur_table = involved[0]
                for nxt_vars, nxt_table in involved[1:]:
                    common = [u for u in nxt_vars if u in cur_vars]
                    cur_pos = {u: i for i, u in enumerate(cur_vars)}
                    nxt_pos = {u: i for i, u in enumerate(nxt_vars)}
                    extra_nxt = [u for u in nxt_vars if u not in cur_pos]
                    new_vars = cur_vars + tuple(extra_nxt)

                    index_nxt = {}
                    for k_nxt, p_nxt in nxt_table.items():
                        ck = tuple(k_nxt[nxt_pos[u]] for u in common)
                        ek = tuple(k_nxt[nxt_pos[u]] for u in extra_nxt)
                        index_nxt.setdefault(ck, []).append((ek, p_nxt))

                    new_table = {}
                    for k_cur, p_cur in cur_table.items():
                        ck = tuple(k_cur[cur_pos[u]] for u in common)
                        matches = index_nxt.get(ck)
                        if not matches:
                            continue
                        for ek, p_nxt in matches:
                            nk = k_cur + ek
                            prod_p = poly_mul(p_cur, p_nxt, max_deg=max_s)
                            if nk in new_table:
                                new_table[nk] = poly_add(new_table[nk], prod_p)
                            else:
                                new_table[nk] = prod_p
                    cur_vars, cur_table = new_vars, new_table

                rem_indices = [cur_vars.index(u) for u in out_vars]
                reduced = {}
                for k_full, p_val in cur_table.items():
                    k_out = tuple(k_full[i] for i in rem_indices)
                    if k_out in reduced:
                        reduced[k_out] = poly_add(reduced[k_out], p_val)
                    else:
                        reduced[k_out] = p_val
                tensors.append((out_vars, reduced))

            comp_poly = [1]
            for vars_t, table_t in tensors:
                assert vars_t == ()
                comp_poly = poly_mul(comp_poly, table_t.get((), [0]), max_deg=max_s)
            total_poly = poly_mul(total_poly, comp_poly, max_deg=max_s)

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        coeffs = list(total_poly) + [0] * max(0, (max_s + 1) - len(total_poly))
        return coeffs, {
            "elapsed_ms": round(elapsed_ms, 4),
            "max_elim_width_groups": max_elim_width_groups,
            "max_tensor_states": max_tensor_states,
            "equiv_binary_treewidth": round(math.log2(max_tensor_states), 3),
        }

    def count_rules(self, s):
        if not isinstance(s, int) or s < 1 or s > self.num_features:
            raise ValueError(f"s must be in [1, {self.num_features}], got {s}")
        coeffs, diag = self.exact_generating_poly(max_s=min(s, self.num_groups))
        return sum(coeffs[1:min(s, self.num_groups) + 1]), diag

    def brute_force_counts(self):
        allowed = []
        for g_id in range(self.num_groups):
            st = [0]
            for f_idx, (gid, l_idx) in self.feat_to_group.items():
                if gid == g_id and f_idx not in self.forbidden_self:
                    st.append(l_idx)
            allowed.append(st)
        counts_by_k = [0] * (self.num_groups + 1)
        for assign in product(*allowed):
            if all(not (assign[g1] == l1 and assign[g2] == l2) for (g1, l1), (g2, l2) in self.cross_pairs):
                counts_by_k[sum(1 for x in assign if x != 0)] += 1
        return counts_by_k


def count_rules_poly(group_sizes, s, extra_exclusions=()):
    p = GrammarRuleCounter(list(group_sizes), extra_exclusions).exact_generating_poly(max_s=min(s, len(group_sizes)))
    p = p[0] if isinstance(p, tuple) else p
    return sum(p[1:s + 1])
