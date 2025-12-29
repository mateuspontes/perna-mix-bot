"""Main entry point for Perna Mix Bot."""

import asyncio
import os
import signal
import sys
import discord

from bot.client import PernaBot
from bot.web_server import run_server


async def start_bot_with_retry(token: str, max_retries: int = 5):
    """Start bot with exponential backoff retry logic.

    Args:
        token: Discord bot token
        max_retries: Maximum number of retry attempts
    """
    bot = PernaBot()
    retry_delay = 5  # Initial delay in seconds

    for attempt in range(max_retries):
        try:
            print(f"Attempting to connect to Discord (attempt {attempt + 1}/{max_retries})...")
            await bot.start(token)
            break  # Successfully started
        except discord.HTTPException as e:
            if e.status == 429 or "rate limit" in str(e).lower():
                if attempt < max_retries - 1:
                    print(f"Rate limited by Discord. Waiting {retry_delay} seconds before retry...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    print("Max retries reached. Could not connect to Discord.")
                    raise
            else:
                raise
        except Exception as e:
            print(f"Error starting bot: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2
            else:
                raise

    return bot


async def main():
    """Main application entry point."""
    # Get Discord token from environment
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("Error: DISCORD_TOKEN environment variable not set")
        sys.exit(1)

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

    # Start bot with retry logic
    bot_task = asyncio.create_task(start_bot_with_retry(token))

    # Wait for shutdown signal or bot to stop
    bot = None
    try:
        done, pending = await asyncio.wait(
            [bot_task, asyncio.create_task(shutdown_event.wait())],
            return_when=asyncio.FIRST_COMPLETED
        )

        if shutdown_event.is_set():
            # Get bot instance from completed task
            if bot_task.done() and not bot_task.exception():
                bot = bot_task.result()
                # Send shutdown message
                await bot.send_shutdown_message()
                await asyncio.sleep(2)  # Give time for message to be sent

                # Close bot
                await bot.close()

        # Cancel any pending tasks
        for task in pending:
            task.cancel()

    except Exception as e:
        print(f"Error in main loop: {e}")
    finally:
        # Cleanup web server
        await web_runner.cleanup()
        print("Shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
