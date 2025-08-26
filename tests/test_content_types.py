import os
import pytest
from fastapi.testclient import TestClient

def test_json_content_type_for_json_and_j2(client: TestClient):
    # Create a temporary scenario with JSON and template files
    scenario_name = "content_types"
    
    # Start session with the scenario
    client.post("/control/session/start", json={"scenario": scenario_name})
    
    # Create a client for GitHub service port
    github_client = TestClient(client.app, base_url="http://testserver:27001")
    
    # Test regular JSON file
    json_resp = github_client.get("/data.json")
    assert json_resp.status_code == 200
    assert json_resp.headers["Content-Type"] == "application/json"
    assert json_resp.json() == {"message": "This is JSON data"}
    
    # Test Jinja2 template that produces JSON
    template_resp = github_client.get("/template")
    assert template_resp.status_code == 200
    assert template_resp.headers["Content-Type"] == "application/json"
    assert template_resp.json()["message"] == "This is a template"
    assert template_resp.json()["method"] == "GET"
    assert template_resp.json()["path"] == "/template"

def test_plain_text_content_type(client: TestClient):
    # Start session with content_types scenario
    client.post("/control/session/start", json={"scenario": "content_types"})
    
    # Create a client for GitHub service port
    github_client = TestClient(client.app, base_url="http://testserver:27001")
    
    # Test plain text file
    resp = github_client.get("/hello.txt")
    assert resp.status_code == 200
    assert resp.headers["Content-Type"] == "text/plain"
    assert "Hello, world!" in resp.text

def test_non_json_body_passthrough(client: TestClient):
    # Start session with content_types scenario
    client.post("/control/session/start", json={"scenario": "content_types"})
    
    # Create a client for GitHub service port
    github_client = TestClient(client.app, base_url="http://testserver:27001")
    
    # Test POST with plain text body
    plain_text = "This is plain text content"
    resp = github_client.post(
        "/echo-plain",
        content=plain_text,
        headers={"Content-Type": "text/plain"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["echo"] is True
    assert data["content_type"] == "text/plain"
    assert data["body_json"] is None  # Should be None for non-JSON content
    assert data["body_raw"] == plain_text
    
    # Test POST with JSON body to template that echoes request
    json_data = {"test": "value"}
    resp = github_client.post(
        "/echo",
        json=json_data,
        headers={"Content-Type": "application/json"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["echo"] is True
    assert "application/json" in data["content_type"].lower()
    assert data["body_json"] == json_data
