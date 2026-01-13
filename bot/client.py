"""Discord client and event handlers."""

import logging
import discord
from discord.ext import commands

from .constants import HELP_COMMAND, MIX_COMMAND, REPORT_COMMAND, NOTIFICATION_CHANNEL_ID
from .commands import handle_help_command, handle_mix_command, handle_report_command

logger = logging.getLogger(__name__)


class PernaBot(discord.Client):
    """Perna Mix Bot Discord client."""

    def __init__(self, *args, **kwargs):
        intents = discord.Intents.all()
        super().__init__(intents=intents, *args, **kwargs)

    async def on_ready(self):
        """Called when the bot is ready."""
        logger.info(f"[DISCORD] Bot connected as {self.user.name} (ID: {self.user.id})")

        # Send startup message to notification channel
        try:
            channel = await self.fetch_channel(NOTIFICATION_CHANNEL_ID)
            logger.info(f"[DISCORD] Sending startup message to channel {NOTIFICATION_CHANNEL_ID}")
            await channel.send("🤖 **Perna Bot está ONLINE!** 🎯")
        except discord.errors.NotFound:
            logger.warning(f"[DISCORD] Notification channel {NOTIFICATION_CHANNEL_ID} not found")
        except discord.errors.Forbidden:
            logger.warning(f"[DISCORD] No permission to access notification channel {NOTIFICATION_CHANNEL_ID}")
        except Exception as e:
            logger.warning(f"[DISCORD] Error accessing notification channel {NOTIFICATION_CHANNEL_ID}: {e}")

    async def on_message(self, message: discord.Message):
        """Handle incoming messages."""
        # Ignore messages from the bot itself
        if message.author == self.user:
            return

        # Handle commands
        if message.content == HELP_COMMAND:
            await handle_help_command(message)

        elif message.content.startswith(REPORT_COMMAND):
            await handle_report_command(message)

        elif message.content.startswith(MIX_COMMAND):
            await handle_mix_command(message)

    async def send_shutdown_message(self):
        """Send shutdown notification message."""
        try:
            channel = await self.fetch_channel(NOTIFICATION_CHANNEL_ID)
            logger.info(f"[DISCORD] Sending shutdown message to channel {NOTIFICATION_CHANNEL_ID}")
            await channel.send("🔴 **Perna Bot está OFFLINE!** \nVolto em breve para sortear Mix! 👋")
        except discord.errors.NotFound:
            logger.warning(f"[DISCORD] Notification channel {NOTIFICATION_CHANNEL_ID} not found")
        except discord.errors.Forbidden:
            logger.warning(f"[DISCORD] No permission to access notification channel {NOTIFICATION_CHANNEL_ID}")
        except Exception as e:
            logger.warning(f"[DISCORD] Error accessing notification channel {NOTIFICATION_CHANNEL_ID}: {e}")
