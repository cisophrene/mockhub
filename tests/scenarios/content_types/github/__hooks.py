def handle(ctx):
    if ctx.request["method"] == "POST" and ctx.request["path"] == "/echo-plain":
        # Echo back the request details for plain text
        return {
            "status": 200,
            "headers": {"Content-Type": "application/json"},
            "body": {
                "echo": True,
                "content_type": ctx.request["headers"].get("content-type", ""),
                "body_json": ctx.request["body_json"],
                "body_raw": ctx.request["body_raw"].decode("utf-8", errors="ignore") if ctx.request["body_raw"] else None
            }
        }
    return None
