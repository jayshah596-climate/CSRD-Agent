"""
XBRL Instance Document Generator
Produces ESRS-compliant XBRL iXBRL output.
"""

from typing import Dict, Any, Optional
from datetime import date
from .taxonomy import ESRS_NAMESPACE, ESRS_PREFIX, get_xbrl_tag
import xml.etree.ElementTree as ET
import xml.dom.minidom


def generate_xbrl_instance(
    company_data: Dict[str, Any],
    report_data: Dict[str, Any],
    reporting_year: int,
) -> str:
    """
    Generate an XBRL instance document for ESRS disclosures.
    Returns XML string.
    """
    # Root element
    root = ET.Element("xbrl")
    root.set("xmlns", "http://www.xbrl.org/2003/instance")
    root.set("xmlns:xbrli", "http://www.xbrl.org/2003/instance")
    root.set("xmlns:xbrldi", "http://xbrl.org/2006/xbrldi")
    root.set("xmlns:link", "http://www.xbrl.org/2003/linkbase")
    root.set("xmlns:xlink", "http://www.w3.org/1999/xlink")
    root.set(f"xmlns:{ESRS_PREFIX}", ESRS_NAMESPACE)
    root.set("xmlns:iso4217", "http://www.xbrl.org/2003/iso4217")

    # Schema reference
    schema_ref = ET.SubElement(root, "link:schemaRef")
    schema_ref.set("xlink:type", "simple")
    schema_ref.set("xlink:href", f"{ESRS_NAMESPACE}/esrs-all.xsd")

    # Context
    period_start = f"{reporting_year}-01-01"
    period_end = f"{reporting_year}-12-31"
    entity_id = company_data.get("lei_code") or company_data.get("registration_number", "UNKNOWN")

    context = ET.SubElement(root, "xbrli:context")
    context.set("id", f"ctx_{reporting_year}")
    entity = ET.SubElement(context, "xbrli:entity")
    identifier = ET.SubElement(entity, "xbrli:identifier")
    identifier.set("scheme", "http://www.gleif.org/data/schema/leidata/2016")
    identifier.text = entity_id

    period = ET.SubElement(context, "xbrli:period")
    start_date = ET.SubElement(period, "xbrli:startDate")
    start_date.text = period_start
    end_date = ET.SubElement(period, "xbrli:endDate")
    end_date.text = period_end

    # Unit for monetary values
    unit_eur = ET.SubElement(root, "xbrli:unit")
    unit_eur.set("id", "EUR")
    measure_eur = ET.SubElement(unit_eur, "xbrli:measure")
    measure_eur.text = "iso4217:EUR"

    # Unit for tonnes CO2e
    unit_tco2 = ET.SubElement(root, "xbrli:unit")
    unit_tco2.set("id", "tCO2e")
    measure_tco2 = ET.SubElement(unit_tco2, "xbrli:measure")
    measure_tco2.text = "xbrli:pure"

    # Facts
    emissions = report_data.get("emissions", {})
    workforce = report_data.get("workforce", {})
    energy = report_data.get("energy", {})

    fact_mappings = [
        ("E1-6_scope1_emissions", emissions.get("scope_1_total"), "tCO2e"),
        ("E1-6_scope2_location", emissions.get("scope_2_location_total"), "tCO2e"),
        ("E1-6_scope2_market", emissions.get("scope_2_market_total"), "tCO2e"),
        ("E1-6_scope3_total", emissions.get("scope_3_total"), "tCO2e"),
        ("E1-6_total_ghg", emissions.get("total_ghg"), "tCO2e"),
        ("E1-5_total_energy", energy.get("total_mwh"), "tCO2e"),
        ("E1-5_renewable_pct", energy.get("renewable_pct"), "tCO2e"),
        ("S1-6_employee_total", workforce.get("total_employees"), "tCO2e"),
        ("S1-14_ltir", workforce.get("ltir"), "tCO2e"),
        ("S1-16_gender_pay_gap", workforce.get("gender_pay_gap"), "tCO2e"),
    ]

    for dp_id, value, unit_ref in fact_mappings:
        if value is None:
            continue
        xbrl_tag = get_xbrl_tag(dp_id)
        tag_prefix, tag_local = xbrl_tag.split(":")
        fact = ET.SubElement(root, xbrl_tag)
        fact.set("contextRef", f"ctx_{reporting_year}")
        fact.set("unitRef", unit_ref)
        fact.set("decimals", "2")
        fact.text = str(round(float(value), 4))

    # Pretty print
    xml_str = ET.tostring(root, encoding="unicode", xml_declaration=False)
    dom = xml.dom.minidom.parseString(f"<?xml version='1.0' encoding='UTF-8'?>{xml_str}")
    return dom.toprettyxml(indent="  ")


def generate_ixbrl_report(
    company_data: Dict[str, Any],
    report_data: Dict[str, Any],
    reporting_year: int,
    html_content: str,
) -> str:
    """
    Generate an iXBRL (inline XBRL) document embedding XBRL tags in HTML.
    Returns HTML string with inline XBRL tags.
    """
    entity_id = company_data.get("lei_code", "UNKNOWN")
    period_start = f"{reporting_year}-01-01"
    period_end = f"{reporting_year}-12-31"

    ixbrl_header = f"""<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:ix="http://www.xbrl.org/2013/inlineXBRL"
      xmlns:{ESRS_PREFIX}="{ESRS_NAMESPACE}"
      xmlns:xbrli="http://www.xbrl.org/2003/instance"
      xmlns:iso4217="http://www.xbrl.org/2003/iso4217">
<head>
  <title>ESRS Sustainability Report {reporting_year} - {company_data.get('name', '')}</title>
  <ix:header>
    <ix:hidden>
      <ix:context id="ctx_{reporting_year}">
        <xbrli:entity>
          <xbrli:identifier scheme="http://www.gleif.org/data/schema/leidata/2016">{entity_id}</xbrli:identifier>
        </xbrli:entity>
        <xbrli:period>
          <xbrli:startDate>{period_start}</xbrli:startDate>
          <xbrli:endDate>{period_end}</xbrli:endDate>
        </xbrli:period>
      </ix:context>
      <xbrli:unit id="tCO2e"><xbrli:measure>xbrli:pure</xbrli:measure></xbrli:unit>
      <xbrli:unit id="EUR"><xbrli:measure>iso4217:EUR</xbrli:measure></xbrli:unit>
    </ix:hidden>
  </ix:header>
</head>
<body>
"""

    ixbrl_footer = "\n</body>\n</html>"

    return ixbrl_header + html_content + ixbrl_footer


def generate_taxonomy_mapping(report_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a summary taxonomy mapping document."""
    mappings = []
    from .taxonomy import XBRL_TAGS

    for dp_id, xbrl_tag in XBRL_TAGS.items():
        value = None
        # Try to find value in report data
        for section, section_data in report_data.items():
            if isinstance(section_data, dict) and dp_id in section_data:
                value = section_data[dp_id]
                break

        mappings.append({
            "datapoint_id": dp_id,
            "xbrl_tag": xbrl_tag,
            "namespace": ESRS_NAMESPACE,
            "value": value,
            "is_tagged": value is not None,
        })

    return {
        "taxonomy_version": "ESRS XBRL 2024",
        "namespace": ESRS_NAMESPACE,
        "total_tags": len(XBRL_TAGS),
        "tagged_facts": sum(1 for m in mappings if m["is_tagged"]),
        "mappings": mappings,
    }
