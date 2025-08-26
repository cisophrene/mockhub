# MockHub – User’s Manual

A pleasant, precise guide to mocking third‑party APIs for integration tests.

## When to use MockHub?

Use MockHub at the **integration testing stage** to simulate real HTTP APIs end‑to‑end. For unit tests, you should prefer your programming language’s in‑process stubs or spies, as they are faster and more tightly coupled to the code under test.

---

## Overview

MockHub is a local HTTP mock server that serves pre‑made or dynamic responses for common third‑party APIs (e.g., GitHub, Shortcut, Zoho, etc.). You select a scenario via a [Control API](control-api.md), and then point your system‑under‑test (SUT) to the relevant service ports (one port per mocked service).

Matching is driven by a powerful and layered system: it starts with simple **filenames**, can be augmented with optional **YAML rules**, and fully customized with **Python hooks**. For dynamic payloads, it integrates **Jinja2 templates**. MockHub also supports **sequences** to model multi‑step flows and can simulate custom latency, headers, and status codes.

### Key Properties

* **Multiple services** on different ports (GitHub, Shortcut, Zoho, Google, Passbolt, Equinix, Discourse, GLPI)
* 📂 **File‑first design** with optional [rules](matching/rules.md) and [hooks](features/hooks.md) for overrides.
* 🔢 **Sequences** for evolving responses (e.g., `file.001.json`, `file.002.json`).
* 🧩 **Jinja2 templating** with strict undefined variable handling to help you fail fast.
* ♻️ **Hot‑reload**: edits to payload files are picked up on the next request without a server restart.
* 📜 **Control API** to switch or reset scenarios without changing your SUT's code.
