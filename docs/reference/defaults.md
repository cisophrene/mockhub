# Defaults & Conventions

This page outlines MockHub's default behaviors and conventions.

---

* **Status Code**: `200 OK` is the default for all HTTP verbs unless overridden by [sidecar metadata](../features/metadata.md) or a [rule](../matching/rules.md).

* **Content-Type**: Inferred from the payload filename's extension. See the [Content Types](content-types.md) page for details.

* **Latency**: No artificial delay by default. Set `delay_ms` in metadata or a rule to simulate latency.

* **Sequence Numbering**: Use three digits (`.001`, `.002`, ...). When a sequence is exhausted, MockHub returns `410 Gone`.

* **Matching Order**: The resolution order is always **Hook → Rules → Files**. Within the filesystem, MockHub looks for the most specific match first (i.e., files with query/body predicates are checked before base files).
