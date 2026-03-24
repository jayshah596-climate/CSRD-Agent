"""Tests for authentication endpoints."""
import pytest


def test_register_success(client):
    res = client.post("/api/auth/register", json={
        "email": "newuser@test.com",
        "password": "SecurePass123!",
        "full_name": "New User",
        "company_name": "New Company",
    })
    assert res.status_code == 201
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "newuser@test.com"
    assert data["user"]["subscription_tier"] == "free"


def test_register_duplicate_email(client):
    payload = {"email": "dup@test.com", "password": "Pass123!", "full_name": "Dup"}
    client.post("/api/auth/register", json=payload)
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == 400
    assert "already registered" in res.json()["detail"].lower()


def test_login_success(client):
    client.post("/api/auth/register", json={
        "email": "login@test.com",
        "password": "LoginPass123!",
        "full_name": "Login User",
    })
    res = client.post("/api/auth/login", data={
        "username": "login@test.com",
        "password": "LoginPass123!",
    })
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_wrong_password(client):
    client.post("/api/auth/register", json={
        "email": "wrongpw@test.com",
        "password": "CorrectPass123!",
        "full_name": "Wrong",
    })
    res = client.post("/api/auth/login", data={
        "username": "wrongpw@test.com",
        "password": "WrongPassword",
    })
    assert res.status_code == 401


def test_get_me(client, auth_headers):
    res = client.get("/api/auth/me", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["email"] == "test@test.com"


def test_get_me_no_token(client):
    res = client.get("/api/auth/me")
    assert res.status_code == 401


def test_health_check(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"
