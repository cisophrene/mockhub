from __future__ import annotations
import asyncio
import logging
import os
from typing import Dict, List

import uvicorn

from .config import CONTROL_PORT, DEFAULT_SERVICE_PORTS, LOG_LEVEL
from .app import create_app

# We run *multiple* uvicorn servers in the same process, one per port.
# All serve the same FastAPI app, which inspects local port to decide behavior.

logger = logging.getLogger(__name__)

def _make_server(port: int) -> uvicorn.Server:
    config = uvicorn.Config(
        app=create_app(),
        host="0.0.0.0",
        port=port,
        log_level=LOG_LEVEL,
        loop="asyncio",
        use_colors=True,
        proxy_headers=False,
        forwarded_allow_ips="*",
        reload=False,  # file changes are picked up on-demand by MockHub
    )
    return uvicorn.Server(config)

async def _run_all(ports: List[int]):
    servers = [_make_server(p) for p in ports]
    await asyncio.gather(*[srv.serve() for srv in servers])

def app():
    import argparse

    parser = argparse.ArgumentParser(prog="mockhub", description="MockHub CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    run_p = sub.add_parser("run", help="Run all servers (control + services).")
    run_p.add_argument("--ports", nargs="*", type=int, default=[CONTROL_PORT] + list(DEFAULT_SERVICE_PORTS.keys()),
                       help="Ports to bind (default: control + default service ports)")

    args = parser.parse_args()

    if args.cmd == "run":
        ports = args.ports
        print(f"MockHub starting on ports: {ports}")
        try:
            asyncio.run(_run_all(ports))
        except KeyboardInterrupt:
            print("MockHub stopped.")
