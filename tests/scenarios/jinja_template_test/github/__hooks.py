def handle(ctx):
    if ctx.request["method"] == "POST" and ctx.request["path"] == "/repos":
        if ctx.request["body_json"] and ctx.request["body_json"].get("name") == "templ":
            # Set state for template to use
            ctx.state["last_repo"] = "previous-repo"
            return ctx.render_file(
                "POST/repos.001.json.j2",
                extra_context={"repo_name": ctx.request["body_json"].get("name")}
            )
    return None
