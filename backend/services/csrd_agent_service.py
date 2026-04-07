"""
CSRD End-to-End Reporting Agent Service
Drives Claude through the 8-step CSRD/ESRS analysis and streams results.
"""

from typing import AsyncGenerator, Dict, Any, List, Optional
import json
import re
import logging

logger = logging.getLogger("csrd-agent")

# ─── Step definitions ─────────────────────────────────────────────────────────

AGENT_STEPS = [
    {"id": "wave_eligibility",              "label": "Wave Eligibility",         "xml_tag": "scratchpad"},
    {"id": "esrs_modules",                  "label": "ESRS Modules",             "xml_tag": "esrs_modules"},
    {"id": "data_processing",               "label": "Data Processing",          "xml_tag": "data_processing"},
    {"id": "double_materiality",            "label": "Double Materiality",       "xml_tag": "double_materiality_assessment"},
    {"id": "iro_analysis",                  "label": "IRO Analysis",             "xml_tag": "iro_analysis"},
    {"id": "climate_scenario",              "label": "Climate Scenarios",        "xml_tag": "climate_scenario_analysis"},
    {"id": "esg_report",                    "label": "ESG Report",               "xml_tag": "esg_report"},
    {"id": "xbrl_specifications",           "label": "XBRL Specifications",      "xml_tag": "xbrl_specifications"},
]

STEP_TAG_MAP = {step["xml_tag"]: step["id"] for step in AGENT_STEPS}


# ─── Prompt builder ───────────────────────────────────────────────────────────

