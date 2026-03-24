"""Tests for climate scenario analysis."""
import pytest
from services.scenario_service import (
    run_scenario_analysis,
    calculate_carbon_cost_impact,
    calculate_value_at_risk,
    get_all_scenarios,
    NGFS_SCENARIOS,
)


def test_ngfs_scenarios_count():
    scenarios = get_all_scenarios()
    assert len(scenarios) == 5
    keys = {s["key"] for s in scenarios}
    assert "net_zero_2050" in keys
    assert "current_policies" in keys


def test_carbon_cost_net_zero():
    result = calculate_carbon_cost_impact(
        scope1_tco2e=10000,
        scope2_tco2e=5000,
        scope3_tco2e=50000,
        scenario_key="net_zero_2050",
        year=2030,
    )
    assert result["carbon_price_usd_per_tco2"] == 147
    assert result["direct_carbon_cost_usd"] > 0
    assert result["total_exposure_usd"] > result["direct_carbon_cost_usd"]


def test_carbon_cost_current_policies():
    result = calculate_carbon_cost_impact(
        scope1_tco2e=10000,
        scope2_tco2e=5000,
        scope3_tco2e=50000,
        scenario_key="current_policies",
        year=2030,
    )
    assert result["carbon_price_usd_per_tco2"] == 5
    # Current policies have low carbon price → lower cost
    nz_result = calculate_carbon_cost_impact(10000, 5000, 50000, "net_zero_2050", 2030)
    assert result["total_exposure_usd"] < nz_result["total_exposure_usd"]


def test_value_at_risk():
    result = calculate_value_at_risk(1000.0, "automotive", "net_zero_2050")
    assert result["total_assets_eur_m"] == 1000.0
    assert result["transition_var_eur_m"] > 0
    assert result["total_var_pct"] > 0


def test_full_scenario_analysis():
    results = run_scenario_analysis(
        scope1=25000,
        scope2=18000,
        scope3=150000,
        total_assets=500.0,
        sector="automotive",
    )
    assert "scenarios" in results
    assert len(results["scenarios"]) == 5
    for key, scenario in results["scenarios"].items():
        assert "temperature_pathway" in scenario
        assert "carbon_price" in scenario
        assert "value_at_risk" in scenario


def test_scenario_api_ngfs(client, auth_headers):
    proj = client.post("/api/projects", json={
        "name": "Scenario API Test", "reporting_year": 2024,
    }, headers=auth_headers).json()
    pid = proj["id"]

    res = client.get(f"/api/projects/{pid}/scenarios/ngfs", headers=auth_headers)
    assert res.status_code == 200
    scenarios = res.json()
    assert len(scenarios) == 5
