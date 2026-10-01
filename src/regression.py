"""Before/after regression testing for configuration or release changes.

Snapshot report output, apply the change, rerun, diff. Intended for biannual
release cycles where you need to know what moved before users find out.
"""
import json, hashlib
from src.values import diff_values


def snapshot(rows, label):
    payload = sorted((m, p, round(v, 2)) for m, p, v in rows)
    digest = hashlib.sha256(json.dumps(payload).encode()).hexdigest()[:12]
    return {"label": label, "digest": digest, "rows": payload}


def compare_snapshots(before, after):
    diffs = diff_values(before["rows"], after["rows"])
    b_keys = {(m, p) for m, p, _ in before["rows"]}
    a_keys = {(m, p) for m, p, _ in after["rows"]}
    return {
        "identical": before["digest"] == after["digest"],
        "rows_added": sorted(a_keys - b_keys),
        "rows_dropped": sorted(b_keys - a_keys),
        "value_changes": diffs,
    }


def regression_report(result) -> str:
    if result["identical"]:
        return "PASS  Output identical before and after. No regression."
    lines = ["FAIL  Output changed."]
    if result["rows_dropped"]:
        lines.append(f"  {len(result['rows_dropped'])} rows dropped  <- usually the serious one")
    if result["rows_added"]:
        lines.append(f"  {len(result['rows_added'])} rows added")
    if result["value_changes"]:
        lines.append(f"  {len(result['value_changes'])} value changes")
        for d in result["value_changes"][:5]:
            lines.append(f"    {d.member} {d.period}: {d.baseline:,.2f} -> {d.extract:,.2f} ({d.classification})")
    lines.append("\nEvery change must be explained before release sign-off.")
    return "\n".join(lines)
