# Python Hooks (`__hooks.py`)

Hooks provide the ultimate level of control by allowing you to execute Python code to generate a response dynamically. Hooks run **before** any rules or files are checked.

---

## Implementation

Create a file named `__hooks.py` in a service's directory. This file can contain functions named `handle` and/or `transform` that accept context arguments.

**`payloads/<scenario>/<service>/__hooks.py`:**
```python
def handle(ctx):
    # ctx provides access to:
    # - ctx.request: A dict with method, path, query, headers, body_json, body_raw
    # - ctx.state: A dict to persist values across requests in the session
    # - ctx.now(), ctx.uuid4(): Helper functions
    # - ctx.render_file(path, extra_context={}): Renders a .j2 file

    # Example 1: Return a direct response
    if ctx.request["method"] == "POST" and ctx.request["path"] == "/repos":
        name = (ctx.request.get("body_json") or {}).get("name")
        if name == "special-case":
            ctx.state["last_repo"] = name
            return {
                "status": 200,
                "body": {"id": ctx.uuid4(), "note": f"Hook processed this."}
            }

    # Example 2: Delegate to a template file
    if ctx.request["path"] == "/delegate":
        return ctx.render_file("POST/repos.001.json.j2")

    # Fall through to rules/files
    return None

def transform(ctx, payload):
    # Transform an existing payload after it has been resolved by rules/files
    # payload contains: status, headers, delay_ms, and body (as bytes or dict)
    # Return a modified payload dict or None to leave unchanged
    
    # Example: Add common fields to all JSON responses
    if ctx.request["path"] == "/api/data":
        if isinstance(payload.get("body"), dict):
            payload["body"]["transformed"] = True
            payload["body"]["timestamp"] = ctx.now()
        return payload
    
    # Example: Modify specific endpoints
    if ctx.request["path"] == "/user/profile":
        # Add authorization header to all responses for this endpoint
        payload["headers"]["X-Authorization"] = "Bearer " + ctx.state.get("token", "default-token")
        return payload
    
    # Leave payload unchanged
    return None
```

-----

## Hook Functions

There are two types of hook functions you can define:

### `handle(ctx)` – Pre-resolution Hook
This function runs **before** any rules or files are checked. It can return:
* **`None`**: The hook does not handle the request. MockHub proceeds to check [Rules](../matching/rules.md) and then the filesystem.
* **`str`**: A string is treated as a relative path to a payload file. This file will be rendered (if it's a template) and served.
* **`dict`**: A dictionary defines a complete response. It can contain `status`, `headers`, `delay_ms`, and `body` keys. The `body` can be a dict/list (auto-encoded to JSON), a string, or bytes.

### `transform(ctx, payload)` – Post-resolution Hook
This function runs **after** a response payload has been resolved through rules or filesystem matching. It receives:
* **`ctx`**: The same context object as `handle`
* **`payload`**: A dictionary containing the resolved response with `status`, `headers`, `delay_ms`, and `body` keys

The `transform` function can modify and return the payload to alter the final response. If it returns `None` or an invalid value, the payload is sent as-is.

Any exception raised within either hook will result in an `HTTP 500 Hook error` response.
