"""Value reconciliation for members present in both versions.

Classifies each difference so rounding noise does not compete for attention with
a material variance.
"""
from dataclasses import dataclass

ROUNDING_TOLERANCE = 0.01
MATERIALITY = 1000.0


@dataclass
class ValueDiff:
    member: str
    period: str
    baseline: float
    extract: float

    @property
    def delta(self) -> float:
        return self.extract - self.baseline

    @property
    def classification(self) -> str:
        d = abs(self.delta)
        if d <= ROUNDING_TOLERANCE:
            return "rounding"
        if self.baseline == 0 and self.extract != 0:
            return "missing_in_baseline"
        if self.extract == 0 and self.baseline != 0:
            return "missing_in_extract"
        if (self.baseline > 0) != (self.extract > 0):
            return "sign_flip"
        if d >= MATERIALITY:
            return "material"
        return "immaterial"


def diff_values(baseline_rows, extract_rows):
    """rows: iterable of (member, period, value). Only members in both are compared."""
    b = {(m, p): v for m, p, v in baseline_rows}
    e = {(m, p): v for m, p, v in extract_rows}
    out = []
    for key in sorted(set(b) & set(e)):
        if b[key] != e[key]:
            out.append(ValueDiff(key[0], key[1], b[key], e[key]))
    return [d for d in out if d.classification != "rounding"]


def material_members(diffs):
    """Members worth tracing to transaction level."""
    flagged = ("material", "sign_flip", "missing_in_baseline", "missing_in_extract")
    return sorted({d.member for d in diffs if d.classification in flagged})
