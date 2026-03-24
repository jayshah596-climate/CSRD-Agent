"""Tests for ESRS mapping and validation engine."""
import pytest
from esrs_engine.mapping import (
    get_esrs_structure,
    get_standard_disclosures,
    map_data_to_esrs,
    validate_esrs_completeness,
)
from esrs_engine.validator import validate_datapoint, validate_project_data


def test_esrs_structure_completeness():
    structure = get_esrs_structure()
    required_standards = {"ESRS_2", "E1", "E2", "E3", "E4", "E5", "S1", "S2", "S3", "S4", "G1"}
    assert required_standards.issubset(set(structure.keys()))


def test_e1_disclosures():
    e1 = get_standard_disclosures("E1")
    assert e1 is not None
    assert e1["name"] == "Climate Change"
    assert "E1-6" in e1["disclosures"]
    assert "E1-1" in e1["disclosures"]


def test_s1_key_metrics():
    s1 = get_standard_disclosures("S1")
    assert "key_metrics" in s1
    assert any("employee" in m.lower() for m in s1["key_metrics"])


def test_map_data_to_esrs():
    project_data = {
        "E1_E1-6": {"scope1": 25000, "scope2": 18000},
        "S1_S1-6": {"employees": 8450},
    }
    result = map_data_to_esrs(project_data, ["E1", "S1"])
    assert "E1" in result
    assert "S1" in result
    assert "completion_pct" in result["E1"]


def test_validate_datapoint_valid():
    is_valid, errors = validate_datapoint("E1-6_scope1_emissions", 25000.0)
    assert is_valid is True
    assert len(errors) == 0


def test_validate_datapoint_negative_emissions():
    is_valid, errors = validate_datapoint("E1-6_scope1_emissions", -100.0)
    assert is_valid is False
    assert len(errors) > 0


def test_validate_datapoint_invalid_percentage():
    is_valid, errors = validate_datapoint("E1-5_renewable_pct", 150.0)
    assert is_valid is False


def test_validate_datapoint_valid_percentage():
    is_valid, errors = validate_datapoint("E1-5_renewable_pct", 45.0)
    assert is_valid is True


def test_validate_project_data_with_gaps():
    data = {
        "E1-6_scope1_emissions": 25000.0,
        "E1-5_total_energy": 85000000.0,
    }
    result = validate_project_data(data)
    assert "is_valid" in result
    assert "warnings" in result
    # Should warn about missing mandatory fields
    assert len(result["warnings"]) > 0


def test_esrs_structure_api(client, auth_headers):
    proj = client.post("/api/projects", json={
        "name": "ESRS API Test", "reporting_year": 2024,
    }, headers=auth_headers).json()
    pid = proj["id"]
    res = client.get(f"/api/projects/{pid}/data/esrs-structure", headers=auth_headers)
    assert res.status_code == 200
    structure = res.json()
    assert "E1" in structure
    assert "S1" in structure
