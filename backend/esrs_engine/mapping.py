"""
ESRS 2025 Mapping Engine
Maps company data to ESRS E1-E5, S1-S4, G1 disclosure requirements.
Based on EFRAG ESRS Set 1 (EU Commission Delegated Regulation 2023/2772).
"""

from typing import Dict, List, Any, Optional


# ─────────────────────────────────────────────────────────────────────────────
# ESRS 2025 Disclosure Structure
# ─────────────────────────────────────────────────────────────────────────────
ESRS_STRUCTURE = {
    "ESRS_2": {
        "name": "General Disclosures",
        "category": "cross_cutting",
        "disclosures": {
            "GOV-1": "The role of the administrative, management and supervisory bodies",
            "GOV-2": "Information provided to and sustainability matters addressed by the AMSB",
            "GOV-3": "Integration of sustainability-related performance in incentive schemes",
            "GOV-4": "Statement on due diligence",
            "GOV-5": "Risk management and internal controls over sustainability reporting",
            "SBM-1": "Strategy, business model and value chain",
            "SBM-2": "Interests and views of stakeholders",
            "SBM-3": "Material impacts, risks and opportunities and their interaction with strategy",
            "IRO-1": "Description of the processes to identify and assess material IROs",
            "IRO-2": "Disclosure Requirements covered by the undertaking's sustainability statement",
            "MDR-P": "Policies adopted to manage material sustainability matters",
            "MDR-A": "Actions and resources in relation to material sustainability matters",
            "MDR-T": "Tracking effectiveness of policies and actions through targets",
        },
    },
    "E1": {
        "name": "Climate Change",
        "category": "environmental",
        "disclosures": {
            "E1-1": "Transition plan for climate change mitigation",
            "E1-2": "Policies related to climate change mitigation and adaptation",
            "E1-3": "Actions and resources in relation to climate change policies",
            "E1-4": "Targets related to climate change mitigation and adaptation",
            "E1-5": "Energy consumption and mix",
            "E1-6": "Gross Scopes 1, 2, 3 and Total GHG emissions",
            "E1-7": "GHG removals and GHG mitigation projects financed through carbon credits",
            "E1-8": "Internal carbon pricing",
            "E1-9": "Anticipated financial effects from material physical and transition risks",
        },
        "key_metrics": [
            "Gross Scope 1 GHG emissions (tCO2e)",
            "Gross Scope 2 GHG emissions – location-based (tCO2e)",
            "Gross Scope 2 GHG emissions – market-based (tCO2e)",
            "Total Scope 3 GHG emissions (tCO2e)",
            "Total GHG emissions (tCO2e)",
            "GHG intensity (tCO2e/EUR M revenue)",
            "Total energy consumption (MWh)",
            "% renewable energy",
            "Energy intensity (MWh/EUR M revenue)",
        ],
    },
    "E2": {
        "name": "Pollution",
        "category": "environmental",
        "disclosures": {
            "E2-1": "Policies related to pollution",
            "E2-2": "Actions and resources related to pollution",
            "E2-3": "Targets related to pollution",
            "E2-4": "Pollution of air, water and soil",
            "E2-5": "Substances of concern and substances of very high concern",
            "E2-6": "Anticipated financial effects from material pollution-related risks",
        },
        "key_metrics": [
            "Air emissions (NOx, SOx, particulate matter) (tonnes)",
            "Water pollutants discharged (kg)",
            "Soil contamination incidents",
            "Substances of concern (tonnes)",
        ],
    },
    "E3": {
        "name": "Water and Marine Resources",
        "category": "environmental",
        "disclosures": {
            "E3-1": "Policies related to water and marine resources",
            "E3-2": "Actions and resources related to water and marine resources",
            "E3-3": "Targets related to water and marine resources",
            "E3-4": "Water consumption",
            "E3-5": "Anticipated financial effects from material water and marine risks",
        },
        "key_metrics": [
            "Total water consumption (m³)",
            "Water withdrawal by source (m³)",
            "Water intensity (m³/EUR M revenue)",
            "% operations in water-stressed areas",
        ],
    },
    "E4": {
        "name": "Biodiversity and Ecosystems",
        "category": "environmental",
        "disclosures": {
            "E4-1": "Transition plan and biodiversity strategy",
            "E4-2": "Policies related to biodiversity and ecosystems",
            "E4-3": "Actions and resources related to biodiversity and ecosystems",
            "E4-4": "Targets related to biodiversity and ecosystems",
            "E4-5": "Impact metrics related to biodiversity and ecosystems change",
            "E4-6": "Anticipated financial effects from material biodiversity risks",
        },
        "key_metrics": [
            "Land use (hectares)",
            "Operations in or near protected areas",
            "Species at risk affected",
        ],
    },
    "E5": {
        "name": "Resource Use and Circular Economy",
        "category": "environmental",
        "disclosures": {
            "E5-1": "Policies related to resource use and circular economy",
            "E5-2": "Actions and resources related to resource use and circular economy",
            "E5-3": "Targets related to resource use and circular economy",
            "E5-4": "Resource inflows",
            "E5-5": "Resource outflows",
            "E5-6": "Anticipated financial effects from material resource use risks",
        },
        "key_metrics": [
            "Total material consumption (tonnes)",
            "% recycled input materials",
            "Total waste generated (tonnes)",
            "% waste recycled",
            "% products designed for reuse/recycling",
        ],
    },
    "S1": {
        "name": "Own Workforce",
        "category": "social",
        "disclosures": {
            "S1-1": "Policies related to own workforce",
            "S1-2": "Processes for engaging with own workers",
            "S1-3": "Processes to remediate negative impacts",
            "S1-4": "Taking action on material impacts on own workforce",
            "S1-5": "Targets related to managing material negative impacts",
            "S1-6": "Characteristics of the undertaking's employees",
            "S1-7": "Characteristics of non-employee workers",
            "S1-8": "Collective bargaining coverage and social dialogue",
            "S1-9": "Diversity metrics",
            "S1-10": "Adequate wages",
            "S1-11": "Social protection",
            "S1-12": "Persons with disabilities",
            "S1-13": "Training and skills development metrics",
            "S1-14": "Health and safety metrics",
            "S1-15": "Work-life balance metrics",
            "S1-16": "Compensation metrics (pay gap and total compensation)",
            "S1-17": "Incidents, complaints and severe human rights impacts",
        },
        "key_metrics": [
            "Total employees",
            "% permanent employees",
            "% part-time employees",
            "Gender pay gap (%)",
            "% women in senior leadership",
            "Lost Time Injury Rate (LTIR)",
            "Fatalities",
            "Training hours per employee",
            "Employee turnover rate (%)",
            "% employees covered by collective bargaining",
        ],
    },
    "S2": {
        "name": "Workers in the Value Chain",
        "category": "social",
        "disclosures": {
            "S2-1": "Policies related to value chain workers",
            "S2-2": "Processes for engaging with value chain workers",
            "S2-3": "Processes to remediate negative impacts on value chain workers",
            "S2-4": "Taking action on material impacts on value chain workers",
            "S2-5": "Targets related to managing material negative impacts on value chain workers",
        },
    },
    "S3": {
        "name": "Affected Communities",
        "category": "social",
        "disclosures": {
            "S3-1": "Policies related to affected communities",
            "S3-2": "Processes for engaging with affected communities",
            "S3-3": "Processes to remediate negative impacts on affected communities",
            "S3-4": "Taking action on material impacts on affected communities",
            "S3-5": "Targets related to managing material negative impacts on affected communities",
        },
    },
    "S4": {
        "name": "Consumers and End-Users",
        "category": "social",
        "disclosures": {
            "S4-1": "Policies related to consumers and end-users",
            "S4-2": "Processes for engaging with consumers and end-users",
            "S4-3": "Processes to remediate negative impacts on consumers and end-users",
            "S4-4": "Taking action on material impacts on consumers and end-users",
            "S4-5": "Targets related to managing material negative impacts on consumers and end-users",
        },
    },
    "G1": {
        "name": "Business Conduct",
        "category": "governance",
        "disclosures": {
            "G1-1": "Business conduct policies and corporate culture",
            "G1-2": "Management of relationships with suppliers",
            "G1-3": "Prevention and detection of corruption and bribery",
            "G1-4": "Confirmed incidents of corruption or bribery",
            "G1-5": "Political influence and lobbying activities",
            "G1-6": "Payment practices",
        },
        "key_metrics": [
            "Confirmed corruption incidents",
            "% employees trained on anti-corruption",
            "% suppliers with sustainability screening",
            "Average payment period (days)",
            "Lobbying expenditures (EUR)",
        ],
    },
}


