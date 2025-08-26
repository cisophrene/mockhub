# Jinja2 Templating

MockHub uses the Jinja2 templating engine to enable dynamic response payloads. Any file ending with a `.j2` extension (e.g., `.json.j2`, `.txt.j2`) will be rendered before being served.

---

## Rendering Context

Templates are rendered with a rich context object, giving you access to request data, session state, and useful helpers.

```json
{
  "req": {
    "method": "GET"|"POST"|...,
    "path": "/full/path",
    "path_segments": ["repos", "octo", "hello", "issues"],
    "path_params": {"owner": "octo", "repo": "hello"}, // from wildcards
    "query": {"key": ["v1", "v2"]},
    "headers": {"content-type": "application/json", ...},
    "body": { ... },                     // parsed JSON body (if any)
    "body_raw": "..."                    // raw body as string
  },
  "state": {...},                        // mutable dict shared across requests
  "now": "2025-08-26T12:34:56Z",         // helper: current time in ISO format
  "uuid4": "a1b2c3d4-e5f6-..."           // helper: random UUID
}
```

### Example (`POST/repos.001.json.j2`)

This template uses data from the request body (`req.body.name`), generates a random UUID, and references a value stored in the session `state`.

```json
{
  "id": "{{ uuid4 }}",
  "name": "{{ req.body.name }}",
  "created_at": "{{ now }}",
  "note": "This repo was created dynamically. Last repo: {{ state.last_repo }}"
}
```

> **Strict Undefineds**: MockHub is configured to fail fast. If you reference a variable in your template that doesn't exist in the context (e.g., `{{ req.body.missing_key }}`), the server will return an `HTTP 500 Internal Server Error` with a descriptive message. This helps you catch errors early.
