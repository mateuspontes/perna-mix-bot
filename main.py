"""Main entry point for Perna Mix Bot."""

import asyncio
import os
import signal
import sys

from bot.client import PernaBot
from bot.web_server import run_server


async def main():
    """Main application entry point."""
    # Get Discord token from environment
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("Error: DISCORD_TOKEN environment variable not set")
        sys.exit(1)

    # Create bot client
    bot = PernaBot()

    # Start web server
    web_runner = await run_server()

    # Setup shutdown handler
    shutdown_event = asyncio.Event()

    def signal_handler(sig, frame):
        """Handle shutdown signals."""
        print("\nReceived shutdown signal, sending goodbye message...")
        shutdown_event.set()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start bot
    bot_task = asyncio.create_task(bot.start(token))

    # Wait for shutdown signal or bot to stop
    try:
        done, pending = await asyncio.wait(
            [bot_task, asyncio.create_task(shutdown_event.wait())],
            return_when=asyncio.FIRST_COMPLETED
        )

        if shutdown_event.is_set():
            # Send shutdown message
            await bot.send_shutdown_message()
            await asyncio.sleep(2)  # Give time for message to be sent

            # Close bot
            await bot.close()

        # Cancel any pending tasks
        for task in pending:
            task.cancel()

    finally:
        # Cleanup web server
        await web_runner.cleanup()
        print("Shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
