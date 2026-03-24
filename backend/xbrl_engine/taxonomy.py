"""
ESRS XBRL Taxonomy Mappings
Based on EFRAG ESRS XBRL Taxonomy (2024 release).
"""

# ESRS XBRL namespace
ESRS_NAMESPACE = "https://xbrl.efrag.org/taxonomy/esrs/2024"
ESRS_PREFIX = "esrs"

# Key ESRS XBRL tags (representative subset)
XBRL_TAGS = {
    # E1 - Climate
    "E1-6_scope1_emissions": "esrs:GrossScope1GHGEmissions",
    "E1-6_scope2_location": "esrs:GrossScope2GHGEmissionsLocationBased",
    "E1-6_scope2_market": "esrs:GrossScope2GHGEmissionsMarketBased",
    "E1-6_scope3_total": "esrs:TotalGrossScope3GHGEmissions",
    "E1-6_total_ghg": "esrs:TotalGHGEmissions",
    "E1-5_total_energy": "esrs:TotalEnergyConsumptionWithinOrganisation",
    "E1-5_renewable_energy": "esrs:EnergyConsumptionFromRenewableSources",
    "E1-5_renewable_pct": "esrs:PercentageRenewableEnergyInTotalEnergyConsumption",
    # E2 - Pollution
    "E2-4_air_emissions_nox": "esrs:NoxEmissions",
    "E2-4_air_emissions_sox": "esrs:SoxEmissions",
    "E2-4_air_emissions_pm": "esrs:ParticulateMatterEmissions",
    # E3 - Water
    "E3-4_water_consumption": "esrs:TotalWaterConsumption",
    "E3-4_water_withdrawal": "esrs:TotalWaterWithdrawal",
    # S1 - Workforce
    "S1-6_employee_total": "esrs:TotalNumberOfEmployees",
    "S1-6_female_employees": "esrs:NumberOfFemaleEmployees",
    "S1-6_male_employees": "esrs:NumberOfMaleEmployees",
    "S1-14_ltir": "esrs:LostTimeInjuryRateEmployees",
    "S1-14_fatalities": "esrs:NumberOfFatalitiesAsResultOfWorkRelatedInjuriesAndDiseasesEmployees",
    "S1-16_gender_pay_gap": "esrs:UnadjustedGenderPayGap",
    # G1 - Governance
    "G1-4_corruption_incidents": "esrs:NumberOfConvictionsForViolationsOfAntiCorruptionAndAntiBriberyLaws",
    "G1-6_avg_payment_days": "esrs:AveragePaymentPeriodToSMEs",
}


def get_xbrl_tag(datapoint_id: str) -> str:
    return XBRL_TAGS.get(datapoint_id, f"esrs:UnmappedDatapoint_{datapoint_id}")


def get_all_tags() -> dict:
    return XBRL_TAGS