def build_csrd_prompt(
    company_data: Dict[str, Any],
    reporting_requirements: List[str],
    raw_data: str,
) -> str:
    """Assemble the comprehensive 8-step CSRD analysis prompt for Claude."""

    company_json = json.dumps(company_data, indent=2, ensure_ascii=False)
    requirements_list = "\n".join(f"- {r}" for r in reporting_requirements)

    return f"""You are an expert CSRD (Corporate Sustainability Reporting Directive) and ESRS (European Sustainability Reporting Standards) specialist with deep knowledge of EFRAG standards, the latest CSRD amendments, and simplified ESRS for SMEs.

You will guide a company through the complete CSRD-ESRS reporting process, from data collection through final XBRL specification, in compliance with the latest EFRAG standards.

Here is the company information you will be working with:

<company_data>
{company_json}
</company_data>

Here are the reporting requirements selected:

<reporting_requirements>
{requirements_list}
</reporting_requirements>

Here is the raw sustainability data:

<raw_data>
{raw_data if raw_data.strip() else "No raw data provided. Use reasonable estimates and clearly note where actual data is needed."}
</raw_data>

Complete the following 8-step CSRD-ESRS reporting process. For each step, output your analysis in the XML tags specified.

---

**STEP 1: DETERMINE REPORTING WAVE ELIGIBILITY**

Analyze the company data to determine which reporting wave applies based on the latest CSRD amendments. Consider:
- Company size (employees, balance sheet total, net turnover)
- Whether EU or non-EU, listed or non-listed
- Current fiscal year

Wave criteria:
- Wave 1: Large EU companies already subject to NFRD (reporting from 2024 for FY 2023)
- Wave 2: Large EU companies not previously subject to NFRD (reporting from 2025 for FY 2024)
- Wave 3: Listed SMEs, small and non-complex credit institutions, captive insurance (reporting from 2026 for FY 2025)
- Wave 4+: Non-EU companies with significant EU operations (≥€150M EU net turnover)

Output your wave analysis in <scratchpad> tags.

---

**STEP 2: IDENTIFY APPLICABLE ESRS MODULES AND METRICS**

Based on the reporting requirements and company characteristics, identify which of the 12 ESRS modules apply. Cross-cutting standards ESRS 1 and ESRS 2 are always mandatory. For topic-specific standards (E1-E5, S1-S4, G1), determine mandatory vs voluntary based on double materiality assessment.

List:
- Which modules are mandatory vs voluntary for this company
- Specific metrics from each selected module that must be reported
- Any phase-in provisions that apply

Output in <esrs_modules> tags.

---

**STEP 3: DATA PROCESSING AND CALCULATIONS**

Process the raw data provided and perform necessary calculations for each applicable metric:

1. Extract relevant data points from the raw data
2. Perform required calculations (GHG emissions in tCO2e, intensity ratios, workforce metrics, etc.)
3. Apply appropriate emission factors and methodologies (GHG Protocol, ISO 14064, etc.)
4. Identify data gaps and quality issues
5. Note assumptions made where data is incomplete

Present results in clearly labelled tables where appropriate, with units of measurement.

Output in <data_processing> tags.

---

**STEP 4: DOUBLE MATERIALITY ASSESSMENT**

Conduct a double materiality assessment covering:

**Impact Materiality** — How the company affects people and the environment:
- Scale: How widespread is the impact?
- Scope: How many people/ecosystems affected?
- Irremediability: How reversible is the impact?
- Likelihood: For potential impacts

**Financial Materiality** — How sustainability matters affect financial performance:
- Magnitude: Size of financial effect
- Likelihood: Probability of occurrence

For each material topic identified:
- Assess impact materiality (High / Medium / Low)
- Assess financial materiality (High / Medium / Low)
- Provide justification
- Determine overall materiality determination

Include a materiality matrix summary.

Output in <double_materiality_assessment> tags.

---

**STEP 5: IRO (IMPACTS, RISKS, AND OPPORTUNITIES) ANALYSIS**

For each material topic, conduct an IRO analysis documenting:

- **Actual impacts** (positive and negative, current)
- **Potential impacts** (positive and negative, future)
- **Physical risks** (acute and chronic climate/environmental risks)
- **Transition risks** (policy, technology, market, reputational)
- **Systemic risks**
- **Opportunities** (resource efficiency, new markets, innovation)
- Time horizons: Short-term (0-3yr), Medium-term (3-10yr), Long-term (10yr+)
- Affected stakeholders
- Connection to strategy and business model

Reference specific ESRS disclosure requirements (e.g., ESRS E1-IRO-1, ESRS S1-IRO-1).

Output in <iro_analysis> tags.

---

**STEP 6: CLIMATE SCENARIO ANALYSIS**

If ESRS E1 (Climate Change) is in the reporting requirements, conduct climate scenario analysis. If E1 is not applicable, briefly note this and skip the detailed analysis.

For E1 companies, provide:

**Scenarios analysed:**
- 1.5°C scenario (NGFS Net Zero 2050 / IEA NZE)
- 2°C scenario (NGFS Delayed Transition)
- 3°C+ scenario (NGFS Current Policies)

**For each scenario:**
- Key assumptions and transition pathway
- Physical risk impacts (flooding, heat stress, water scarcity, etc.)
- Transition risk impacts (carbon pricing, stranded assets, regulatory changes)
- Financial implications (revenue, costs, capex)
- Time horizons: 2030, 2040, 2050

**Resilience assessment**: How well can the company adapt its strategy?

Output in <climate_scenario_analysis> tags.

---

**STEP 7: GENERATE COMPREHENSIVE ESG REPORT**

Compile all analyses into a structured CSRD-compliant ESG report with the following sections:

## 1. Executive Summary
- Company overview and reporting scope
- Reporting wave and applicable standards
- Key material topics summary
- Most significant findings

## 2. General Information (ESRS 2)
- Basis for preparation (ESRS 1 & 2)
- Governance structure (GOV-1 through GOV-5)
- Strategy and business model (SBM-1 through SBM-3)
- IRO management approach (IRO-1, IRO-2)

## 3. Environmental Disclosures
For each applicable E standard (E1-E5):
- Policies and commitments (with ESRS disclosure reference)
- Targets and progress
- Actions and resources allocated
- Metrics and KPIs (in tables with units)

## 4. Social Disclosures
For each applicable S standard (S1-S4):
- Policies and due diligence
- Targets
- Actions
- Metrics and KPIs

## 5. Governance Disclosures (G1)
- Business conduct policies
- Anti-corruption and anti-bribery programme
- Political engagement and lobbying
- Payment practices

## 6. Double Materiality Assessment Results (summary)

## 7. IRO Analysis Summary

## 8. Climate Scenario Analysis Summary (if E1 applicable)

## 9. Data Quality and Limitations

## 10. Forward-Looking Statements and Targets

Use clear headings, tables for quantitative data, and reference specific ESRS disclosure codes throughout (e.g., "ESRS E1-6", "ESRS S1-1").

Output in <esg_report> tags.

---

**STEP 8: GENERATE XBRL FILE SPECIFICATION**

Provide the technical specifications for XBRL digital reporting:

- **Taxonomy**: ESRS XBRL Taxonomy (EFRAG ESRS Set 1, latest version)
- **Filing format**: Inline XBRL (iXBRL) embedded in HTML
- **Namespace prefixes**: List all required namespace declarations
- **Data point mapping table**: Map each reported metric to its XBRL element
  - ESRS Disclosure Reference | Metric Name | XBRL Element | Data Type | Unit | Value
- **Mandatory vs optional tagging**: Indicate which elements are mandatory
- **Period types**: Instant vs duration for each element
- **Validation rules**: Key EFRAG XBRL validation checks to apply
- **File structure**: Required document components (taxonomy reference, facts, contexts, units)
- **Technical notes**: Software/tools recommended for XBRL generation

Output in <xbrl_specifications> tags.

---

Begin your analysis now. Be thorough, professional, and use ESRS-compliant language throughout. Reference specific ESRS disclosure requirements wherever applicable."""


