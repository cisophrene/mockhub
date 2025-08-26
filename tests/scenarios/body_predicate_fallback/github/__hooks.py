def handle(ctx):
    if ctx.request["method"] == "POST" and ctx.request["path"] == "/repos":
        if ctx.request["body_json"] and ctx.request["body_json"].get("name") != "my-repo":
            return {
                "status": 422,
                "headers": {"X-MockHub": "fallback"},
                "body": {"message": "Invalid repository name"}
            }
    return None
