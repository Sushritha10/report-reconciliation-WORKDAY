# Report Reconciliation and Regression Testing Framework

When two versions of the same report disagree, this tells you **why** — separating hierarchy differences from value differences, and value differences from transaction routing.

Built after investigating a real discrepancy in a Workday FY25 Budget vs Actual report, where the reported problem ("33 cost centers vs 32") turned out not to be the actual problem.

---

## The problem it solves

Someone extracts a report. It doesn't match the standard extract. The usual response is to eyeball two spreadsheets, spot the first difference, and stop there.

That first difference is often not the real one. In the case this was built from:

- The apparent issue was a **count mismatch** — 33 cost centers in one extract, 32 in the standard hierarchy
- That difference was one cost center, deliberately added to widen coverage. Not a defect.
- The actual issue was underneath: **the same cost centers returned different values**, because certain payroll transactions were routing to alternative cost centers — deflating one extract and inflating the other

Two different classes of problem, and only the second one needed fixing. A tool that stops at the count difference reports the wrong answer confidently.

## What it does

**1 — Hierarchy reconciliation.** Diffs two versions of an org or cost center hierarchy. Reports members added, removed, and re-parented, separately from anything about values.

**2 — Value reconciliation.** For members present in both, compares values and classifies each difference: rounding, sign, magnitude, or missing period.

**3 — Transaction attribution.** For material value differences, traces to transaction level and groups by routing destination — which is what surfaces a "payroll posting to the wrong cost center" pattern rather than leaving it as an unexplained variance.

**4 — Regression testing.** Snapshots report output before a configuration change, reruns after, and diffs result sets. Intended for release cycles where you need to know what a system update moved before users find out.

## Why it's structured this way

The design point is that **each check must fail independently**. If hierarchy and value differences are reported together, a structural change masks a data problem. Keeping them separate is what turned a vague "the reports don't match" into two specific findings, only one of which was a defect.

## Stack

`Python` · `pandas` · `SQL` · `pytest` · synthetic hierarchy and transaction generator

## Repo layout

```
src/
  hierarchy.py     structural diff: added, removed, re-parented
  values.py        value diff with difference classification
  attribute.py     transaction-level attribution for material variances
  regression.py    before/after snapshot comparison
  report.py        findings summary
data/
  generate.py      synthetic hierarchies and transactions
tests/
```

## Running it

```bash
pip install -r requirements.txt
python -m data.generate --cost-centers 32 --periods 12 --inject-routing-error
python -m src.report --baseline data/baseline.csv --extract data/extract.csv
```

Output separates structural findings from value findings, and attributes material variances to their transaction source.

## Notes

Built on synthetic data. The methodology is ERP-agnostic — it was developed against Workday reporting but the reconciliation logic applies to any system where a hierarchy drives report aggregation.
