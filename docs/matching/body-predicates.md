# Matching by Body Predicate

For simple `POST` or `PUT` requests with JSON bodies, you can create response variants by encoding a top-level key-value pair in the filename.

---

## Syntax

Append `__b.` followed by a `key=value` pair to the filename. MockHub will check if the incoming JSON body contains that top-level key with the matching value.

* **Request**: `POST /repos` with body `{ "name": "my-repo", "private": true }`
* **File**: `POST/repos__b.name=my-repo.json`

This also works with sidecar metadata files:

* **Metadata**: `POST/repos__b.name=my-repo.meta.yaml`

> **Important**: This feature is designed for simplicity. MockHub only considers the **first key-value pair** it finds in the JSON body when probing for a file match. For more complex body matching (e.g., nested objects, multiple fields), you should use [Rules](rules.md) instead.
