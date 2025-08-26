from __future__ import annotations
from jinja2 import Environment, FileSystemLoader, StrictUndefined

def make_jinja_env(searchpath: str):
    # StrictUndefined so missing keys fail loudly during tests
    return Environment(
        loader=FileSystemLoader(searchpath),
        autoescape=False,
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
