# Matching with Rules (`rules.yaml`)

Rules provide a powerful, declarative way to match requests using a combination of attributes and direct the response. They are defined in a `rules.yaml` file within a service directory and take precedence over filesystem matching.

---

## Schema

The `rules.yaml` file contains a list of rule objects. Each rule has a `when` block for matching criteria and a `respond` block for the action.

```yaml
rules:
  - when:
      method: GET # Can be a string or a list: [GET, POST]
      path: /repos/{owner}/{repo}/issues
      query:
        sort: created
        order: desc
      body:
        # Match a subset of the JSON body
        json: { q: "is:open" }
        # Alternatively, match a substring in the raw body
        # contains: "raw substring"
    respond:
      # Path to the response file, can use captured path variables
      file: GET/repos/{owner}/{repo}/issues.001.json
      status: 201
      headers:
        X-Rule-Matched: 'true'
      delay_ms: 25
```

### Key Details

  * **Path Variables**: Path segments enclosed in braces (e.g., `{owner}`) capture values from the URL. These are available in `req.path_params` for [templating](../features/templating.md) and can be used in the `respond.file` path.
  * **Body Matching**: `body.json` performs a **subset match**. All key-value pairs in the rule's `json` block must be present in the request body for it to match.
  * **Query Matching**: The `query` block requires an exact match of key-value pairs (order is not important).
  * **Response without File**: You can omit the `file` key in the `respond` block to return a response with only a status, headers, and/or delay.

<!-- end list -->
