from __future__ import annotations

import json
import os
import re
import time
import uuid
import yaml
from typing import Any, Dict, Optional, Tuple, List

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.routing import APIRouter
from pydantic import BaseModel

from .config import PAYLOADS_ROOT, CONTROL_PORT, service_for_port
from .templates import make_jinja_env

# ---------------- Session & global state ----------------

class SessionState:
    def __init__(self, session_id: str, scenario: str):
        self.session_id = session_id
        self.scenario = scenario
        self.state: Dict[str, Any] = {}               # user state (hooks/templates)
        self.sequences: Dict[str, int] = {}           # base_file -> next index (1-based)

class GlobalState:
    def __init__(self):
        self.current: Optional[SessionState] = None
        self.jinja_env_cache: Dict[str, Any] = {}     # scenario->jinja env cache mtime key

GLOBAL = GlobalState()

# ---------------- Utilities ----------------

def now_iso() -> str:
    import datetime as dt
    # Return in format: 2023-01-01T00:00:00Z (no timezone info in string)
    return dt.datetime.now(dt.UTC).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")

def ensure_scenario_dir(scenario: str) -> str:
    path = os.path.join(PAYLOADS_ROOT, scenario)
    if not os.path.isdir(path):
        raise HTTPException(status_code=404, detail=f"Scenario not found: {scenario}")
    return path

def service_dir(scenario: str, service: str) -> str:
    base = ensure_scenario_dir(scenario)
    sdir = os.path.join(base, service)
    if not os.path.isdir(sdir):
        # Missing service folder is allowed but results in 404 for requests
        return sdir
    return sdir

def http_port_from_request(req: Request) -> int:
    # Prefer ASGI scope server port
    server = req.scope.get("server")
    if server and len(server) == 2 and isinstance(server[1], int):
        return server[1]
    # Fallback: request.url.port or base_url port
    if req.url.port:
        return req.url.port
    # Extract from base_url if present in scope
    base_url = req.scope.get("root_path", "")
    if "27001" in base_url:
        return 27001
    if "27002" in base_url:
        return 27002
    if "27003" in base_url:
        return 27003
    if "27004" in base_url:
        return 27004
    if "27005" in base_url:
        return 27005
    if "27006" in base_url:
        return 27006
    if "27007" in base_url:
        return 27007
    if "27008" in base_url:
        return 27008
    # Last resort
    return CONTROL_PORT

