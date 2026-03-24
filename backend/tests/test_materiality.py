"""Tests for Double Materiality Assessment."""
import pytest
from services.materiality_service import (
    calculate_impact_score,
    calculate_financial_score,
    is_material,
)


def test_impact_score_high():
    score = calculate_impact_score(5, 5, 5, 5, is_negative=True)
    assert score > 70


def test_impact_score_low():
    score = calculate_impact_score(1, 1, 1, 1, is_negative=True)
    assert score < 30


def test_financial_score_calculation():
    score = calculate_financial_score(5, 5)
    assert score == 100.0


def test_financial_score_medium():
    score = calculate_financial_score(3, 3)
    assert 30 < score < 50


def test_materiality_threshold():
    assert is_material(50, 10) is True   # impact material
    assert is_material(10, 50) is True   # financial material
    assert is_material(45, 45) is True   # dual material
    assert is_material(20, 20) is False  # not material


def test_get_materiality_topics(client, auth_headers):
    proj = client.post("/api/projects", json={
        "name": "Materiality Test", "reporting_year": 2024,
    }, headers=auth_headers).json()
    pid = proj["id"]

    res = client.get(f"/api/projects/{pid}/materiality/topics", headers=auth_headers)
    assert res.status_code == 200
    topics = res.json()
    # Should auto-create default ESRS topics
    assert len(topics) == 10
    standards = {t["esrs_standard"] for t in topics}
    assert "E1" in standards
    assert "S1" in standards
    assert "G1" in standards


def test_update_topic_score(client, auth_headers):
    proj = client.post("/api/projects", json={
        "name": "Score Update Test", "reporting_year": 2024,
    }, headers=auth_headers).json()
    pid = proj["id"]

    topics = client.get(
        f"/api/projects/{pid}/materiality/topics", headers=auth_headers
    ).json()
    topic_id = topics[0]["id"]

    res = client.put(
        f"/api/projects/{pid}/materiality/topics/{topic_id}",
        json={
            "topic_id": topic_id,
            "impact_scale": 4.5,
            "impact_scope": 4.0,
            "impact_irremediability": 4.0,
            "impact_likelihood": 4.5,
            "financial_magnitude": 4.0,
            "financial_likelihood": 4.0,
        },
        headers=auth_headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["impact_score"] is not None
    assert data["impact_score"] > 0


def test_materiality_heatmap(client, auth_headers):
    proj = client.post("/api/projects", json={
        "name": "Heatmap Test", "reporting_year": 2024,
    }, headers=auth_headers).json()
    pid = proj["id"]
    client.get(f"/api/projects/{pid}/materiality/topics", headers=auth_headers)

    res = client.get(f"/api/projects/{pid}/materiality/heatmap", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "data_points" in data
    assert "threshold" in data