def get_esrs_structure() -> Dict[str, Any]:
    return ESRS_STRUCTURE


def get_standard_disclosures(standard: str) -> Optional[Dict[str, Any]]:
    return ESRS_STRUCTURE.get(standard)


def map_data_to_esrs(
    project_data: Dict[str, Any],
    material_standards: List[str],
) -> Dict[str, Any]:
    """
    Map collected project data to ESRS disclosure requirements.
    Returns a structured dict of ESRS disclosures with data and gaps.
    """
    mapped = {}

    for standard in material_standards:
        std_config = ESRS_STRUCTURE.get(standard)
        if not std_config:
            continue

        std_result = {
            "standard": standard,
            "name": std_config["name"],
            "category": std_config["category"],
            "disclosures": {},
            "completion_pct": 0,
            "data_gaps": [],
        }

        disclosures = std_config.get("disclosures", {})
        completed = 0

        for disc_id, disc_name in disclosures.items():
            disc_key = f"{standard}_{disc_id}".replace("-", "_")
            disc_data = project_data.get(disc_key) or project_data.get(disc_id)

            std_result["disclosures"][disc_id] = {
                "disclosure_id": disc_id,
                "disclosure_name": disc_name,
                "status": "completed" if disc_data else "missing",
                "data": disc_data,
            }

            if disc_data:
                completed += 1
            else:
                std_result["data_gaps"].append(disc_id)

        if disclosures:
            std_result["completion_pct"] = round(completed / len(disclosures) * 100, 1)

        mapped[standard] = std_result

    return mapped


def validate_esrs_completeness(mapped_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate completeness of ESRS disclosures and flag mandatory gaps."""
    validation_result = {
        "overall_complete": True,
        "standards": {},
        "critical_gaps": [],
        "warnings": [],
    }

    MANDATORY_DISCLOSURES = {
        "ESRS_2": ["GOV-1", "SBM-1", "SBM-3", "IRO-1", "IRO-2"],
        "E1": ["E1-1", "E1-6"],
        "S1": ["S1-6", "S1-14", "S1-16"],
        "G1": ["G1-1", "G1-3"],
    }

    for standard, data in mapped_data.items():
        mandatory = MANDATORY_DISCLOSURES.get(standard, [])
        std_gaps = []

        for disc_id in mandatory:
            disc = data.get("disclosures", {}).get(disc_id)
            if disc and disc.get("status") == "missing":
                std_gaps.append(disc_id)
                validation_result["critical_gaps"].append(f"{standard} - {disc_id}")

        validation_result["standards"][standard] = {
            "completion_pct": data.get("completion_pct", 0),
            "mandatory_gaps": std_gaps,
            "is_complete": len(std_gaps) == 0,
        }

        if std_gaps:
            validation_result["overall_complete"] = False

    return validation_result
