"""Web server for health checks."""

import os
from aiohttp import web


async def home(request):
    """Home endpoint."""
    return web.Response(text="Hello From Perna Mix Bot 👮‍♂️")


async def healthcheck(request):
    """Health check endpoint."""
    return web.Response(text="Working")


def create_app():
    """Create and configure the web application."""
    app = web.Application()
    app.router.add_get("/", home)
    app.router.add_get("/healthcheck", healthcheck)
    return app


async def run_server():
    """Run the web server."""
    port = int(os.getenv("PORT", "10000"))
    app = create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"Web server listening on 0.0.0.0:{port}")
    return runner
