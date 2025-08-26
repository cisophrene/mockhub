import os
import pytest
from fastapi.testclient import TestClient

@pytest.fixture(scope="session")
def scenario_root():
    # Point tests to scenarios under tests/scenarios (not payloads/)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "scenarios"))

@pytest.fixture
def client(scenario_root, monkeypatch):
    # Ensure the app uses tests/scenarios as PAYLOADS_ROOT
    monkeypatch.setenv("MOCKHUB_PAYLOADS_ROOT", scenario_root)
    # Import after env var is set so config picks it up
    from src.mockhub.app import create_app
    app = create_app()
    return TestClient(app)
