def handle(ctx):
    # Always return None to fall through to file-based handling
    return None

def transform(ctx, payload):
    # Transform the payload by adding new fields
    if ctx.request["path"] == "/test":
        if isinstance(payload.get("body"), dict):
            payload["body"]["transformed"] = True
            payload["body"]["added_by_hook"] = "hook_value"
    return payload
