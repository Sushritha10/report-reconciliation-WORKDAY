from src.hierarchy import diff_hierarchy
from src.values import diff_values, material_members
from src.attribute import attribute_variance


def test_identical_hierarchy_is_clean():
    h = {"CC001": "ALL", "CC002": "ALL"}
    assert diff_hierarchy(h, dict(h)).is_clean


def test_added_member_detected_without_flagging_values():
    b = {"CC001": "ALL"}
    e = {"CC001": "ALL", "CC_SUMMER": "ALL"}
    d = diff_hierarchy(b, e)
    assert d.added == ["CC_SUMMER"]
    assert not d.removed and not d.reparented


def test_rounding_is_filtered_out():
    b = [("CC001", "P01", 100.00)]
    e = [("CC001", "P01", 100.005)]
    assert diff_values(b, e) == []


def test_material_variance_surfaces():
    b = [("CC001", "P01", 50_000.0)]
    e = [("CC001", "P01", 41_000.0)]
    d = diff_values(b, e)
    assert d[0].classification == "material"
    assert material_members(d) == ["CC001"]


def test_attribution_finds_routing_destination():
    txns = [
        {"id": "T1", "amount": 9_000.0, "expected_cost_center": "CC001",
         "posted_cost_center": "CC_SUMMER", "source": "payroll"},
        {"id": "T2", "amount": 500.0, "expected_cost_center": "CC001",
         "posted_cost_center": "CC001", "source": "payroll"},
    ]
    out = attribute_variance(txns, "CC001")
    assert list(out) == ["CC_SUMMER"]
    assert len(out["CC_SUMMER"]) == 1
