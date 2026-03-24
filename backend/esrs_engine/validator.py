"""
ESRS Data Validation Engine
Validates submitted data against ESRS 2025 requirements.
"""

from typing import Dict, List, Any, Tuple


DATAPOINT_RULES = {
    # E1 - Climate
    "E1-6_scope1_emissions": {
        "type": "numeric",
        "unit": "tCO2e",
        "required": True,
        "min": 0,
        "description": "Gross Scope 1 GHG emissions",
    },
    "E1-6_scope2_location": {
        "type": "numeric",
        "unit": "tCO2e",
        "required": True,
        "min": 0,
        "description": "Gross Scope 2 GHG emissions (location-based)",
    },
    "E1-6_scope2_market": {
        "type": "numeric",
        "unit": "tCO2e",
        "required": False,
        "min": 0,
        "description": "Gross Scope 2 GHG emissions (market-based)",
    },
    "E1-5_total_energy": {
        "type": "numeric",
        "unit": "MWh",
        "required": True,
        "min": 0,
        "description": "Total energy consumption",
    },
    "E1-5_renewable_pct": {
        "type": "percentage",
        "unit": "%",
        "required": False,
        "min": 0,
        "max": 100,
        "description": "Percentage of renewable energy",
    },
    # S1 - Workforce
    "S1-6_employee_count": {
        "type": "integer",
        "unit": "headcount",
        "required": True,
        "min": 0,
        "description": "Total number of employees",
    },
    "S1-14_ltir": {
        "type": "numeric",
        "unit": "per million hours",
        "required": True,
        "min": 0,
        "description": "Lost Time Injury Rate",
    },
    "S1-16_gender_pay_gap": {
        "type": "percentage",
        "unit": "%",
        "required": True,
        "min": -100,
        "max": 100,
        "description": "Gender pay gap (unadjusted)",
    },
}


def validate_datapoint(
    datapoint_id: str,
    value: Any,
) -> Tuple[bool, List[str]]:
    """Validate a single data point against ESRS rules."""
    errors = []
    rule = DATAPOINT_RULES.get(datapoint_id)

    if not rule:
        return True, []  # No rule defined; pass

    # Type checks
    if rule["type"] == "numeric":
        try:
            v = float(value)
        except (TypeError, ValueError):
            errors.append(f"{datapoint_id}: Expected numeric value, got '{value}'")
            return False, errors

        if "min" in rule and v < rule["min"]:
            errors.append(f"{datapoint_id}: Value {v} is below minimum {rule['min']}")
        if "max" in rule and v > rule["max"]:
            errors.append(f"{datapoint_id}: Value {v} exceeds maximum {rule['max']}")

    elif rule["type"] == "percentage":
        try:
            v = float(value)
        except (TypeError, ValueError):
            errors.append(f"{datapoint_id}: Expected percentage, got '{value}'")
            return False, errors
        if v < 0 or v > 100:
            errors.append(f"{datapoint_id}: Percentage {v} is outside 0-100 range")

    elif rule["type"] == "integer":
        try:
            v = int(value)
        except (TypeError, ValueError):
            errors.append(f"{datapoint_id}: Expected integer, got '{value}'")
            return False, errors
        if "min" in rule and v < rule["min"]:
            errors.append(f"{datapoint_id}: Value {v} is below minimum {rule['min']}")

    return len(errors) == 0, errors


def validate_project_data(
    data: Dict[str, Any],
) -> Dict[str, Any]:
    """Validate all data points for a project."""
    all_errors = []
    all_warnings = []
    validated = {}

    for dp_id, value in data.items():
        is_valid, errors = validate_datapoint(dp_id, value)
        validated[dp_id] = {"value": value, "is_valid": is_valid, "errors": errors}
        if not is_valid:
            all_errors.extend(errors)

    # Check mandatory fields
    for dp_id, rule in DATAPOINT_RULES.items():
        if rule.get("required") and dp_id not in data:
            all_warnings.append(f"Missing mandatory datapoint: {dp_id} ({rule['description']})")

    return {
        "is_valid": len(all_errors) == 0,
        "errors": all_errors,
        "warnings": all_warnings,
        "datapoints": validated,
        "total_validated": len(validated),
    }
