from __future__ import annotations
import os
from typing import Dict

CONTROL_PORT = int(os.getenv("MOCKHUB_CONTROL_PORT", "27000"))
PAYLOADS_ROOT = os.getenv("MOCKHUB_PAYLOADS_ROOT", os.path.abspath("./payloads"))
LOG_LEVEL = os.getenv("MOCKHUB_LOG_LEVEL", "info").lower()

# Default service ports
DEFAULT_SERVICE_PORTS: Dict[int, str] = {
    27001: "github",
    27002: "shortcut",
    27003: "zoho",
    27004: "google",

}

def service_for_port(port: int) -> str | None:
    return DEFAULT_SERVICE_PORTS.get(port)
