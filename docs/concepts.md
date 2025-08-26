# Core Concepts & Directory Layout

MockHub's behavior is driven by a simple yet powerful directory structure. Understanding this layout is key to creating effective mock scenarios.

---

## Directory Structure

All mock data lives inside the `payloads/` directory. Here is the basic hierarchy:

```
payloads/
  <scenario>/
    <service>/
      rules.yaml          # Optional – rules evaluated before files
      __hooks.py          # Optional – Python hook executed before rules
      GET/
      POST/
      PUT/
      PATCH/
      DELETE/
      HEAD/
      OPTIONS/
        ... files ...
```

* **Scenario**: A top-level folder under `payloads/`. Each scenario represents a complete, self-contained set of mock responses for one or more services. You switch between scenarios using the [Control API](control-api.md).

* **Service**: A sub-folder within a scenario, representing one mocked API (e.g., `github`). Each service is mapped to a unique port.

* **Method Directories**: Inside each service, requests are routed based on their HTTP method (e.g., `GET/`, `POST/`).

* **Files**: These are the actual response payloads, typically JSON or text files. They can be enhanced with [sequencing](features/sequences.md) (`.001.json`) or [templating](features/templating.md) (`.json.j2`).

* **Sidecar Metadata**: An optional `*.meta.yaml` file placed next to a payload file to define custom [status codes, headers, and latency](features/metadata.md).

* **Rules**: An optional `rules.yaml` file per service to define [declarative matching logic](matching/rules.md).

* **Hooks**: An optional `__hooks.py` file per service to implement [fully dynamic responses](features/hooks.md) in Python.

---

## Request Resolution Order

For every incoming request to a service port, MockHub attempts to find a response in the following order:

1.  **Python Hook (`__hooks.py`)**: If the `handle` function in the hook returns a response, that response is used immediately. This is the highest level of precedence.

2.  **Rules (`rules.yaml`)**: If the hook returns `None`, MockHub evaluates the rules in `rules.yaml`. The first matching rule wins.

3.  **Filesystem**: If no hook or rule matches, MockHub searches the filesystem for a corresponding file based on the request's method, path, [query string](matching/query-strings.md), and [body predicates](matching/body-predicates.md).

If no match is found after checking all three layers, MockHub returns an `HTTP 404 Not Found` response.
