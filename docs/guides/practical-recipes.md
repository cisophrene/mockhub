# Practical Recipes

Here are some common patterns and solutions for advanced mocking scenarios.

---

### A) Multiple Ways to Vary a POST Response

1.  **Filename Predicate (`__b.`)**: For simple key-value matches.
    * `POST/repos__b.name=my-repo.json`

2.  **Rules (`rules.yaml`)**: For matching multiple fields, query params, or complex conditions.
    ```yaml
    rules:
      - when:
          method: POST
          path: /search/issues
          body: { json: { q: "is:open", author: "user" } }
        respond:
          file: POST/search_result.json
    ```

3.  **Hook (`__hooks.py`)**: For complex logic, validation, or conditional responses.
    ```python
    def handle(ctx):
        if ctx.request["path"] == "/repos":
            body = ctx.request.get("body_json") or {}
            if not body.get("name"):
                return {"status": 422, "body": {"message": "Name is required"}}
        return None
    ```

### B) Simulate Rate Limiting

Use a [sequence](../features/sequences.md) to return a rate limit error, followed by a success response.

* `GET/rate_limit.001.json`
* `GET/rate_limit.001.meta.yaml`:
    ```yaml
    status: 429
    headers:
      Retry-After: 60
      X-RateLimit-Remaining: 0
    ```
* `GET/rate_limit.002.json`: `{"status": "ok"}`

### C) Record State Across Requests

Use the `state` object in a [hook](../features/hooks.md) or [template](../features/templating.md).

* **In a hook**: `ctx.state["last_created_id"] = new_id`
* **In a template**: `{"previous_id": "{{ state.last_created_id }}"}`

### D) Handle Plain Text Bodies

In a hook, `ctx.request["body_json"]` will be `None` if the `Content-Type` is not JSON. You can read the raw data from `ctx.request["body_raw"]`.
