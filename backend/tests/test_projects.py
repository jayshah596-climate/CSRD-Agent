"""Tests for project management endpoints."""
import pytest


def test_create_project(client, auth_headers):
    res = client.post("/api/projects", json={
        "name": "Test CSRD Project",
        "reporting_year": 2024,
        "esrs_standards": ["E1", "S1", "G1"],
    }, headers=auth_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "Test CSRD Project"
    assert data["reporting_year"] == 2024
    assert data["status"] == "draft"
    return data["id"]


def test_list_projects(client, auth_headers):
    client.post("/api/projects", json={
        "name": "List Test Project", "reporting_year": 2024,
    }, headers=auth_headers)
    res = client.get("/api/projects", headers=auth_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)
    assert len(res.json()) >= 1


def test_get_project(client, auth_headers):
    create_res = client.post("/api/projects", json={
        "name": "Get Test", "reporting_year": 2024,
    }, headers=auth_headers)
    pid = create_res.json()["id"]
    res = client.get(f"/api/projects/{pid}", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["id"] == pid


def test_get_project_not_found(client, auth_headers):
    res = client.get("/api/projects/00000000-0000-0000-0000-000000000000", headers=auth_headers)
    assert res.status_code == 404


def test_update_project(client, auth_headers):
    create_res = client.post("/api/projects", json={
        "name": "Update Test", "reporting_year": 2024,
    }, headers=auth_headers)
    pid = create_res.json()["id"]
    res = client.put(f"/api/projects/{pid}", json={"name": "Updated Name"}, headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["name"] == "Updated Name"


def test_project_progress(client, auth_headers):
    create_res = client.post("/api/projects", json={
        "name": "Progress Test", "reporting_year": 2024,
    }, headers=auth_headers)
    pid = create_res.json()["id"]
    res = client.get(f"/api/projects/{pid}/progress", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "progress_pct" in data
    assert "steps" in data
    assert data["progress_pct"] == 0


def test_delete_project(client, auth_headers):
    create_res = client.post("/api/projects", json={
        "name": "Delete Test", "reporting_year": 2024,
    }, headers=auth_headers)
    pid = create_res.json()["id"]
    res = client.delete(f"/api/projects/{pid}", headers=auth_headers)
    assert res.status_code == 204
    get_res = client.get(f"/api/projects/{pid}", headers=auth_headers)
    assert get_res.status_code == 404
