"""Command handlers for the bot."""

import random
import discord
from typing import List

from .constants import HELP_MESSAGE, REPORT_MESSAGE, MIX_COMMAND, HELP_COMMAND, REPORT_COMMAND
from .utils import create_team_message


async def handle_help_command(message: discord.Message):
    """Handle !help command.

    Args:
        message: Discord message that triggered the command
    """
    await message.channel.send(HELP_MESSAGE)


async def handle_report_command(message: discord.Message):
    """Handle !report command.

    Args:
        message: Discord message that triggered the command
    """
    cleaned_input = message.content.removeprefix(REPORT_COMMAND).strip()

    if not cleaned_input:
        await message.channel.send(
            "🚨 Você precisa informar o nome dos jogadores, separados por vírgula! Não é tão difícil, basta ler."
        )
        return

    await message.channel.send(REPORT_MESSAGE)


async def handle_mix_command(message: discord.Message):
    """Handle !mix command to create random teams.

    Args:
        message: Discord message that triggered the command
    """
    cleaned_input = message.content.removeprefix(MIX_COMMAND).strip()

    if not cleaned_input:
        await message.channel.send(
            "🚨 Você precisa informar o nome dos jogadores, separados por vírgula! Não é tão difícil, basta ler."
        )
        return

    users = [user.strip() for user in cleaned_input.split(",")]
    shuffled_users = users.copy()
    random.shuffle(shuffled_users)

    # Create buttons
    view = MixView(users)

    # Send message with teams and buttons
    await message.reply(
        content=create_team_message(shuffled_users),
        view=view,
        mention_author=False
    )


class MixView(discord.ui.View):
    """View with buttons for team reshuffling."""

    def __init__(self, users: List[str]):
        super().__init__(timeout=None)
        self.users = users

    @discord.ui.button(label="🔮 Não tá balanceado", style=discord.ButtonStyle.primary, custom_id="reshuffle")
    async def reshuffle_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Reshuffle teams when button is clicked."""
        shuffled = self.users.copy()
        random.shuffle(shuffled)
        await interaction.response.edit_message(content=create_team_message(shuffled), view=self)

    @discord.ui.button(label="✅ Aceito", style=discord.ButtonStyle.success, custom_id="accept")
    async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Accept teams and remove buttons."""
        await interaction.response.edit_message(view=None)
