"""Transaction-level attribution for material variances.

Turns "these two numbers differ" into "these transactions posted somewhere other
than expected" — which is an actionable finding rather than an open question.
"""
from collections import defaultdict


def attribute_variance(transactions, member):
    """transactions: iterable of dicts with keys
       {id, amount, posted_cost_center, expected_cost_center, source}

    Returns transactions expected at `member` that landed elsewhere, grouped by
    where they actually posted.
    """
    misrouted = defaultdict(list)
    for t in transactions:
        if t.get("expected_cost_center") == member and t["posted_cost_center"] != member:
            misrouted[t["posted_cost_center"]].append(t)
    return dict(misrouted)


def routing_summary(misrouted: dict, member: str) -> str:
    if not misrouted:
        return f"{member}: no misrouted transactions. Variance originates elsewhere."
    lines = [f"{member}: transactions expected here posted elsewhere"]
    ordered = sorted(misrouted.items(), key=lambda kv: -sum(abs(t["amount"]) for t in kv[1]))
    for dest, txns in ordered:
        total = sum(t["amount"] for t in txns)
        sources = sorted({t.get("source", "unknown") for t in txns})
        lines.append(
            f"  -> {dest}: {len(txns)} txns, {total:,.2f}, source(s): {', '.join(sources)}"
        )
    return "\n".join(lines)
