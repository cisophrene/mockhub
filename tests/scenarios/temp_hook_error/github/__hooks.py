
def handle(ctx):
    if ctx.request["path"] == "/error":
        raise ValueError("Intentional error for testing")
    return None
