import os
import pytest
from fastapi.testclient import TestClient

def test_rules_yaml_path_template_matching(client: TestClient, scenario_root):
    # Create necessary files for the test
    scenario_name = "rules_path_template"

    # Start session with the scenario
    client.post("/control/session/start", json={"scenario": scenario_name})

    # Create a client for GitHub service port
    github_client = TestClient(client.app, base_url="http://testserver:27001")

    # Request should match the rule and serve the file
    resp = github_client.get("/repos/octo/hello/issues")
    assert resp.status_code == 200
    assert resp.json() == [{"number": 1, "title": "Test issue"}]

def test_rules_override_status_headers(client: TestClient, scenario_root):
    # Create necessary files for the test
    scenario_name = "rules_override"

    # Start session with the scenario
    client.post("/control/session/start", json={"scenario": scenario_name})

    # Create a client for GitHub service port
    github_client = TestClient(client.app, base_url="http://testserver:27001")

    # Request should match the rule and use the rule's status/headers
    resp = github_client.get("/repos/octo/hello/issues")
    assert resp.status_code == 201  # From rule, not 200 from meta
    assert resp.headers.get("X-MockHub-Rule") == "applied"
    assert resp.headers.get("X-Test-Header") == "custom-value"
    assert resp.headers.get("X-MockHub-File") == "original"  # File headers are preserved

def test_rules_body_and_query_predicates(client: TestClient, scenario_root):
    # Create necessary files for the test
    scenario_name = "rules_predicates"

    # Start session with the scenario
    client.post("/control/session/start", json={"scenario": scenario_name})

    # Create a client for GitHub service port
    github_client = TestClient(client.app, base_url="http://testserver:27001")

    # Request with matching query and body should succeed
    resp = github_client.post(
        "/search/issues?sort=created&order=desc",
        json={"q": "is:open"},
        headers={"Content-Type": "application/json"}
    )
    assert resp.status_code == 200
    assert resp.headers.get("X-MockHub-Match") == "complete"
    assert resp.json() == {"items": [{"number": 42, "title": "Matched issue"}]}

    # Request with different query should fail to match
    resp_bad_query = github_client.post(
        "/search/issues?sort=created&order=asc",  # different order
        json={"q": "is:open"},
        headers={"Content-Type": "application/json"}
    )
    assert resp_bad_query.status_code == 404  # No match, no fallback

    # Request with different body should fail to match
    resp_bad_body = github_client.post(
        "/search/issues?sort=created&order=desc",
        json={"q": "is:closed"},  # different query
        headers={"Content-Type": "application/json"}
    )
    assert resp_bad_body.status_code == 404  # No match, no fallback
