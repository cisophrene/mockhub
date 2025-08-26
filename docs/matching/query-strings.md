# Matching by Query String

MockHub supports serving different responses based on URL query parameters by encoding the canonical query string into the filename.

---

## Syntax

To create a query-specific variant of a response, append `__q.` followed by the URL-encoded query string to the filename, just before the extension.

**Keys and values must be sorted alphabetically** for order-insensitive matching.

### Example

* **Request**: `GET /search?labels=bug&state=open`
* **File**: `GET/search__q.labels=bug&state=open.json`

This file would also match `GET /search?state=open&labels=bug` because the keys are sorted in the filename.

### Multi-Value Parameters

For parameters that appear multiple times, include them all in the filename, with their values sorted lexicographically.

* **Request**: `GET /search?label=bug&label=security`
* **File**: `GET/search__q.label=bug&label=security.json`

> **Note**: Sequence counters are tracked independently for each query variant. This means requests to `/items` and `/items?type=a` will advance their own sequences and will appear as separate entries in the `/control/status` output.
