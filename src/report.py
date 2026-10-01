"""End-to-end reconciliation: structure first, then values, then attribution."""
import argparse, csv
from src.hierarchy import diff_hierarchy
from src.values import diff_values, material_members
from src.attribute import attribute_variance, routing_summary


def load_pairs(path):
    with open(path) as f:
        return {r["member"]: r["parent"] for r in csv.DictReader(f)}


def load_values(path):
    with open(path) as f:
        return [(r["member"], r["period"], float(r["value"])) for r in csv.DictReader(f)]


def load_txns(path):
    with open(path) as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["amount"] = float(r["amount"])
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", default="data/baseline.csv")
    ap.add_argument("--extract", default="data/extract.csv")
    ap.add_argument("--hierarchy-baseline", default="data/hierarchy_baseline.csv")
    ap.add_argument("--hierarchy-extract", default="data/hierarchy_extract.csv")
    ap.add_argument("--transactions", default="data/transactions.csv")
    a = ap.parse_args()

    print("=" * 70)
    print("STEP 1  STRUCTURE")
    print("=" * 70)
    hd = diff_hierarchy(load_pairs(a.hierarchy_baseline), load_pairs(a.hierarchy_extract))
    print(hd.summary())

    print("\n" + "=" * 70)
    print("STEP 2  VALUES (members present in both)")
    print("=" * 70)
    vd = diff_values(load_values(a.baseline), load_values(a.extract))
    if not vd:
        print("No value differences beyond rounding.")
        return
    by_class = {}
    for d in vd:
        by_class.setdefault(d.classification, []).append(d)
    for cls, items in sorted(by_class.items()):
        total = sum(abs(i.delta) for i in items)
        print(f"  {cls:22s} {len(items):4d} differences, {total:>14,.2f} absolute")

    print("\n" + "=" * 70)
    print("STEP 3  ATTRIBUTION (material variances only)")
    print("=" * 70)
    txns = load_txns(a.transactions)
    for m in material_members(vd):
        print(routing_summary(attribute_variance(txns, m), m))


if __name__ == "__main__":
    main()