# ─── Streaming analysis ───────────────────────────────────────────────────────

async def stream_csrd_analysis(
    company_data: Dict[str, Any],
    reporting_requirements: List[str],
    raw_data: str,
    api_key: Optional[str] = None,
) -> AsyncGenerator[str, None]:
    """
    Async generator that streams the CSRD analysis from Claude.
    Yields SSE-formatted text chunks.
    """
    try:
        import anthropic
    except ImportError:
        yield "data: [ERROR] Anthropic package not installed. Run: pip install anthropic\n\n"
        return

    if not api_key:
        yield "data: [ERROR] ANTHROPIC_API_KEY not configured. Please set the environment variable.\n\n"
        return

    prompt = build_csrd_prompt(company_data, reporting_requirements, raw_data)

    try:
        client = anthropic.AsyncAnthropic(api_key=api_key)

        async with client.messages.stream(
            model="claude-sonnet-4-6",
            max_tokens=16000,
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            async for text in stream.text_stream:
                # Escape newlines for SSE and send chunk
                # Send the raw text — frontend accumulates it
                escaped = text.replace("\n", "\\n")
                yield f"data: {escaped}\n\n"

        yield "data: [DONE]\n\n"

    except anthropic.AuthenticationError:
        yield "data: [ERROR] Invalid Anthropic API key. Please check your ANTHROPIC_API_KEY.\n\n"
    except anthropic.RateLimitError:
        yield "data: [ERROR] Rate limit exceeded. Please try again in a moment.\n\n"
    except Exception as e:
        logger.error(f"CSRD agent streaming error: {e}", exc_info=True)
        yield f"data: [ERROR] Analysis failed: {str(e)}\n\n"


# ─── Section parser (post-stream) ─────────────────────────────────────────────

def parse_agent_sections(full_text: str) -> Dict[str, str]:
    """
    Extract XML-tagged sections from the full Claude response.
    Returns a dict mapping step_id → content.
    """
    results = {}
    for step in AGENT_STEPS:
        tag = step["xml_tag"]
        step_id = step["id"]
        pattern = rf"<{tag}>([\s\S]*?)</{tag}>"
        match = re.search(pattern, full_text, re.IGNORECASE)
        if match:
            results[step_id] = match.group(1).strip()
        else:
            results[step_id] = ""
    return results
