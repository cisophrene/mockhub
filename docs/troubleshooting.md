# Troubleshooting

Common issues and how to resolve them.

---

* **`400 No active session`**
    * **Cause**: A request was made to a service port before a scenario was started.
    * **Fix**: Call `POST /control/session/start` first.

* **`404 Scenario not found`** (from Control API)
    * **Cause**: The scenario name in the start request doesn't match a folder under `payloads/`.
    * **Fix**: Check for typos in the scenario name.

* **`404 no mock for request`** (from Service Port)
    * **Cause**: No matching hook, rule, or file was found for the request.
    * **Fix**: Check the method, path, and any [query](matching/query-strings.md) or [body](matching/body-predicates.md) variants. Ensure the corresponding directories and files exist.

* **`410 sequence exhausted … at index 00X`**
    * **Cause**: All numbered files in a [sequence](features/sequences.md) have been served.
    * **Fix**: Add more numbered files to the sequence or call `POST /control/session/reset`.

* **`422 Invalid meta …`**
    * **Cause**: A `*.meta.yaml` file has invalid YAML syntax.
    * **Fix**: Check the file for formatting errors.

* **`500 Template error: … undefined …`**
    * **Cause**: A Jinja2 template is referencing a variable that does not exist.
    * **Fix**: Correct the variable name in the template or ensure it's provided via a hook or the request context.

* **`500 Hook error: …`**
    * **Cause**: An unhandled exception occurred in a `__hooks.py` file.
    * **Fix**: Check the hook's code and the server logs for the full traceback.

### Debugging Tips

1.  **Check Status**: Hit `GET /control/status` to inspect the active scenario and current sequence counters.
2.  **Verify Filenames**: Ensure query string `__q.` suffixes have sorted keys and values.
3.  **File Extensions**: Remember that a request to `/hello` looks for `hello.json` by default, while a request to `/hello.txt` looks for `hello.txt`.
