import os
import time
import pytest
from fastapi.testclient import TestClient

def test_meta_overrides_status_headers_delay(client: TestClient, scenario_root):
    # Start session with github_repo_flow scenario
    client.post("/control/session/start", json={"scenario": "github_repo_flow"})

    # Create a client for GitHub service port
    github_client = TestClient(client.app, base_url="http://testserver:27001")

    # Ensure the metadata file exists with expected content
    github_dir = os.path.join(scenario_root, "github_repo_flow", "github", "POST")
    os.makedirs(github_dir, exist_ok=True)

    # Create or verify the metadata file
    meta_path = os.path.join(github_dir, "repos__b.name=my-repo.json.meta.yaml")
    with open(meta_path, "w") as f:
        f.write("""status: 201
headers:
  X-MockHub: created
delay_ms: 10""")

    # Measure time to validate delay
    start_time = time.time()

    # POST to /repos with a matching body
    resp = github_client.post(
        "/repos",
        json={"name": "my-repo"},
        headers={"Content-Type": "application/json"}
    )

    # Calculate elapsed time
    elapsed_ms = (time.time() - start_time) * 1000

    # Verify response
    assert resp.status_code == 201
    assert resp.headers.get("X-MockHub") == "created"
    assert resp.json()["name"] == "my-repo"

    # Verify delay (with some tolerance for system variations)
    # This is optional and might be flaky on CI systems
    assert elapsed_ms >= 5, f"Expected delay of at least 5ms, got {elapsed_ms}ms"

def test_invalid_meta_returns_422(client: TestClient, scenario_root):
    # Create a temporary scenario with invalid metadata
    temp_scenario = "temp_invalid_meta"

    # Start session with the temporary scenario
    client.post("/control/session/start", json={"scenario": temp_scenario})

    # Create a client for service port
    service_client = TestClient(client.app, base_url="http://testserver:27001")

    # Request should fail with 422 due to invalid metadata
    resp = service_client.get("/test")
    assert resp.status_code == 422
    assert "Invalid meta" in resp.json()["detail"]
