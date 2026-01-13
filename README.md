# Perna Mix Bot 🐦🤖

Bot Discord para sortear times de MIX de forma aleatória e equilibrada, com sistema anti-panela integrado.

## Comandos

### !help
Mostra a mensagem de ajuda com todos os comandos e exemplos.

### !mix
Sorteia times aleatórios (até 5 jogadores por time) com múltiplas formas de uso:

**Formatos aceitos:**
- Vírgulas: `!mix João, Maria, Pedro`
- Espaços: `!mix João Maria Pedro`
- Hífens: `!mix João - Maria - Pedro`
- Menções Discord: `!mix @João @Maria @Pedro`
- Canal de voz: `!mix` (sem argumentos, pega todos do seu canal de voz automaticamente)

**Sistema Anti-Panela:**
Use parênteses `()`, colchetes `[]` ou chaves `{}` para agrupar jogadores que jogam muito juntos. Os jogadores agrupados serão **separados entre os times** para equilibrar a partida:
- `!mix (João, Maria) Pedro Ana Carlos` → João e Maria vão para times diferentes
- `!mix [Tryhard1, Tryhard2] Casual1 Casual2` → Os tryhards são separados
- `!mix {Amigo1, Amigo2, Amigo3} Resto1 Resto2` → Amigos distribuídos entre os times

**Funcionalidades:**
- Suporta mais de 10 jogadores (excedentes vão para lista de espera)
- Suporta menos de 10 jogadores (mostra quantos faltam para completar)
- Botão "🔮 Não tá balanceado" para refazer o sorteio
- Botão "✅ Aceito" para finalizar

### !report
Sistema de reporte de usuários tóxicos para moderação.

## Deploy

### pella.app (Free, renovação manual diária)

1. Acesse [pella.app](https://pella.app)
2. Faça upload do projeto
3. Configure a variável `DISCORD_TOKEN`
4. Start command: `python main.py`

### [Railway](https://railway.com/)

## Local

```bash
pip install -r requirements.txt
export DISCORD_TOKEN="seu-token"
python main.py
```

## Tecnologias

- Python 3.11
- discord.py

---

Desenvolvido com ❤️ para a comunidade Perna
