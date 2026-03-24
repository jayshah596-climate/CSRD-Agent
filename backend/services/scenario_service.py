from typing import Dict, List, Any


# NGFS Climate Scenarios (2023 vintage) - representative data
NGFS_SCENARIOS = {
    "net_zero_2050": {
        "name": "Net Zero 2050",
        "description": "Limits warming to 1.5°C with high overshoot. Ambitious emissions reductions and carbon removal.",
        "temperature_2030": 1.5,
        "temperature_2050": 1.5,
        "temperature_2100": 1.4,
        "carbon_price_2030": 147,  # USD/tCO2
        "carbon_price_2050": 563,
        "transition_risk": "high",
        "physical_risk": "low",
        "renewable_share_2050": 0.85,
        "co2_reduction_2030_pct": 0.43,
        "category": "orderly",
    },
    "below_2c": {
        "name": "Below 2°C",
        "description": "Achieves below 2°C with 67% probability. Gradual policy tightening.",
        "temperature_2030": 1.7,
        "temperature_2050": 1.8,
        "temperature_2100": 1.7,
        "carbon_price_2030": 75,
        "carbon_price_2050": 225,
        "transition_risk": "medium",
        "physical_risk": "low_medium",
        "renewable_share_2050": 0.70,
        "co2_reduction_2030_pct": 0.28,
        "category": "orderly",
    },
    "delayed_transition": {
        "name": "Delayed Transition",
        "description": "Delayed action until 2030, then disruptive transition. Higher financial risks.",
        "temperature_2030": 2.0,
        "temperature_2050": 1.8,
        "temperature_2100": 1.8,
        "carbon_price_2030": 20,
        "carbon_price_2050": 677,
        "transition_risk": "very_high",
        "physical_risk": "medium",
        "renewable_share_2050": 0.72,
        "co2_reduction_2030_pct": 0.05,
        "category": "disorderly",
    },
    "divergent_net_zero": {
        "name": "Divergent Net Zero",
        "description": "Reaches 1.5°C but with divergent policies and higher renewables costs.",
        "temperature_2030": 1.6,
        "temperature_2050": 1.5,
        "temperature_2100": 1.4,
        "carbon_price_2030": 180,
        "carbon_price_2050": 543,
        "transition_risk": "high",
        "physical_risk": "low",
        "renewable_share_2050": 0.88,
        "co2_reduction_2030_pct": 0.37,
        "category": "disorderly",
    },
    "current_policies": {
        "name": "Current Policies (Hothouse World)",
        "description": "Only current policies implemented. High physical risk. ~3°C warming.",
        "temperature_2030": 2.1,
        "temperature_2050": 2.7,
        "temperature_2100": 3.2,
        "carbon_price_2030": 5,
        "carbon_price_2050": 15,
        "transition_risk": "low",
        "physical_risk": "very_high",
        "renewable_share_2050": 0.35,
        "co2_reduction_2030_pct": 0.02,
        "category": "hot_house",
    },
}


def calculate_carbon_cost_impact(
    scope1_tco2e: float,
    scope2_tco2e: float,
    scope3_tco2e: float,
    scenario_key: str,
    year: int = 2030,
) -> Dict[str, Any]:
    """Estimate carbon cost exposure under a given scenario."""
    scenario = NGFS_SCENARIOS.get(scenario_key)
    if not scenario:
        return {}

    carbon_price = scenario["carbon_price_2030"] if year <= 2030 else scenario["carbon_price_2050"]

    # Direct cost (Scope 1 and 2 are typically covered by ETS/carbon tax)
    direct_exposure = (scope1_tco2e + scope2_tco2e) * carbon_price
    indirect_exposure = scope3_tco2e * carbon_price * 0.3  # partial pass-through

    return {
        "scenario": scenario["name"],
        "year": year,
        "carbon_price_usd_per_tco2": carbon_price,
        "direct_carbon_cost_usd": round(direct_exposure, 0),
        "indirect_carbon_cost_usd": round(indirect_exposure, 0),
        "total_exposure_usd": round(direct_exposure + indirect_exposure, 0),
        "temperature_pathway": scenario[f"temperature_{year}"] if f"temperature_{year}" in scenario else None,
    }


