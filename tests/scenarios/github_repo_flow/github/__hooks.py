def handle(ctx):
    if ctx.request["method"] == "POST" and ctx.request["path"] == "/repos":
        body = ctx.request.get("body_json")
        if not body:
            return None

        repo_name = body.get("name")

        # Case for test_hook_handles_post_and_sets_state
        if repo_name == "other":
            ctx.state["last_repo"] = repo_name
            return {
                "status": 200,
                "body": {
                    "id": ctx.uuid4(),
                    "name": repo_name,
                    "created_at": ctx.now(),
                    "note": f"Hook processed this. Last repo: {repo_name}",
                },
            }

        # Case for test_jinja_renders_with_request_context
        if repo_name == "templ":
            return ctx.render_file(
                "POST/repos.001.json.j2",
                extra_context={"repo_name": repo_name}
            )

    # Fall through for all other requests
    return None
