# Example Scenario: `github_repo_flow`

The `github_repo_flow` scenario is a practical example that demonstrates many of MockHub's core features working together.

---

## Key Files and Features

Here are some of the interesting files in this scenario and what they showcase:

* **`GET/user/repos.001.json`**, **`.002.json`**, **`.003.json`**
    * Demonstrates a basic [sequence](features/sequences.md) for a `GET` request. Each call to `/user/repos` returns the next file in the series.

* **`GET/search__q.labels=bug&state=open.json`**
    * Shows how to handle a specific [query string variant](matching/query-strings.md).

* **`POST/repos__b.name=my-repo.json`** and **`.meta.yaml`**
    * A simple [body predicate](matching/body-predicates.md) for a `POST` request.
    * The associated `meta.yaml` file overrides the default response to be `201 Created`, adds a custom header (`X-MockHub: created`), and simulates a 10ms delay.

* **`POST/repos.001.json.j2`**
    * A dynamic response using [Jinja2 templating](features/templating.md). It likely uses `{{ req.body.name }}` to reflect the requested repository name and `{{ state.last_repo }}` to show statefulness.

* **`__hooks.py`**
    * A [Python hook](features/hooks.md) that programmatically handles certain `POST /repos` requests, perhaps for a specific repository name, while allowing other requests to fall through to the file-based responses.

This scenario provides a great starting point. Feel free to duplicate it, tweak the files and logic, and switch to it via `/control/session/start` to build out your own test flows. Happy mocking!
