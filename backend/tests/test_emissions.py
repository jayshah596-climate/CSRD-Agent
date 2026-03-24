"""Tests for GHG emissions endpoints and calculation logic."""
import pytest
from services.emissions_service import calculate_emission, get_scope3_categories


def test_calculate_emission_basic():
    # 1000 kWh * 0.276 kgCO2e/kWh = 276 kgCO2e = 0.276 tCO2e
    result = calculate_emission(1000, 0.276, "kWh", "kgCO2e/kWh")
    assert abs(result - 0.276) < 0.001


def test_calculate_emission_natural_gas():
    # 10000 m3 * 2.034 kgCO2e/m3 = 20340 kgCO2e = 20.34 tCO2e
    result = calculate_emission(10000, 2.034, "m3", "kgCO2e/m3")
    assert abs(result - 20.34) < 0.01


def test_scope3_categories_count():
    categories = get_scope3_categories()
    assert len(categories) == 15
    assert categories[0]["id"] == "cat1"
    assert categories[14]["id"] == "cat15"


def test_add_emission_entry(client, auth_headers):
    # Create project first
    proj = client.post("/api/projects", json={
        "name": "Emissions Test Project", "reporting_year": 2024,
    }, headers=auth_headers).json()
    pid = proj["id"]

    res = client.post(f"/api/projects/{pid}/emissions", json={
        "scope": "scope_1",
        "source_name": "Gas boiler",
        "activity_value": 5000.0,
        "activity_unit": "m3",
        "emission_factor_value": 2.034,
        "emission_factor_unit": "kgCO2e/m3",
        "emission_factor_source": "DEFRA 2023",
    }, headers=auth_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["scope"] == "scope_1"
    assert data["source_name"] == "Gas boiler"
    assert data["co2e_tonnes"] == pytest.approx(10.17, rel=0.01)


def test_emission_summary(client, auth_headers):
    proj = client.post("/api/projects", json={
        "name": "Summary Test", "reporting_year": 2024,
    }, headers=auth_headers).json()
    pid = proj["id"]

    client.post(f"/api/projects/{pid}/emissions", json={
        "scope": "scope_1",
        "source_name": "Source A",
        "activity_value": 1000.0,
        "activity_unit": "litre",
        "emission_factor_value": 2.687,
        "emission_factor_unit": "kgCO2e/litre",
        "emission_factor_source": "DEFRA 2023",
    }, headers=auth_headers)

    res = client.get(f"/api/projects/{pid}/emissions/summary", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "scope_1" in data
    assert data["scope_1"]["total_co2e"] > 0
    assert "total_co2e" in data


def test_list_emission_factors(client, auth_headers):
    proj = client.post("/api/projects", json={
        "name": "EF Test", "reporting_year": 2024,
    }, headers=auth_headers).json()
    pid = proj["id"]
    res = client.get(f"/api/projects/{pid}/emissions/emission-factors", headers=auth_headers)
    assert res.status_code == 200
    factors = res.json()
    assert len(factors) > 0
    assert "factor_value" in factors[0]
