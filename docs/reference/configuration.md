# Configuration & CLI

MockHub can be configured via environment variables and controlled with a simple CLI.

---

## Environment Variables

* `MOCKHUB_CONTROL_PORT`: The port for the Control API. (Default: `27000`)
* `MOCKHUB_PAYLOADS_ROOT`: The root directory for scenario payloads. (Default: `./payloads`)
* `MOCKHUB_LOG_LEVEL`: The logging level. (Default: `info`)

---

## Command-Line Interface (CLI)

After installing with `pip`, you can use the `mockhub` command.

* **Start all services**:
    ```bash
    mockhub run
    ```
* **Start only a subset of services**:
    ```bash
    # Run the control server and the first service port
    mockhub run --ports 27000 27001
    ```

---

## Default Service Ports

* `27001`: github
* `27002`: shortcut
* `27003`: zoho
* `27004`: google