def calculate_value_at_risk(
    total_assets: float,  # EUR millions
    sector: str,
    scenario_key: str,
) -> Dict[str, Any]:
    """
    Calculate climate Value at Risk (VaR) using sector-adjusted multipliers.
    Based on Network for Greening the Financial System (NGFS) methodology.
    """
    scenario = NGFS_SCENARIOS.get(scenario_key)
    if not scenario:
        return {}

    # Sector transition risk multipliers (% of asset value at risk)
    sector_transition_risk = {
        "oil_gas": 0.45,
        "coal": 0.75,
        "utilities": 0.25,
        "automotive": 0.20,
        "aviation": 0.30,
        "steel": 0.22,
        "cement": 0.18,
        "chemicals": 0.15,
        "real_estate": 0.12,
        "financial": 0.08,
        "technology": 0.04,
        "healthcare": 0.03,
        "consumer_staples": 0.05,
        "default": 0.10,
    }

    # Physical risk multipliers (% of asset value at risk by 2050)
    sector_physical_risk = {
        "agriculture": 0.35,
        "real_estate_coastal": 0.28,
        "tourism": 0.22,
        "insurance": 0.18,
        "utilities": 0.15,
        "default": 0.08,
    }

    transition_mult = sector_transition_risk.get(sector, sector_transition_risk["default"])
    physical_mult = sector_physical_risk.get(sector, sector_physical_risk["default"])

    # Adjust by scenario
    transition_scenario_adj = {
        "net_zero_2050": 1.5,
        "below_2c": 1.0,
        "delayed_transition": 2.0,
        "divergent_net_zero": 1.8,
        "current_policies": 0.3,
    }
    physical_scenario_adj = {
        "net_zero_2050": 0.3,
        "below_2c": 0.5,
        "delayed_transition": 0.6,
        "divergent_net_zero": 0.4,
        "current_policies": 1.5,
    }

    t_adj = transition_scenario_adj.get(scenario_key, 1.0)
    p_adj = physical_scenario_adj.get(scenario_key, 1.0)

    transition_var = total_assets * transition_mult * t_adj
    physical_var = total_assets * physical_mult * p_adj

    return {
        "scenario": scenario["name"],
        "total_assets_eur_m": total_assets,
        "transition_var_eur_m": round(transition_var, 2),
        "physical_var_eur_m": round(physical_var, 2),
        "total_var_eur_m": round(transition_var + physical_var, 2),
        "total_var_pct": round((transition_var + physical_var) / total_assets * 100, 1),
    }


def run_scenario_analysis(
    scope1: float,
    scope2: float,
    scope3: float,
    total_assets: float,
    sector: str,
) -> Dict[str, Any]:
    """Run full scenario analysis across all NGFS scenarios."""
    results = {}

    for scenario_key in NGFS_SCENARIOS.keys():
        carbon_cost = calculate_carbon_cost_impact(scope1, scope2, scope3, scenario_key)
        var = calculate_value_at_risk(total_assets, sector, scenario_key)
        scenario = NGFS_SCENARIOS[scenario_key]

        results[scenario_key] = {
            "scenario_name": scenario["name"],
            "description": scenario["description"],
            "category": scenario["category"],
            "temperature_pathway": {
                "2030": scenario["temperature_2030"],
                "2050": scenario["temperature_2050"],
                "2100": scenario["temperature_2100"],
            },
            "carbon_price": {
                "2030": scenario["carbon_price_2030"],
                "2050": scenario["carbon_price_2050"],
                "unit": "USD/tCO2e",
            },
            "risk_levels": {
                "transition": scenario["transition_risk"],
                "physical": scenario["physical_risk"],
            },
            "carbon_cost_impact": carbon_cost,
            "value_at_risk": var,
        }

    return {
        "scenarios": results,
        "methodology": "NGFS Phase 4 (2023), aligned with TCFD recommendations",
        "reference_year": 2023,
    }


def get_all_scenarios() -> List[Dict[str, Any]]:
    return [
        {
            "key": k,
            "name": v["name"],
            "description": v["description"],
            "category": v["category"],
            "temperature_2050": v["temperature_2050"],
            "transition_risk": v["transition_risk"],
            "physical_risk": v["physical_risk"],
        }
        for k, v in NGFS_SCENARIOS.items()
    ]
