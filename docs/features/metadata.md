# Sidecar Metadata (`*.meta.yaml`)

For any payload file, you can create an adjacent `.meta.yaml` file to override the default response behavior, such as setting a custom status code, adding headers, or simulating network latency.

---

## Syntax

Simply create a YAML file with the same name as your payload file, but with `.meta.yaml` appended.

**Example:**
* **Payload file**: `POST/repos__b.name=my-repo.json`
* **Metadata file**: `POST/repos__b.name=my-repo.json.meta.yaml`

**Contents of `*.meta.yaml`:**
```yaml
status: 201
headers:
  X-MockHub: created
delay_ms: 10
```

  * `status`: Overrides the default `200 OK` status code.
  * `headers`: A dictionary of headers to add to the response.
  * `delay_ms`: An integer number of milliseconds to wait before sending the response.

-----

## Precedence

Metadata settings are applied with the following priority:

1.  The `Content-Type` header is first inferred from the payload filename (e.g., `.json` → `application/json`).
2.  Headers from the `.meta.yaml` file are merged on top of this.
3.  If the response is triggered by a [Rule](../matching/rules.md), any `status`, `headers`, or `delay_ms` defined in the rule will override the metadata file's settings.
