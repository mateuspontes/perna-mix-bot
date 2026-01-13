"""Constants used throughout the bot."""

HELP_MESSAGE = """
Perna Bot aqui! 🐦

Você invocou meus poderes, vamos ver o que posso fazer por você:

❓ Sorteio de um MIX?
➡️ Digite `!mix` com o nome dos jogadores separados por vírgula, espaço, hífen... (aceito qualquer formato burro mesmo)

   **Exemplos:**
   • `!mix João, Maria, Pedro, Ana` (vírgula)
   • `!mix João Maria Pedro Ana` (espaço)
   • `!mix João - Maria - Pedro` (hífen)
   • `!mix @João @Maria @Pedro` (menções do Discord)
   • `!mix` (estando em um canal de voz - pega todos automaticamente! 🎤)

🚫 **ANTI-PANELA:** Use parênteses, colchetes ou chaves para marcar jogadores que jogam muito juntos!
   Os jogadores agrupados serão **SEPARADOS** entre os times para equilibrar.

   **Exemplos:**
   • `!mix (João, Maria) Pedro Ana Carlos` → João e Maria vão para times diferentes
   • `!mix [Tryhard1, Tryhard2] Casual1 Casual2` → Os tryhards são separados
   • `!mix {Amigo1, Amigo2, Amigo3} Resto1 Resto2` → Amigos distribuídos entre os times

   ⚖️ Resultado: Times mais equilibrados, sem panelinha dominando! 🎯

❓ Quer ver os mandamentos do Perna?
➡️ Aqui está: <https://discord.com/channels/776249840938123286/1128670966449438841/1128670966449438841>

❓ Alguém foi tóxico e você quer reportar?
➡️ Fale com um moderador ou use o comando `!report` para reportar um usuário.

Boa jogatina!

— PernaBot 🤖
"""

REPORT_MESSAGE = """
🚨 **Reporte de usuário** 🚨

👮‍♂️ Obrigado por enviar o usuário para a moderação. Vamos analisar o caso e tomar as devidas providências. 🚔
"""

# Channel ID for startup/shutdown messages
NOTIFICATION_CHANNEL_ID = 1132852398654754866

# Command prefixes
HELP_COMMAND = "!help"
MIX_COMMAND = "!mix"
REPORT_COMMAND = "!report"