def load_yaml_file(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def body_json_equals(expected: Any, actual: Any) -> bool:
    """Compare expected body JSON with actual body JSON.
    Supports exact match or partial match (expected is subset of actual)."""
    if expected is None:
        return True  # No constraint
    if actual is None:
        return False  # Constraint but no body
    if isinstance(expected, dict) and isinstance(actual, dict):
        # Check that all keys in expected exist in actual with same values
        for k, v in expected.items():
            if k not in actual:
                return False
            if actual[k] != v:
                return False
        return True
    # For non-dict types, do exact match
    return expected == actual

# ---------------- Control API ----------------

class StartBody(BaseModel):
    scenario: str

control_router = APIRouter()

@control_router.post("/control/session/start")
def start_session(body: StartBody):
    scenario = body.scenario.strip()
    ensure_scenario_dir(scenario)
    sid = f"s-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    GLOBAL.current = SessionState(session_id=sid, scenario=scenario)
    return {"session_id": sid, "scenario": scenario}

@control_router.post("/control/session/reset")
def reset_session(body: Optional[StartBody] = None):
    if GLOBAL.current is None:
        raise HTTPException(400, "No active session")
    scenario = GLOBAL.current.scenario
    if body and body.scenario:
        scenario = body.scenario.strip()
        ensure_scenario_dir(scenario)
    sid = f"s-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    GLOBAL.current = SessionState(session_id=sid, scenario=scenario)
    return {"session_id": sid, "scenario": scenario}

@control_router.get("/control/status")
def status():
    if GLOBAL.current is None:
        return {"session_id": None, "scenario": None, "services": {}, "sequences": {}}
    return {
        "session_id": GLOBAL.current.session_id,
        "scenario": GLOBAL.current.scenario,
        "services": { "available": True },
        "sequences": GLOBAL.current.sequences,
    }

@control_router.get("/control/health")
def health():
    return {"status": "healthy"}

# ---------------- Hooks ----------------

class HookContext:
    def __init__(self, request_data: Dict[str, Any], session: SessionState, sroot: str, jinja_env):
        self.request = request_data
        self.state = session.state
        self._sroot = sroot
        self._jinja = jinja_env

    def now(self) -> str:
        return now_iso()

    def uuid4(self) -> str:
        return str(uuid.uuid4())

    def render_file(self, relative_path: str, extra_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return render_payload(self._sroot, relative_path, self._jinja, self.request, self.state, extra_context or {})

def run_hook_if_any(sroot: str, request_data: Dict[str, Any], session: SessionState, jinja_env) -> Optional[Dict[str, Any]]:
    hook_path = os.path.join(sroot, "__hooks.py")
    if not os.path.isfile(hook_path):
        return None

    # Load/reload module per mtime using unique name
    mtime = os.path.getmtime(hook_path)
    mod_name = f"mockhub_hook_{hash((sroot, mtime))}"
    import importlib.util, sys
    if mod_name in sys.modules:
        mod = sys.modules[mod_name]
    else:
        spec = importlib.util.spec_from_file_location(mod_name, hook_path)
        if spec is None or spec.loader is None:
            return None
        mod = importlib.util.module_from_spec(spec)
        sys.modules[mod_name] = mod
        spec.loader.exec_module(mod)

    handle = getattr(mod, "handle", None)
    if not callable(handle):
        return None

    ctx = HookContext(request_data, session, sroot, jinja_env)
    try:
        result = handle(ctx)
        if result is None:
            return None
        if isinstance(result, str):
            # treat as file path
            return render_payload(sroot, result, jinja_env, request_data, session.state, {})
        if isinstance(result, dict):
            # assume ResponseSpec
            return result
        # Unsupported type → ignore
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hook error: {e}")

def run_transform_hook_if_any(sroot: str, request_data: Dict[str, Any], session: SessionState, jinja_env, payload: Dict[str, Any]) -> Dict[str, Any]:
    hook_path = os.path.join(sroot, "__hooks.py")
    if not os.path.isfile(hook_path):
        return payload

    # Load/reload module per mtime using unique name
    mtime = os.path.getmtime(hook_path)
    mod_name = f"mockhub_hook_transform_{hash((sroot, mtime))}"
    import importlib.util, sys
    if mod_name in sys.modules:
        mod = sys.modules[mod_name]
    else:
        spec = importlib.util.spec_from_file_location(mod_name, hook_path)
        if spec is None or spec.loader is None:
            return payload
        mod = importlib.util.module_from_spec(spec)
        sys.modules[mod_name] = mod
        spec.loader.exec_module(mod)

    transform = getattr(mod, "transform", None)
    if not callable(transform):
        return payload

    ctx = HookContext(request_data, session, sroot, jinja_env)
    try:
        # Convert payload to a format that the transform hook can work with
        # If body is bytes and represents JSON, parse it
        transform_payload = payload.copy()
        if isinstance(transform_payload.get("body"), bytes):
            body_bytes = transform_payload["body"]
            if body_bytes:
                # Try to decode as JSON if content-type suggests it
                content_type = transform_payload.get("headers", {}).get("Content-Type", "")
                if "application/json" in content_type:
                    try:
                        transform_payload["body"] = json.loads(body_bytes.decode("utf-8"))
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        pass  # Keep as bytes if can't decode as JSON
        
        result = transform(ctx, transform_payload)
        if result is None:
            return payload
        
        # Convert the result back to the expected payload format
        if isinstance(result, dict):
            # If body is a dict or list, convert it to JSON bytes and set content-type
            if isinstance(result.get("body"), (dict, list)):
                result["body"] = json.dumps(result["body"]).encode("utf-8")
                result["headers"] = {**result.get("headers", {}), "Content-Type": "application/json"}
            # If body is a string, encode it to bytes
            elif isinstance(result.get("body"), str):
                result["body"] = result["body"].encode("utf-8")
            return result
        
        # Unsupported type → ignore
        return payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hook transform error: {e}")

# ---------------- Rules ----------------

def load_rules_if_any(sroot: str) -> List[Dict[str, Any]]:
    path = os.path.join(sroot, "rules.yaml")
    if not os.path.isfile(path):
        return []
    try:
        data = load_yaml_file(path)
        rules = data.get("rules", [])
        return rules if isinstance(rules, list) else []
    except Exception as e:
        raise HTTPException(422, f"Invalid rules.yaml: {e}")

def path_template_match(pattern: str, path: str) -> Optional[Dict[str, str]]:
    # Convert '/repos/{owner}/{repo}/issues' to regex
    esc = re.escape(pattern)
    # Replace escaped '{var}' with '([^/]+)'
    rx = re.sub(r"\\{([a-zA-Z_][a-zA-Z0-9_]*)\\}", r"(?P<\1>[^/]+)", esc)
    rx = "^" + rx + "$"
    m = re.match(rx, path)
    if not m:
        return None
    return m.groupdict()

def query_equals(expected: Any, actual: Dict[str, List[str]]) -> bool:
    # expected str or list; actual dict of key -> list[str]
    if isinstance(expected, list):
        # flatten actual values then compare sets
        flat = actual
        # For comparison we accept order-insensitive equals
        return set(expected) == set(actual.get("", []))  # not used; will handle per key
    return False  # not used at top-level

def dict_query_match(expected: Dict[str, Any], actual: Dict[str, List[str]]) -> bool:
    for k, v in expected.items():
        if isinstance(v, list):
            if set(actual.get(k, [])) != set(v):
                return False
        else:
            vals = actual.get(k, [])
            if len(vals) != 1 or vals[0] != str(v):
                return False
    return True

def apply_rules(rules: List[Dict[str, Any]], req: Dict[str, Any], sroot: str, jinja_env, session: SessionState) -> Optional[Dict[str, Any]]:
    for rule in rules:
        when = rule.get("when", {})
        respond = rule.get("respond", {})
        if not when or not respond:
            continue
        if "method" in when:
            method_ok = False
            m = when["method"]
            if isinstance(m, str):
                method_ok = (req["method"] == m.upper())
            else:
                method_ok = req["method"] in [x.upper() for x in m]
            if not method_ok:
                continue
        if "path" in when:
            params = path_template_match(when["path"], req["path"])
            if params is None:
                continue
            req["path_params"] = params  # expose to templates
        if "query" in when:
            if not dict_query_match(when["query"], req["query"]):
                continue
        if "body" in when:
            b = when["body"]
            if "json" in b:
                if not body_json_equals(b["json"], req["body_json"]):
                    continue
            if "contains" in b:
                raw = req["body_raw"] or b""
                if b["contains"] not in raw.decode("utf-8", errors="ignore"):
                    continue
        # Matched; render
        file_rel = respond.get("file")
        status = int(respond.get("status", 200))
        headers = respond.get("headers", {})
        delay_ms = int(respond.get("delay_ms", 0))
        if file_rel:
            # Replace path template variables with actual values from path_params
            if "path_params" in req and "{" in file_rel:
                for key, value in req.get("path_params", {}).items():
                    file_rel = file_rel.replace(f"{{{key}}}", value)
            spec = render_payload(sroot, file_rel, jinja_env, req, session.state, {})
            # override status/headers/delay if provided inline
            spec["status"] = status
            spec["headers"] = {**spec.get("headers", {}), **headers}
            spec["delay_ms"] = delay_ms if "delay_ms" not in spec else spec["delay_ms"]
            return spec
        else:
            # No file; return an empty response with status
            return {"status": status, "headers": headers, "body": ""}
    return None

# ---------------- File matching & sequences ----------------

from urllib.parse import urlencode, quote_plus, parse_qs

def canonical_query_suffix(query: Dict[str, List[str]]) -> str:
    if not query:
        return ""
    parts: List[Tuple[str, str]] = []
    for k in sorted(query.keys()):
        vals = query[k]
        if not isinstance(vals, list):
            vals = [vals]
        for v in sorted([str(x) for x in vals]):
            parts.append((k, v))
    q = "&".join([f"{quote_plus(k)}={quote_plus(v)}" for k, v in parts])
    return f"__q.{q}" if q else ""

def body_pred_suffix(body_json: Optional[Dict[str, Any]]) -> str:
    # Only support simple top-level key equality with single value in filename
    # This function returns an empty suffix; we will *probe* dynamically for existing files with __b.*
    return ""

def potential_file_candidates(base_path_no_ext: str, has_template: bool, with_query: str, body_pairs: List[Tuple[str, str]], search_dir: str) -> List[str]:
    # Produce likely candidates in order of specificity:
    # 1) base + query + body
    # 2) base + query
    # 3) base + body
    # 4) base
    candidates = []

    def add(ext):
        candidates.append(base_path_no_ext + ext)
        if has_template:
            candidates.append(base_path_no_ext + ext + ".j2")

    # We will probe filesystem for body predicates that match given pairs by constructing suffix
    def build_body_suffix(pairs: List[Tuple[str, str]]) -> str:
        if not pairs:
            return ""
        # Use the first pair only for filename (common/simple case)
        k, v = pairs[0]
        return f"__b.{quote_plus(k)}={quote_plus(v)}"

    q = with_query
    b = build_body_suffix(body_pairs)

    variants = []
    if q and b:
        variants.append(q + b)
    if q:
        variants.append(q)
    if b:
        variants.append(b)
    variants.append("")

    for var in variants:
        if var:
            add(var + ".json")
        else:
            add(".json")

    # Sequences will be handled after picking the base; here we build non-numbered variants.
    # We'll later check for numbered versions of the chosen base.
    return candidates

def match_wildcard_path(request_path_segments: List[str], file_path_segments: List[str]) -> Optional[Dict[str, str]]:
    """Match request path segments against file path segments with wildcard support.
    Returns a dict of wildcard parameter values if match, None otherwise."""
    if len(request_path_segments) != len(file_path_segments):
        return None
    
    params = {}
    for req_seg, file_seg in zip(request_path_segments, file_path_segments):
        if file_seg.startswith("__") and file_seg.endswith("__"):
            # This is a wildcard segment, capture the value
            param_name = file_seg[2:-2]  # Remove __ prefix and suffix
            params[param_name] = req_seg
        elif req_seg != file_seg:
            # Segments don't match and it's not a wildcard
            return None
    
    return params

def find_matching_file_with_wildcards(method_dir: str, request_path: str) -> Optional[Tuple[str, Dict[str, str]]]:
    """Find a file that matches the request path with wildcard support.
    Returns (relative_file_path, path_params) or None if no match."""
    request_segments = [s for s in request_path.split("/") if s != ""]
    
    # Walk through the method directory to find matching files
    for root, dirs, files in os.walk(method_dir):
        for file in files:
            if file.endswith(".json") or file.endswith(".json.j2"):
                file_path = os.path.join(root, file)
                # Get relative path from method_dir
                rel_path = os.path.relpath(file_path, method_dir)
                
                # Properly construct file segments for matching
                # Split the relative path to get directory parts
                dir_part, filename = os.path.split(rel_path)
                dir_segments = [s for s in dir_part.split(os.sep) if s] if dir_part else []
                
                # Remove extension from filename for comparison
                base_name = os.path.splitext(filename)[0]
                if filename.endswith(".json.j2"):
                    base_name = os.path.splitext(base_name)[0]
                
                # Combine directory segments with the base filename
                file_segments = dir_segments + [base_name]
                
                # Try to match the segments
                path_params = match_wildcard_path(request_segments, file_segments)
                if path_params is not None:
                    return rel_path, path_params
    
    return None

def resolve_path_to_file(sroot: str, method: str, path: str, query: Dict[str, List[str]], body_json: Optional[Dict[str, Any]]) -> Tuple[str, str, Optional[Dict[str, str]]]:
    # Return (base_without_index_rel, selected_rel_file_rel_or_single, path_params)
    # Construct base path
    segs = [s for s in path.split("/") if s != ""]
    mdir = os.path.join(sroot, method)
    if not os.path.isdir(mdir):
        raise HTTPException(404, f"Service/method folder not found")
    if len(segs) == 0:
        # root path
        base_no_ext = os.path.join(mdir, "_index")
    else:
        # Trailing slash → directory index
        if path.endswith("/"):
            base_no_ext = os.path.join(mdir, *segs, "_index")
        else:
            last = segs[-1]
            # If the request path explicitly includes an extension (e.g., /data.json or /hello.txt),
            # honor it instead of appending another extension.
            if "." in last:
                base_with_ext = os.path.join(mdir, *segs)
                # Exact file
                if os.path.isfile(base_with_ext):
                    rel = os.path.relpath(base_with_ext, sroot)
                    return os.path.splitext(rel)[0], rel, None
                # Template variant
                if os.path.isfile(base_with_ext + ".j2"):
                    rel = os.path.relpath(base_with_ext + ".j2", sroot)
                    base_rel_no_idx = os.path.splitext(os.path.relpath(base_with_ext, sroot))[0]
                    if base_rel_no_idx.endswith(".json"):
                        base_rel_no_idx = base_rel_no_idx[:-5]
                    return base_rel_no_idx, rel, None
                # Fall back to sequence probing using the non-templated path
                rel = os.path.relpath(base_with_ext, sroot)
                base_rel_no_idx = os.path.splitext(rel)[0]
                if base_rel_no_idx.endswith(".json"):
                    base_rel_no_idx = base_rel_no_idx[:-5]
                return base_rel_no_idx, rel, None
            # No explicit extension → logical base (e.g., /template)
            base_no_ext = os.path.join(mdir, *segs)

    # Build candidates and probe for existence
    q_suffix = canonical_query_suffix(query)
    body_pairs: List[Tuple[str, str]] = []
    if isinstance(body_json, dict):
        # Produce pairs from body for simple filename predicate test
        for k, v in body_json.items():
            if isinstance(v, (str, int, float, bool)):
                body_pairs.append((str(k), str(v)))
    candidates = potential_file_candidates(
        base_path_no_ext=base_no_ext,
        has_template=True,
        with_query=q_suffix,
        body_pairs=body_pairs,
        search_dir=sroot,
    )
    for cand in candidates:
        if os.path.isfile(cand):
            # Found an exact, single (non-sequenced) file
            rel = os.path.relpath(cand, sroot)
            base_rel_no_idx = os.path.splitext(rel)[0]  # remove .json or .json.j2
            if base_rel_no_idx.endswith(".json"):
                base_rel_no_idx = base_rel_no_idx[:-5]
            return base_rel_no_idx, rel, None

        # If not single file, check if sequenced files exist (001.json / 001.json.j2)
        base, ext = os.path.splitext(cand)
        for i in range(1, 1000):
            num = f".{i:03d}"
            for actual in (base + num + ext, base + num + ext + ".j2"):
                if os.path.isfile(actual):
                    # Found a sequence base
                    rel = os.path.relpath(cand, sroot)  # we return *non-numbered* candidate
                    base_rel_no_idx = os.path.splitext(os.path.relpath(base + ext, sroot))[0]
                    if base_rel_no_idx.endswith(".json"):
                        base_rel_no_idx = base_rel_no_idx[:-5]
                    # 'rel' is non-numbered file (may not exist), but sequence base is base + ext
                    return base_rel_no_idx, os.path.relpath(base + ext, sroot), None  # non-numbered representative

    # Try wildcard matching if no exact match found
    wildcard_match = find_matching_file_with_wildcards(mdir, path)
    if wildcard_match:
        rel_path, path_params = wildcard_match
        rel_path = os.path.join(method, rel_path)
        # For wildcard matches, we return the relative path and set path_params
        base_rel_no_idx = os.path.splitext(rel_path)[0]
        if base_rel_no_idx.endswith(".json"):
            base_rel_no_idx = base_rel_no_idx[:-5]
        elif base_rel_no_idx.endswith(".json.j2"):
            base_rel_no_idx = base_rel_no_idx[:-8]
        return base_rel_no_idx, rel_path, path_params

    raise HTTPException(404, "no mock for request")

def next_sequence_file(session: SessionState, sroot: str, base_rel_with_ext: str) -> str:
    # base_rel_with_ext is something like 'GET/user/repos.json' (without .NNN)
    base_no_ext, ext = os.path.splitext(base_rel_with_ext)
    key = base_no_ext  # include method/path and optional q/b suffix
    idx = session.sequences.get(key, 1)
    # Find the file with this idx
    for cand in (base_no_ext + f".{idx:03d}" + ext, base_no_ext + f".{idx:03d}" + ext + ".j2"):
        if os.path.isfile(os.path.join(sroot, cand)):
            # Increment for next time
            session.sequences[key] = idx + 1
            return cand
    # If no numbered file for current idx and a non-numbered file exists, serve non-numbered
    if os.path.isfile(os.path.join(sroot, base_rel_with_ext)):
        # 'single' file — not a sequence; do not increment further
        return base_rel_with_ext
    # Check if any numbered files exist to know if it's a sequence exhaustion
    # If at least one exists but not the requested idx, it means exhausted
    any_seq = False
    for i in range(1, 1000):
        probe = os.path.join(sroot, base_no_ext + f".{i:03d}" + ext)
        probe2 = probe + ".j2"
        if os.path.isfile(probe) or os.path.isfile(probe2):
            any_seq = True
            break
    if any_seq:
        raise HTTPException(410, f"sequence exhausted for {base_rel_with_ext} at index {idx:03d}")
    raise HTTPException(404, "no mock for request")

def render_payload(sroot: str, rel_path: str, jinja_env, req: Dict[str, Any], state: Dict[str, Any], extra: Dict[str, Any]) -> Dict[str, Any]:
    # Look for sidecar meta
    full = os.path.join(sroot, rel_path)
    meta = {}
    meta_path = full + ".meta.yaml"
    if os.path.isfile(meta_path):
        try:
            meta = load_yaml_file(meta_path) or {}
        except Exception as e:
            raise HTTPException(422, f"Invalid meta for {rel_path}: {e}")

    status = int(meta.get("status", 200))
    headers = meta.get("headers", {})
    delay_ms = int(meta.get("delay_ms", 0))

    body_bytes: bytes
    if rel_path.endswith(".j2"):
        try:
            # Read the template file directly instead of using jinja_env.get_template
            with open(full, "r", encoding="utf-8") as f:
                template_content = f.read()
            
            # Create a template from the string
            template = jinja_env.from_string(template_content)
            
            context = {
                "req": {
                    "method": req["method"],
                    "path": req["path"],
                    "path_segments": [s for s in req["path"].split("/") if s],
                    "path_params": req.get("path_params", {}),
                    "query": req["query"],
                    "headers": req["headers"],
                    "body": req["body_json"],
                    "body_raw": req["body_raw"],
                },
                "state": state,
                "now": now_iso,
                "uuid4": uuid.uuid4,
            }
            context.update(extra)
            rendered = template.render(**context)
            body_bytes = rendered.encode("utf-8")
        except Exception as e:
            if "undefined" in str(e).lower():
                # Handle undefined variable errors specifically
                raise HTTPException(500, f"Template error: {e}")
            raise  # Re-raise other exceptions
    else:
        with open(full, "rb") as f:
            body_bytes = f.read()

    # Infer content-type
    ct = "application/octet-stream"
    if rel_path.endswith(".json") or rel_path.endswith(".json.j2"):
        ct = "application/json"
    elif rel_path.endswith(".txt") or rel_path.endswith(".txt.j2"):
        ct = "text/plain"
    headers = {"Content-Type": ct, **headers}

    return {"status": status, "headers": headers, "delay_ms": delay_ms, "body": body_bytes}

# ---------------- Service handler ----------------

service_router = APIRouter()

@service_router.api_route("/{path:path}", methods=["GET","POST","PUT","PATCH","DELETE","HEAD","OPTIONS"])
async def handle_any(path: str, request: Request):
    port = http_port_from_request(request)
    if port == CONTROL_PORT:
        # Let control routes handle; unreached if routing matched here
        raise HTTPException(404, "control port")
    service = service_for_port(port)
    if service is None:
        raise HTTPException(404, f"Unknown service port {port}")
    
    # Check for active session FIRST - this should happen before any scenario operations
    if GLOBAL.current is None:
        raise HTTPException(400, "No active session. Call /control/session/start first.")

    scenario = GLOBAL.current.scenario
    sdir = service_dir(scenario, service)
    # Don't check if directory exists until after session check

    # Build request info
    method = request.method.upper()
    # Query dict[str, List[str]]
    from urllib.parse import parse_qs
    query = parse_qs(request.url.query, keep_blank_values=True)
    # Headers
    headers = {k.decode().lower(): v.decode() for k, v in request.scope.get("headers", [])}
    # Body
    body_raw = await request.body()
    body_json = None
    if body_raw:
        ctype = headers.get("content-type","")
        if "application/json" in ctype:
            try:
                body_json = json.loads(body_raw.decode("utf-8"))
            except Exception:
                body_json = None

    req_data = {
        "method": method,
        "path": "/" + path,
        "query": query,
        "headers": headers,
        "body_json": body_json,
        "body_raw": body_raw,
    }

    # Make jinja env (per scenario cache)
    jkey = scenario
    jenv = getattr(GLOBAL, "_jinja_cache", None)
    if not hasattr(GLOBAL, "_jinja_map"):
        GLOBAL._jinja_map = {}
    jinja_env = GLOBAL._jinja_map.get(jkey)
    if jinja_env is None:
        jinja_env = make_jinja_env(searchpath=os.path.join(PAYLOADS_ROOT, scenario))
        GLOBAL._jinja_map[jkey] = jinja_env

    # 1) Hook
    hook_resp = run_hook_if_any(sdir, req_data, GLOBAL.current, jinja_env)
    if hook_resp is not None:
        # Apply transform hook if exists
        hook_resp = run_transform_hook_if_any(sdir, req_data, GLOBAL.current, jinja_env, hook_resp)
        return build_response(hook_resp)

    # 2) Rules
    rules = load_rules_if_any(sdir)
    if rules:
        rule_resp = apply_rules(rules, req_data, sdir, jinja_env, GLOBAL.current)
        if rule_resp is not None:
            # Apply transform hook if exists
            rule_resp = run_transform_hook_if_any(sdir, req_data, GLOBAL.current, jinja_env, rule_resp)
            return build_response(rule_resp)

    # 3) Files (with sequences)
    base_rel_no_idx, chosen_rel, path_params = resolve_path_to_file(sdir, method, "/" + path, query, body_json)
    if path_params:
        req_data["path_params"] = path_params
    final_rel = next_sequence_file(GLOBAL.current, sdir, chosen_rel)
    spec = render_payload(sdir, final_rel, jinja_env, req_data, GLOBAL.current.state, {})
    
    # Apply transform hook if exists
    spec = run_transform_hook_if_any(sdir, req_data, GLOBAL.current, jinja_env, spec)
    return build_response(spec)

def build_response(spec: Dict[str, Any]) -> Response:
    delay_ms = int(spec.get("delay_ms", 0) or 0)
    if delay_ms > 0:
        import time
        time.sleep(delay_ms / 1000.0)
    status = int(spec.get("status", 200))
    headers = spec.get("headers", {})
    body = spec.get("body", b"")
    if isinstance(body, (dict, list)):
        body = json.dumps(body).encode("utf-8")
        headers = {"Content-Type": "application/json", **headers}
    elif isinstance(body, str):
        body = body.encode("utf-8")
    return Response(content=body, status_code=status, headers=headers)

# ---------------- App factory ----------------

def create_app() -> FastAPI:
    # Fresh app → reset global state so tests don't leak between clients
    GLOBAL.current = None
    if not hasattr(GLOBAL, "_jinja_map"):
        GLOBAL._jinja_map = {}
    else:
        GLOBAL._jinja_map.clear()
    app = FastAPI(title="MockHub", version="0.1.0")
    app.include_router(control_router)
    app.include_router(service_router)
    return app
