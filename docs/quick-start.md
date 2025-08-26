# Quick Start

This guide will get you up and running with MockHub in minutes.

---

## 1. Run with Docker Compose

The easiest way to start is with Docker Compose.

```bash
docker compose up --build
```

This command starts the control server and all predefined mock services.

  * **Control API**: `http://localhost:27000`
  * **Service Ports** (defaults):
      * GitHub → `http://localhost:27001`
      * Shortcut → `http://localhost:27002`
      * Zoho → `http://localhost:27003`
      * Google → `http://localhost:27004`


-----

## 2. Select a Scenario

Before your application can interact with a mocked service, you must start a session and select a scenario using the [Control API](control-api.md).

First, check that the server is healthy:

```bash
# Health Check
curl -s http://localhost:27000/control/health
```

Next, start a session using the `github_repo_flow` scenario:

```bash
# Start a session
curl -s -X POST http://localhost:27000/control/session/start \
  -H 'Content-Type: application/json' \
  -d '{"scenario":"github_repo_flow"}'
```

You can inspect the current status, which includes the active scenario and any sequence counters:

```bash
# Inspect status
curl -s http://localhost:27000/control/status | jq .
```

-----

## 3. Call the Mocked API

Now that a scenario is active, you can make requests to the service ports. This request will be handled by the mock GitHub service on port `27001`.

```bash
# GET /user/repos served from the scenario's filesystem
curl -s http://localhost:27001/user/repos | jq .
```

> **💡 Pro Tip:** In your CI/CD pipeline or test suite, call `/control/session/start` in a "BeforeAll" or "BeforeScenario" hook. This ensures a clean state for each test run. Then, simply point your application's configuration to the MockHub service ports and run your tests as usual.
