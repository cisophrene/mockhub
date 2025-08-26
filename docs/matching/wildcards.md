# Path Wildcards

You can capture dynamic parts of a request's path in two ways: declaratively with [Rules](rules.md) or directly in the filesystem with filename wildcards.

---

## A) Path Templates in Rules

This is the most flexible approach. You define a path with placeholders in your `rules.yaml` file.

**`rules.yaml`:**
```yaml
rules:
  - when:
      method: GET
      path: /repos/{owner}/{repo}/issues
    respond:
      file: GET/repos/{owner}/{repo}/issues.001.json
```

The captured variables (`owner`, `repo`) are then available for use in the `respond.file` path and within [Jinja2 templates](../features/templating.md) as `req.path_params`.

-----

## B) Wildcards in Filenames

For simpler cases that don't require the full power of rules, you can embed wildcards directly into your file and directory names. A wildcard is any name enclosed in double underscores (e.g., `__owner__`).

**File Path:**
`GET/repos/__owner__/__repo__/issues.json.j2`

When a request like `GET /repos/google/mockhub/issues` is made, MockHub will match this file and make the captured values available in the Jinja2 context:

  * `req.path_params.owner` will be `"google"`
  * `req.path_params.repo` will be `"mockhub"`

### When to Choose Which?

  * Use **rules** when you need to centralize matching logic, handle multiple conditions for the same path pattern, or match on more than just the path.
  * Use **file wildcards** for quick, file-only setups where the path structure is the primary matching criterion.
