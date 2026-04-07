from typing import Dict, Any, Optional, List
import os

# Try to use Anthropic; fallback to template-based generation if not configured
try:
    import anthropic
    _ANTHROPIC_AVAILABLE = True
except ImportError:
    _ANTHROPIC_AVAILABLE = False


ESRS_NARRATIVE_TEMPLATES = {
    "E1_policy": """
{company_name} is committed to climate change mitigation and adaptation in alignment with the Paris Agreement
and the EU's 2050 climate neutrality objective. Our climate policy establishes science-based targets
to reduce greenhouse gas emissions across Scope 1, 2, and 3, in line with ESRS E1 requirements.
We have set a target to reduce absolute Scope 1 and 2 emissions by {emission_reduction_target}% by {target_year}
(versus {base_year} baseline), and to achieve net zero across our value chain by 2050.
Our approach is governed by the Board-level {governance_body}, with quarterly progress reviews
and annual disclosure under ESRS E1 and the TCFD framework.
""",
    "E1_strategy": """
{company_name}'s climate strategy is built on four pillars: (1) rapid decarbonisation of our operations,
(2) transition of our value chain, (3) climate resilience through scenario-based risk management, and
(4) nature-based solutions for residual emissions. We have conducted a Double Materiality Assessment
identifying climate change as a {materiality_level} priority across both impact and financial materiality
dimensions. Transition planning is guided by the IEA Net Zero by 2050 and NGFS scenarios.
""",
    "S1_workforce": """
{company_name} employs {employee_count} people across {country_count} countries.
Our workforce strategy prioritises safe and healthy working conditions, fair wages, equal
opportunities, and continuous development. We are committed to the UN Guiding Principles on
Business and Human Rights and have implemented a comprehensive human rights due diligence process
in line with ESRS S1 requirements. Gender pay gap reporting shows {gender_pay_gap}%.
Our Lost Time Injury Rate (LTIR) stands at {ltir} per million hours worked.
""",
    "G1_governance": """
{company_name} maintains robust corporate governance structures to support sustainable business
conduct. Our Board of Directors includes {board_members} members, of whom {independent_members}
are independent and {female_board_pct}% are women. The Board's Sustainability Committee provides
oversight of CSRD/ESRS compliance, climate strategy, and ESG risk management.
We operate a comprehensive anti-corruption and anti-bribery programme,
with mandatory annual training reaching {compliance_training_pct}% of employees in {reporting_year}.
""",
    "general_disclosure": """
This disclosure has been prepared in accordance with the European Sustainability Reporting Standards
(ESRS) as adopted under the Corporate Sustainability Reporting Directive (CSRD), Commission Delegated
Regulation (EU) 2023/2772. The information covers {company_name}'s activities for the reporting period
{reporting_year} and reflects the outcomes of our Double Materiality Assessment conducted in accordance
with ESRS 1 General Requirements.
""",
}


def generate_narrative_template(
    template_key: str,
    context: Dict[str, Any],
) -> str:
    """Generate narrative using template substitution."""
    template = ESRS_NARRATIVE_TEMPLATES.get(template_key, "")
    if not template:
        return f"Narrative for {template_key} not available."

    # Fill in template variables with context
    for key, value in context.items():
        placeholder = "{" + key + "}"
        template = template.replace(placeholder, str(value) if value is not None else "N/A")

    # Clean up any unfilled placeholders
    import re
    template = re.sub(r"\{[^}]+\}", "[TO BE COMPLETED]", template)
    return template.strip()


def generate_ai_narrative(
    section: str,
    context: Dict[str, Any],
    api_key: Optional[str] = None,
) -> str:
    """
    Generate ESRS-compliant narrative using Claude API.
    Falls back to template if API is unavailable.
    """
    if not _ANTHROPIC_AVAILABLE or not api_key:
        return generate_narrative_template(
            _map_section_to_template(section), context
        )

    try:
        client = anthropic.Anthropic(api_key=api_key)

        company_ctx = f"""
Company: {context.get('company_name', 'the company')}
Sector: {context.get('sector', 'N/A')}
Employees: {context.get('employee_count', 'N/A')}
Revenue: EUR {context.get('annual_revenue', 'N/A')}M
Reporting year: {context.get('reporting_year', 2023)}
Material topics: {', '.join(context.get('material_topics', []))}
Total Scope 1+2 emissions: {context.get('total_scope12_tco2e', 'N/A')} tCO2e
Total Scope 3 emissions: {context.get('total_scope3_tco2e', 'N/A')} tCO2e
"""
        prompt = f"""You are an expert CSRD/ESRS sustainability reporting specialist.

Write a professional, regulatory-compliant narrative for the following ESRS section:
**Section:** {section}

**Company Context:**
{company_ctx}

Requirements:
- Comply strictly with ESRS 2025 structure and language
- Use formal, enterprise-grade tone
- Include specific data points from the context where available
- Avoid greenwashing language
- Length: 200-350 words
- Reference relevant ESRS disclosure requirements

Output only the narrative text, no headings or metadata."""

        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text

    except Exception as e:
        # Fallback to template
        return generate_narrative_template(
            _map_section_to_template(section), context
        )


def generate_full_report_narratives(
    context: Dict[str, Any],
    sections: List[str],
    api_key: Optional[str] = None,
) -> Dict[str, str]:
    """Generate narratives for all required ESRS sections."""
    narratives = {}
    for section in sections:
        narratives[section] = generate_ai_narrative(section, context, api_key)
    return narratives


def _map_section_to_template(section: str) -> str:
    mapping = {
        "E1 Climate Policy": "E1_policy",
        "E1 Strategy": "E1_strategy",
        "S1 Own Workforce": "S1_workforce",
        "G1 Governance": "G1_governance",
        "General Disclosure": "general_disclosure",
    }
    return mapping.get(section, "general_disclosure")


ESRS_REPORT_SECTIONS = [
    "General Disclosure",
    "E1 Climate Policy",
    "E1 Strategy",
    "E1 Targets",
    "E1 GHG Emissions",
    "E1 Energy",
    "E2 Pollution Policy",
    "E3 Water Policy",
    "E4 Biodiversity Policy",
    "E5 Circular Economy",
    "S1 Own Workforce",
    "S2 Value Chain Workers",
    "S3 Affected Communities",
    "S4 Consumers",
    "G1 Governance",
    "G1 Business Conduct",
]
