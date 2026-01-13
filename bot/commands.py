"""Command handlers for the bot."""

import random
import discord
from typing import List

from .constants import HELP_MESSAGE, REPORT_MESSAGE, MIX_COMMAND, HELP_COMMAND, REPORT_COMMAND
from .utils import create_team_message, parse_players, get_voice_channel_members, extract_groups_from_text


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

    users = []
    groups = None

    # If no arguments, try to get players from voice channel
    if not cleaned_input:
        voice_members = get_voice_channel_members(message)
        if voice_members:
            users = voice_members
        else:
            await message.channel.send(
                "🚨 Você precisa estar em um canal de voz OU informar o nome dos jogadores! "
                "Não é tão difícil, basta ler as instruções ou entrar no canal de voz. 🙄"
            )
            return
    else:
        users = parse_players(cleaned_input, message)

        if not users or len(users) < 2:
            await message.channel.send(
                "🚨 Precisa de pelo menos 2 jogadores para fazer um mix! "
                "Você consegue digitar pelo menos 2 nomes, né? 😒"
            )
            return

        groups = extract_groups_from_text(cleaned_input, message) or None

    # Create buttons
    view = MixView(users, groups)

    # Send message with teams and buttons
    await message.reply(
        content=create_team_message(users, groups),
        view=view,
        mention_author=False
    )


class MixView(discord.ui.View):
    """View with buttons for team reshuffling."""

    def __init__(self, users: List[str], groups: List[List[str]] = None):
        super().__init__(timeout=None)
        self.users = users
        self.groups = groups

    @discord.ui.button(label="🔮 Não tá balanceado", style=discord.ButtonStyle.primary, custom_id="reshuffle")
    async def reshuffle_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Reshuffle teams when button is clicked."""
        await interaction.response.edit_message(content=create_team_message(self.users, self.groups), view=self)

    @discord.ui.button(label="✅ Aceito", style=discord.ButtonStyle.success, custom_id="accept")
    async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Accept teams and remove buttons."""
        await interaction.response.edit_message(view=None)
