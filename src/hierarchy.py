"""Structural reconciliation between two hierarchy versions.

Reports ONLY structural differences. Value differences are handled separately in
values.py, because conflating the two is what lets a data defect hide behind a
structural change.
"""
from dataclasses import dataclass, field


@dataclass
class HierarchyDiff:
    added: list = field(default_factory=list)
    removed: list = field(default_factory=list)
    reparented: list = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return not (self.added or self.removed or self.reparented)

    def summary(self) -> str:
        if self.is_clean:
            return "Hierarchy: identical membership and parentage."
        lines = ["Hierarchy differences:"]
        for m in self.added:
            lines.append(f"  + {m} present in extract, absent from baseline")
        for m in self.removed:
            lines.append(f"  - {m} present in baseline, absent from extract")
        for m, old, new in self.reparented:
            lines.append(f"  ~ {m} re-parented: {old} -> {new}")
        lines.append(
            "\nStructural differences are not defects by default. A member added "
            "deliberately to widen coverage appears here. Confirm intent before escalating."
        )
        return "\n".join(lines)


def diff_hierarchy(baseline: dict, extract: dict) -> HierarchyDiff:
    """baseline / extract: {member_id: parent_id}"""
    b, e = set(baseline), set(extract)
    d = HierarchyDiff(added=sorted(e - b), removed=sorted(b - e))
    for m in sorted(b & e):
        if baseline[m] != extract[m]:
            d.reparented.append((m, baseline[m], extract[m]))
    return d
