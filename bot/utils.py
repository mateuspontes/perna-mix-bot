"""Utility functions for the bot."""

import re
import random
import discord
from typing import List, Optional, Tuple, Dict


def parse_players(text: str, message: discord.Message) -> List[str]:
    """Parse player names from text input, handling multiple formats.

    Supports:
    - Multiple separators: comma, hyphen, space, newline
    - Discord mentions (@user, <@id>, <@!id>)
    - Extracts display names from mentions
    - Removes extra spaces and empty entries
    - Removes duplicates

    Args:
        text: Raw text input from user
        message: Discord message object to access mentions

    Returns:
        List of cleaned player names
    """
    if not text:
        return []

    # Replace Discord mentions (<@id> or <@!id>) with display names
    mention_pattern = r'<@!?(\d+)>'
    mentions = re.findall(mention_pattern, text)

    for user_id in mentions:
        member = message.guild.get_member(int(user_id))
        if member:
            # Replace mention with display name
            text = re.sub(f'<@!?{user_id}>', member.display_name, text)

    text = re.sub(r'[()[\]{}]', ' ', text)

    # Note: @username format (not a real mention) will be handled by separator logic
    # The @ symbol will be part of the name or treated as separator depending on context

    # Split by multiple separators: comma, hyphen, space, newline
    # Use regex to split on any of these separators
    # Note: hyphen must be at start/end of character class or escaped
    separators = r'[,;\s\n-]+'
    players = re.split(separators, text)

    # Clean up players
    cleaned_players = []
    seen = set()

    for player in players:
        player = player.strip()
        # Remove empty strings and very short names (likely artifacts)
        if player and len(player) > 0:
            # Normalize: remove extra spaces, convert to lowercase for duplicate check
            normalized = ' '.join(player.split())
            normalized_lower = normalized.lower()

            # Check for duplicates (case-insensitive)
            if normalized_lower not in seen:
                seen.add(normalized_lower)
                cleaned_players.append(normalized)

    return cleaned_players


def extract_groups_from_text(text: str, message: discord.Message) -> List[List[str]]:
    """Extract player groups from text using (), [] or {} brackets.

    Args:
        text: Raw text input from user
        message: Discord message object to access mentions

    Returns:
        List of groups, where each group is a list of player names
    """
    if not text:
        return []

    # Replace Discord mentions with display names first
    mention_pattern = r'<@!?(\d+)>'
    mentions = re.findall(mention_pattern, text)

    for user_id in mentions:
        member = message.guild.get_member(int(user_id))
        if member:
            text = re.sub(f'<@!?{user_id}>', member.display_name, text)

    groups = []

    patterns = [
        r'\(([^()]+)\)',
        r'\[([^\[\]]+)\]',
        r'\{([^{}]+)\}',
    ]

    for pattern in patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            group_content = match.group(1)
            separators = r'[,;\s\n-]+'
            group_players = [p.strip() for p in re.split(
                separators, group_content) if p.strip()]
            cleaned_group = []
            for player in group_players:
                normalized = ' '.join(player.split())
                if normalized:
                    cleaned_group.append(normalized)
            if cleaned_group:
                groups.append(cleaned_group)

    return groups


def balance_teams_with_groups(players: List[str], groups: List[List[str]]) -> List[str]:
    """Balance teams by distributing groups evenly between teams.

    Strategy:
    - For each group, distribute players evenly between teams (splitting each group)
    - Fill remaining slots with ungrouped players randomly
    - This ensures balanced distribution while maintaining randomness

    Args:
        players: List of all player names
        groups: List of groups, where each group is a list of player names

    Returns:
        List of players ordered for team distribution (first half = team A, second half = team B)
    """
    if not groups:
        shuffled = players.copy()
        random.shuffle(shuffled)
        return shuffled

    grouped_players_set = set()
    for group in groups:
        for player in group:
            grouped_players_set.add(player.lower())

    grouped_players_dict = {}
    ungrouped_players = []

    for player in players:
        player_lower = player.lower()
        if player_lower in grouped_players_set:
            grouped_players_dict[player_lower] = player
        else:
            ungrouped_players.append(player)

    team_a_grouped = []
    team_b_grouped = []

    shuffled_groups = groups.copy()
    random.shuffle(shuffled_groups)

    for group in shuffled_groups:
        group_players = [grouped_players_dict[p.lower()]
                         for p in group if p.lower() in grouped_players_dict]
        random.shuffle(group_players)
        mid = (len(group_players) + 1) // 2
        team_a_grouped.extend(group_players[:mid])
        team_b_grouped.extend(group_players[mid:])

    random.shuffle(ungrouped_players)

    total_players = len(players)
    target_team_size = (total_players + 1) // 2

    current_a_size = len(team_a_grouped)
    current_b_size = len(team_b_grouped)

    remaining_ungrouped = len(ungrouped_players)
    ungrouped_a_count = (remaining_ungrouped + 1) // 2

    if current_a_size + ungrouped_a_count > current_b_size + (remaining_ungrouped - ungrouped_a_count):
        ungrouped_a_count = remaining_ungrouped // 2

    team_a = team_a_grouped + ungrouped_players[:ungrouped_a_count]
    team_b = team_b_grouped + ungrouped_players[ungrouped_a_count:]

    random.shuffle(team_a)
    random.shuffle(team_b)

    return team_a + team_b


