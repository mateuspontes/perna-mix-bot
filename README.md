# Perna Mix Bot 🐦🤖

Bot Discord para sortear times de MIX de forma aleatória e equilibrada.

## Funcionalidades

- **!help** - Mostra a mensagem de ajuda com todos os comandos disponíveis
- **!mix** - Sorteia times aleatórios a partir de uma lista de jogadores separados por vírgula
- **!report** - Sistema de reporte de usuários para moderação

### Sorteio de Times

O comando `!mix` divide os jogadores em dois times de até 5 jogadores cada, com lista de espera se necessário. Os times podem ser reembaralhados com o botão "🔮 Não tá balanceado" até que estejam satisfeitos.

## Tecnologias

- **Python 3.11**
- **discord.py** - Biblioteca para interagir com a API do Discord
- **aiohttp** - Servidor web assíncrono para health checks

## Estrutura do Projeto

```
perna-mix-bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Cliente Discord e event handlers
│   ├── commands.py         # Handlers de comandos (!help, !mix, !report)
│   ├── constants.py        # Constantes e mensagens
│   ├── utils.py           # Funções utilitárias
│   └── web_server.py      # Servidor web para healthcheck
├── main.py                # Entry point da aplicação
├── requirements.txt       # Dependências Python
├── render.yaml           # Configuração de deploy no Render.com
└── README.md
```

## Instalação Local

1. Clone o repositório:
```bash
git clone <repo-url>
cd perna-mix-bot
```

2. Crie um ambiente virtual e instale as dependências:
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente:
```bash
export DISCORD_TOKEN="seu-token-aqui"
export PORT=10000  # Opcional, padrão é 10000
```

4. Execute o bot:
```bash
python main.py
```

## Deploy no Render.com

O bot está configurado para deploy automático no Render.com usando o arquivo `render.yaml`.

### Passos para Deploy:

1. Faça push do código para o GitHub
2. Conecte seu repositório no Render.com
3. Configure a variável de ambiente `DISCORD_TOKEN` no painel do Render
4. O deploy será feito automaticamente

### Configuração de Ambiente no Render:

- **DISCORD_TOKEN**: Token do bot Discord (obrigatório)
- **PORT**: Porta do servidor web (padrão: 10000)

## Desenvolvimento

### Adicionando Novos Comandos

1. Adicione a constante do comando em [bot/constants.py](bot/constants.py)
2. Crie o handler em [bot/commands.py](bot/commands.py)
3. Adicione a lógica de roteamento em [bot/client.py](bot/client.py) no método `on_message`

### Health Check

O servidor web expõe dois endpoints:
- `/` - Mensagem de boas-vindas
- `/healthcheck` - Endpoint para health checks do Render.com

## Licença

MIT

---

Desenvolvido com ❤️ para a comunidade Perna
