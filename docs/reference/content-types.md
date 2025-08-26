# Content Types & Bodies

MockHub handles various content types and request bodies.

---

## Response Content-Type

The `Content-Type` header of a response is determined as follows:

1.  **File-based responses** infer the `Content-Type` from the file extension:
    * `*.json`, `*.json.j2` → `application/json`
    * `*.txt`, `*.txt.j2` → `text/plain`
    * Anything else → `application/octet-stream`

2.  **Hook-based responses** have their `Content-Type` set automatically if the `body` is a `dict` or `list` (`application/json`). You can set it explicitly in the `headers` dictionary for other types like strings or bytes.

This default behavior can be overridden by setting the `Content-Type` header in [sidecar metadata](../features/metadata.md) or a [rule](../matching/rules.md).

---

## Request Body Handling

* If a request includes a `Content-Type` header of `application/json`, MockHub will attempt to parse the body as JSON.
* The parsed body is available in [templates](../features/templating.md) as `req.body` and in [hooks](../features/hooks.md) as `ctx.request["body_json"]`.
* The raw, unparsed request body is always available as bytes in a hook (`ctx.request["body_raw"]`) for handling non-JSON content like `text/plain` or `application/x-www-form-urlencoded`.
