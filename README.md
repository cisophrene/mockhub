# MockHub

Local HTTP mock server to simulate third-party APIs for integration and behavior-driven development (BDD) tests.

MockHub allows you to create realistic mock APIs by defining scenarios in a file-based structure. Each scenario represents a complete set of responses for one or more services, which can be activated dynamically via a Control API without requiring changes to your system-under-test (SUT) configuration.

## Key Features

- Scenarios selected via **Control API** (no changes needed in SUT code)
- File-driven responses with optional **YAML rules**, **Python hooks**, and **Jinja2 templating**
- **Sequences** for modeling stateful flows (returns HTTP 410 when exhausted)
- **Hot reload** functionality through on-demand file reads and mtime-based caching
- **HTTP only** on custom ports (no TLS support) with no passthrough for unmatched requests

## Quick Start

For detailed instructions on getting started with MockHub, please refer to our [documentation](https://cisophrene.github.io/mockhub/).

```bash
# Build & run with Docker
docker compose up --build

# Control API (port 27000)
curl -s http://localhost:27000/control/status
curl -s -X POST http://localhost:27000/control/session/start -H "Content-Type: application/json" -d '{"scenario":"github_repo_flow"}'

# Documentation (port 27009)
# Open http://localhost:27009 in your browser
```

Point your SDKs to service ports, for ex:
- GitHub → `http://localhost:27001`
- Shortcut → `http://localhost:27002`
- Zoho → `http://localhost:27003`
- Google → `http://localhost:27004`

Documentation → `http://localhost:27009`

## Filesystem Layout

```
payloads/
  <scenario>/
    <service>/
      rules.yaml        # optional — evaluated before filenames
      __hooks.py        # optional — Python logic evaluated before rules
      GET/ POST/ PUT/ PATCH/ DELETE/  # method directories
```

### Path to File Mapping

- `GET /user/repos` → `GET/user/repos.json`
- Trailing slash maps to `_index.json` inside directory (`GET/issues/` → `GET/issues/_index.json`)
- Query variants append `__q.` + sorted, URL-encoded query string:
  - `GET /search?labels=bug&state=open` → `GET/search__q.labels=bug&state=open.json`
- Body predicates (top-level) in filename using `__b.`:
  - POST body `{"name":"my-repo"}` → `POST/repos__b.name=my-repo.json`

### Sequences

Use numbered files (3-digit format) per endpoint. When all files in a sequence have been served, MockHub responds with HTTP 410.
```
GET/user/repos.001.json
GET/user/repos.002.json
GET/user/repos.003.json
```

### Metadata

For any payload file, you can add a sidecar `<file>.meta.yaml` to control status codes, headers, and simulated latency:
```yaml
status: 201
headers:
  X-MockHub: github
delay_ms: 50
```

### Templating

Render files ending with `.j2` extension. Templates have access to request data, session state, and helper functions.

## Control API (port 27000)

- `POST /control/session/start` — body: `{ "scenario": "my_scenario" }`
- `POST /control/session/reset` — optional body `{ "scenario": "..." }`
- `GET /control/status`

Use in BDD `BeforeScenario` hooks to select scenarios, then run test steps without modifying SUT requests.

## Documentation

MockHub's complete documentation is available at: https://cisophrene.github.io/mockhub/

When running with Docker Compose, documentation is served on port 27009:
1. Run `docker compose up`
2. Open `http://localhost:27009` in your browser

## Development

Run locally:
```bash
pip install -e .
mockhub run
```

## License

MIT
