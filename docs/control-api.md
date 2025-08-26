# Control API

The Control API is a simple HTTP interface, running on port `27000` by default, that allows you to manage MockHub's state without restarting the server.

---

## Endpoints

### `GET /control/health`

Checks if the MockHub server is running.

* **Success Response** (`200 OK`):
    ```json
    { "status": "healthy" }
    ```

### `POST /control/session/start`

Starts a new session and loads the specified scenario. All subsequent requests to service ports will be handled by this scenario.

* **Request Body**:
    ```json
    { "scenario": "name_of_scenario" }
    ```

### `POST /control/session/reset`

Resets all [sequence counters](features/sequences.md) and other state for the current session. You can optionally provide a new scenario name to switch to it atomically.

* **Request Body** (optional):
    ```json
    { "scenario": "another_scenario" }
    ```

### `GET /control/status`

Retrieves the current state of the active session, including its unique ID, the active scenario, and the current value of all sequence counters. This is incredibly useful for debugging stateful flows.

* **Example Response**:
    ```json
    {
      "session_id": "a1b2c3d4-e5f6-a7b8-c9d0-e1f2a3b4c5d6",
      "scenario": "github_repo_flow",
      "sequences": {
        "GET/user/repos": 3,
        "GET/items__q.type=a": 3
      }
    }
    ```
    In this example, the next request to `GET /user/repos` would look for a file ending in `.003.json`.

---

## Common Errors

* `404 Scenario not found`: The scenario name provided in `POST /control/session/start` does not correspond to a folder under the `payloads/` directory.
* `400 No active session`: You made a request to a service port before starting a session with `/control/session/start`.