def get_voice_channel_members(message: discord.Message) -> Optional[List[str]]:
    """Get display names of all members in the author's voice channel.

    Args:
        message: Discord message object

    Returns:
        List of display names (excluding bots), or None if author is not in a voice channel
    """
    if not message.author.voice or not message.author.voice.channel:
        return None

    voice_channel = message.author.voice.channel
    members = []

    for member in voice_channel.members:
        # Exclude bots
        if not member.bot:
            members.append(member.display_name)

    return members if members else None


def create_team_message(users: List[str], groups: Optional[List[List[str]]] = None) -> str:
    """Create team assignment message from list of users.

    Handles different player counts:
    - > 10: Randomly selects who stays out (groups don't affect this), then balances remaining 10
    - = 10: Normal division into 2 teams of 5 (with group balancing if applicable)
    - < 10: Divides equally and indicates how many are missing to complete 5 per team

    If groups are provided, uses balanced distribution for team assignment (not for selection of who stays out).

    Args:
        users: List of user names
        groups: Optional list of player groups for balanced distribution

    Returns:
        Formatted message with team assignments
    """
    if not users:
        return "Nenhum jogador encontrado."

    if len(users) > 10:
        shuffled_all = users.copy()
        random.shuffle(shuffled_all)
        num_out = len(shuffled_all) - 10
        out_players = shuffled_all[:num_out]
        playing_players = shuffled_all[num_out:]

        playing_players_set = {p.lower() for p in playing_players}
        filtered_groups = None
        if groups:
            filtered_groups = []
            for group in groups:
                group_in_players = all(
                    p.lower() in playing_players_set for p in group)
                if group_in_players and len(group) > 1:
                    filtered_groups.append(group)
            if not filtered_groups:
                filtered_groups = None

        if filtered_groups:
            balanced_players = balance_teams_with_groups(
                playing_players, filtered_groups)
        else:
            balanced_players = playing_players.copy()
            random.shuffle(balanced_players)

        team_a = balanced_players[:5]
        team_b = balanced_players[5:10]

        response = f"# Time A 🔫\n {', '.join(team_a)}\n\n# Time B 🔫\n {', '.join(team_b)}"
        response += f"\n\n# Lista de Espera ⏳\n {', '.join(out_players)}"

        return response

    if groups:
        shuffled = balance_teams_with_groups(users, groups)
    else:
        shuffled = users.copy()
        random.shuffle(shuffled)

    if len(shuffled) == 10:
        team_a = shuffled[:5]
        team_b = shuffled[5:10]

        response = f"# Time A 🔫\n {', '.join(team_a)}\n\n# Time B 🔫\n {', '.join(team_b)}"
        return response

    # Less than 10 players: divide equally and indicate missing
    # Divide as equally as possible
    # For odd numbers, first team gets the extra player
    half = (len(shuffled) + 1) // 2
    team_a = shuffled[:half]
    team_b = shuffled[half:]

    # Calculate how many are missing to complete 5 per team
    missing_a = 5 - len(team_a)
    missing_b = 5 - len(team_b)

    response = f"# Time A 🔫\n {', '.join(team_a)}"
    if missing_a > 0:
        response += f" (+{missing_a} para completar)"

    response += f"\n\n# Time B 🔫\n {', '.join(team_b)}"
    if missing_b > 0:
        response += f" (+{missing_b} para completar)"

    return response
