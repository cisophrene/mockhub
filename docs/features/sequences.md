# Sequences (Stateful Flows)

Sequences allow you to serve a different response for each subsequent call to the same endpoint, which is perfect for modeling stateful flows.

---

## How It Works

To create a sequence, add a numeric suffix (e.g., `.001`, `.002`) to your payload files.

**Example:**
* `GET/user/repos.001.json`
* `GET/user/repos.002.json`
* `GET/user/repos.003.json`

1.  The **first** request to `GET /user/repos` will receive the contents of `.001.json`.
2.  The **second** request will receive `.002.json`.
3.  The **third** request will receive `.003.json`.

### Sequence Exhaustion

After the last numbered file in a sequence has been served, any further requests to that endpoint will receive an `HTTP 410 Gone` response.

### Inspecting and Resetting

You can monitor the current counter for any sequence by calling `GET /control/status` on the [Control API](../control-api.md).

To reset all sequence counters back to `1`, use the `POST /control/session/reset` endpoint.

> Sequences work with any file-based matching, including those with [query string](../matching/query-strings.md) variants, [body predicates](../matching/body-predicates.md), and [Jinja2 templates](templating.md). Each variant maintains its own independent sequence counter.
