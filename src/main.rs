use axum::{routing::get, Router};
use rand::seq::SliceRandom;
use rand::thread_rng;
use shuttle_runtime::SecretStore;

use serenity::{
    async_trait,
    model::{channel::Message, gateway::Ready},
    prelude::*,
};

const HELP_MESSAGE: &str = "
Perna Bot aqui! 🐦

Você invocou meus poderes, vamos ver o que posso fazer por você:

❓ Sorteio de um MIX?
➡️ Digite `!mix` com o nome dos meliantes separados por vírgula.

❓ Quer ver os mandamentos do Perna?
➡️ Aqui está: <https://discord.com/channels/776249840938123286/1128670966449438841/1128670966449438841>

❓ Alguém foi tóxico e você quer reportar?
➡️ Fale com um moderador ou use o comando `!report` para reportar um usuário.

Boa jogatina!

— PernaBot 🤖
";

const REPORT_MESSAGE: &str = "
🚨 **Reporte de usuário** 🚨

👮‍♂️ Obrigado por enviar o usuário para a moderação. Vamos analisar o caso e tomar as devidas providências. 🚔
";

const HELP_COMMAND: &str = "!help";
const MIX_COMMAND: &str = "!mix";
const REPORT_COMMAND: &str = "!report";

struct Handler;

async fn home() -> &'static str {
    "Hello From Perna Mix Bot 👮‍♂️"
}

async fn healthcheck() -> &'static str {
    "Working"
}

#[async_trait]
impl EventHandler for Handler {
    async fn message(&self, ctx: Context, msg: Message) {
        if msg.content == HELP_COMMAND {
            if let Err(why) = msg.channel_id.say(&ctx.http, HELP_MESSAGE).await {
                println!("Error sending message: {:?}", why);
            }
        }

        if msg.content.starts_with(REPORT_COMMAND) {
            if let Err(why) = msg.channel_id.say(&ctx.http, REPORT_MESSAGE).await {
                println!("Error sending message: {:?}", why);
            }
        }

        if msg.content.starts_with(MIX_COMMAND) {
            let cleaned_input = msg
                .content
                .strip_prefix(MIX_COMMAND)
                .unwrap_or(msg.content.as_str());


            // if the input is empty, return an error message
            if cleaned_input.trim().is_empty() {
                if let Err(why) = msg.channel_id.say(&ctx.http, "🚨 Você precisa informar o nome dos jogadores, separados por vírgula! Não é tão difícil, basta ler.")
                    .await {
                    println!("Error sending message: {:?}", why);
                }
                return;

            } else {
                println!("Vamos sortear um mix com os meliantes: {:?}", cleaned_input);

                // get the parameters separated by comma, split then by comma and trim the whitespaces
                let mut users: Vec<&str> = cleaned_input.split(',').map(|s| s.trim()).collect();

                // shuffle the list
                users.shuffle(&mut thread_rng());

                // get the first 5 users from the list
                let team_a: Vec<&str> = users.iter().take(5).copied().collect();
                let team_b: Vec<&str> = users.iter().skip(5).copied().collect();

                let response = format!(
                    "# Time A 🔫:\n {}\n\n# Time B 🔫:\n {}\n\n🔮 Chama novamente se alguém chorar dizendo que não tá balanceado 😢",
                    team_a.join(", "),
                    team_b.join(", ")
                );

                if let Err(why) = msg.channel_id.say(&ctx.http, response).await {
                    println!("Error sending message: {:?}", why);
                }
            }
        }
    }

    async fn ready(&self, _: Context, ready: Ready) {
        println!("{} is connected!", ready.user.name);
    }
}

#[shuttle_runtime::main]
pub async fn axum(#[shuttle_runtime::Secrets] secrets: SecretStore) -> shuttle_axum::ShuttleAxum {
    let token = secrets.get("DISCORD_TOKEN");

    let mut client = Client::builder(token.unwrap(), GatewayIntents::all())
        .event_handler(Handler)
        .await
        .expect("Err creating client");

    let router = Router::new()
        .route("/", get(home))
        .route("/healthcheck", get(healthcheck));

    if let Err(why) = client.start().await {
        println!("Client error: {:?}", why);
    }

    Ok(router.into())
}
