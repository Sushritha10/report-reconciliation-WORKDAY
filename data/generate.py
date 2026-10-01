"""Synthetic hierarchy + transaction generator.

--inject-routing-error reproduces the failure mode this framework was built for:
same membership, different values, caused by transactions posting to an
alternative cost center.
"""
import argparse, csv, random

random.seed(42)


def build(n_cc=32, periods=12, inject=False, extra_member=True):
    centers = [f"CC{i:03d}" for i in range(1, n_cc + 1)]
    hierarchy = {c: "ALL_COST_CENTERS" for c in centers}

    # baseline hierarchy is the official master list
    baseline_h = dict(hierarchy)
    extract_h = dict(hierarchy)
    if extra_member:
        # a cost center deliberately added by the report author to widen coverage
        extract_h["CC_AUX01"] = "ALL_COST_CENTERS"

    baseline_v, extract_v, txns = [], [], []
    tid = 0
    for c in centers:
        for p in range(1, periods + 1):
            period = f"FY25-P{p:02d}"
            amount = round(random.uniform(5_000, 90_000), 2)
            baseline_v.append((c, period, amount))
            ext = amount
            if inject and c in centers[:3] and p % 3 == 0:
                # payroll routed to an alternative cost center
                moved = round(amount * 0.18, 2)
                ext = round(amount - moved, 2)
                tid += 1
                txns.append({
                    "id": f"T{tid:05d}", "amount": moved,
                    "expected_cost_center": c,
                    "posted_cost_center": "CC_AUX01",
                    "source": "payroll",
                })
            extract_v.append((c, period, ext))
    return baseline_h, extract_h, baseline_v, extract_v, txns


def write(path, rows, header):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cost-centers", type=int, default=32)
    ap.add_argument("--periods", type=int, default=12)
    ap.add_argument("--inject-routing-error", action="store_true")
    a = ap.parse_args()
    bh, eh, bv, ev, tx = build(a.cost_centers, a.periods, a.inject_routing_error)
    write("data/baseline.csv", bv, ["member", "period", "value"])
    write("data/extract.csv", ev, ["member", "period", "value"])
    write("data/hierarchy_baseline.csv", bh.items(), ["member", "parent"])
    write("data/hierarchy_extract.csv", eh.items(), ["member", "parent"])
    write("data/transactions.csv",
          [(t["id"], t["amount"], t["expected_cost_center"], t["posted_cost_center"], t["source"]) for t in tx],
          ["id", "amount", "expected_cost_center", "posted_cost_center", "source"])
    print(f"generated: {len(bv)} baseline rows, {len(ev)} extract rows, {len(tx)} misrouted txns")
