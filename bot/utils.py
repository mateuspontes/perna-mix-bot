"""Utility functions for the bot."""

from typing import List


def create_team_message(users: List[str]) -> str:
    """Create team assignment message from list of users.

    Args:
        users: List of user names

    Returns:
        Formatted message with team assignments
    """
    half = min(len(users) // 2, 5)
    team_a = users[:half]
    team_b = users[half:half + 5]
    team_wait = users[half + 5:]

    response = f"# Time A 🔫\n {', '.join(team_a)}\n\n# Time B 🔫\n {', '.join(team_b)}"

    if team_wait:
        response += f"\n\n# Lista de Espera ⏳\n {', '.join(team_wait)}"

    return response
