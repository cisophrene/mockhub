# Reference Cheatsheet

A quick summary of syntax and APIs.

---

## Filename Syntax

* **Base**: `{METHOD}/{path}.json`
* **Directory Index**: `{METHOD}/{dir}/_index.json`
* **Query Variant**: `...__q.k1=v1&k2=v2.json` (keys/values sorted)
* **Body Predicate**: `...__b.key=value.json`
* **Sequence**: `....001.json`, `....002.json`
* **Template**: Any of the above with a `.j2` suffix (e.g., `.json.j2`)
* **Metadata**: Add `.meta.yaml` next to any payload file.

---

## Rules (`rules.yaml`) Fields

* `when.method`: A string or list of strings.
* `when.path`: A string, may include `{var}` placeholders.
* `when.query`: A map of key-value pairs for exact matching.
* `when.body.json`: A dictionary for subset matching against a JSON body.
* `when.body.contains`: A string for substring matching in the raw body.
* `respond.file`: A relative path to a payload file.
* `respond.status`, `respond.headers`, `respond.delay_ms`: Overrides.

---

## Hook (`__hooks.py`) API

* **Signature**: `def handle(ctx): ...`
* `ctx.request`: Dict with `method`, `path`, `query`, `headers`, `body_json`, `body_raw`.
* `ctx.state`: A dictionary shared within the session.
* `ctx.now()`: Returns current time as an ISO UTC string.
* `ctx.uuid4()`: Returns a random UUID string.
* `ctx.render_file(rel_path, extra_context={})`: Renders a template file.
* **Return Value**: `None` (fall through), `str` (file path), or `dict` (full response).
