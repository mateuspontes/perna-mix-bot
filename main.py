"""Main entry point for Perna Mix Bot."""

import asyncio
import logging
import os
import signal
import sys
import warnings
import discord

from bot.client import PernaBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set discord.py logging to INFO to see connection issues
logging.getLogger('discord').setLevel(logging.INFO)
logging.getLogger('discord.gateway').setLevel(logging.INFO)
logging.getLogger('discord.client').setLevel(logging.INFO)

# Filter out ResourceWarning about unclosed sockets (these are managed by discord.py)
warnings.filterwarnings('ignore', category=ResourceWarning, message='unclosed.*')


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
            logger.info(f"[DISCORD] Attempting to connect (attempt {attempt + 1}/{max_retries})...")
            await bot.start(token)
            break  # Successfully started
        except discord.HTTPException as e:
            if e.status == 429 or "rate limit" in str(e).lower():
                if attempt < max_retries - 1:
                    logger.warning(f"[DISCORD] Rate limited. Waiting {retry_delay}s before retry...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error("[DISCORD] Max retries reached. Could not connect.")
                    raise
            else:
                logger.error(f"[DISCORD] HTTP Exception: {e}", exc_info=True)
                raise
        except discord.LoginFailure as e:
            logger.error(f"[DISCORD] Login failed - invalid token: {e}", exc_info=True)
            raise
        except discord.ConnectionClosed as e:
            logger.error(f"[DISCORD] Connection closed unexpectedly: {e}", exc_info=True)
            if attempt < max_retries - 1:
                logger.info(f"[DISCORD] Retrying in {retry_delay}s...")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2
            else:
                raise
        except Exception as e:
            logger.error(f"[DISCORD] Unexpected error: {type(e).__name__}: {e}", exc_info=True)
            if attempt < max_retries - 1:
                logger.info(f"[DISCORD] Retrying in {retry_delay}s...")
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
        logger.error("[STARTUP] DISCORD_TOKEN environment variable not set")
        sys.exit(1)

    logger.info("[STARTUP] Starting Perna Mix Bot...")

    # Setup shutdown handler
    shutdown_event = asyncio.Event()

    def signal_handler(sig, frame):
        """Handle shutdown signals."""
        logger.info(f"[SHUTDOWN] Received signal {sig}, initiating shutdown...")
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
            logger.info("[SHUTDOWN] Processing shutdown...")
            # Get bot instance from completed task
            if bot_task.done() and not bot_task.exception():
                bot = bot_task.result()
                # Send shutdown message
                logger.info("[DISCORD] Sending shutdown message...")
                await bot.send_shutdown_message()
                await asyncio.sleep(2)  # Give time for message to be sent

                # Close bot
                logger.info("[DISCORD] Closing bot connection...")
                await bot.close()

        # Cancel any pending tasks
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    except Exception as e:
        logger.error(f"[ERROR] Main loop error: {type(e).__name__}: {e}", exc_info=True)
    finally:
        # Ensure bot is closed
        if bot and not bot.is_closed():
            logger.info("[DISCORD] Ensuring bot connection is closed...")
            await bot.close()

        logger.info("[SHUTDOWN] Shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
