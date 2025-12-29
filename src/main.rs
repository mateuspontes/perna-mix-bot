use axum::{routing::get, Router};
use rand::seq::SliceRandom;
use rand::thread_rng;
use std::env;

use serenity::{
    async_trait,
    builder::CreateComponents,
    model::application::{
        component::ButtonStyle,
        interaction::{Interaction, InteractionResponseType},
    },
    model::{channel::Message, gateway::Ready},
    prelude::*,
    framework::standard::{
        macros::{command, group},
        CommandResult, StandardFramework,
    },
};
use serenity::model::prelude::ChannelId;

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

fn create_team_message(users: &[&str]) -> String {
    let half = (users.len() / 2).min(5);
    let team_a: Vec<&str> = users.iter().take(half).copied().collect();
    let team_b: Vec<&str> = users.iter().skip(half).take(5).copied().collect();
    let team_wait: Vec<&str> = users.iter().skip(half + 5).copied().collect();

    let mut response = format!(
        "# Time A 🔫\n {}\n\n# Time B 🔫\n {}",
        team_a.join(", "),
        team_b.join(", ")
    );

    if !team_wait.is_empty() {
        response.push_str(&format!(
            "\n\n# Lista de Espera ⏳\n {}",
            team_wait.join(", ")
        ));
    }

    response
}

async fn send_error_message(ctx: &Context, channel_id: ChannelId, message: &str) {
    if let Err(why) = channel_id.say(&ctx.http, message).await {
        println!("Error sending message: {:?}", why);
    }
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
            let cleaned_input = msg
                .content
                .strip_prefix(MIX_COMMAND)
                .unwrap_or(msg.content.as_str());

            if cleaned_input.trim().is_empty() {
                send_error_message(&ctx, msg.channel_id, "🚨 Você precisa informar o nome dos jogadores, separados por vírgula! Não é tão difícil, basta ler.").await;
                return;
            }

            if let Err(why) = msg.channel_id.say(&ctx.http, REPORT_MESSAGE).await {
                println!("Error sending message: {:?}", why);
            }
        }

        if msg.content.starts_with(MIX_COMMAND) {
            let cleaned_input = msg
                .content
                .strip_prefix(MIX_COMMAND)
                .unwrap_or(msg.content.as_str());

            if cleaned_input.trim().is_empty() {
                send_error_message(&ctx, msg.channel_id, "🚨 Você precisa informar o nome dos jogadores, separados por vírgula! Não é tão difícil, basta ler.").await;
                return;
            }

            let users: Vec<&str> = cleaned_input.split(',').map(|s| s.trim()).collect();
            let mut shuffled_users = users.clone();
            shuffled_users.shuffle(&mut thread_rng());

            // Create buttons
            let mut components = CreateComponents::default();
            components.create_action_row(|row| {
                row.create_button(|button| {
                    button
                        .custom_id("reshuffle")
                        .label("🔮 Não tá balanceado")
                        .style(ButtonStyle::Primary)
                })
                .create_button(|button| {
                    button
                        .custom_id("accept")
                        .label("✅ Aceito")
                        .style(ButtonStyle::Success)
                })
            });

            // Store the original users in the button's custom_id
            let custom_id = format!("reshuffle:{}", users.join(","));

            if let Err(why) = msg
                .channel_id
                .send_message(&ctx.http, |m| {
                    m.content(create_team_message(&shuffled_users))
                        .components(|c| {
                            c.create_action_row(|row| {
                                row.create_button(|button| {
                                    button
                                        .custom_id(custom_id)
                                        .label("🔮 Não tá balanceado")
                                        .style(ButtonStyle::Primary)
                                })
                                .create_button(|button| {
                                    button
                                        .custom_id("accept")
                                        .label("✅ Aceito")
                                        .style(ButtonStyle::Success)
                                })
                            })
                        })
                        .reference_message(&msg)
                })
                .await
            {
                println!("Error sending message: {:?}", why);
            }
        }
    }

    async fn ready(&self, ctx: Context, ready: Ready) {
        println!("{} is connected!", ready.user.name);

        // Send startup message to a specific channel
        let channel_id = ChannelId(1132852398654754866);
        let startup_message = "🤖 **Perna Bot está ONLINE!** 🎯";

        if let Err(why) = channel_id.say(&ctx.http, startup_message).await {
            println!("Error sending startup message: {:?}", why);
        }
    }

    async fn interaction_create(&self, ctx: Context, interaction: Interaction) {
        if let Interaction::MessageComponent(component) = interaction {
            if component.data.custom_id.starts_with("reshuffle:") {
                let users_str = component.data.custom_id.strip_prefix("reshuffle:").unwrap();
                let mut users: Vec<&str> = users_str.split(',').collect();
                users.shuffle(&mut thread_rng());

                if let Err(why) = component
                    .create_interaction_response(&ctx.http, |response| {
                        response
                            .kind(InteractionResponseType::UpdateMessage)
                            .interaction_response_data(|data| {
                                data.content(create_team_message(&users));
                                data
                            })
                    })
                    .await
                {
                    println!("Error responding to interaction: {:?}", why);
                }
            } else if component.data.custom_id == "accept" {
                let original_message = component.message.content.clone();

                if let Err(why) = component
                    .create_interaction_response(&ctx.http, |response| {
                        response
                            .kind(InteractionResponseType::UpdateMessage)
                            .interaction_response_data(|data| {
                                data.content(original_message).components(|c| c); // Remove os botões
                                data
                            })
                    })
                    .await
                {
                    println!("Error responding to interaction: {:?}", why);
                }
            }
        }
    }
}

#[group]
#[commands(ping)]
struct General;

#[command]
async fn ping(ctx: &Context, msg: &Message) -> CommandResult {
    msg.reply(ctx, "Pong!").await?;
    Ok(())
}

#[tokio::main]
async fn main() {
    // Get Discord token from environment variable
    let token = env::var("DISCORD_TOKEN").expect("Expected DISCORD_TOKEN in environment");

    let framework = StandardFramework::new()
        .configure(|c| c.prefix("!"))
        .group(&GENERAL_GROUP);

    let mut client = Client::builder(token, GatewayIntents::all())
        .framework(framework)
        .event_handler(Handler)
        .await
        .expect("Error creating client");

    // Clone the HTTP client for the shutdown handler
    let http = client.cache_and_http.http.clone();

    // Spawn the Discord client in a separate task
    let client_handle = tokio::spawn(async move {
        if let Err(why) = client.start().await {
            println!("Client error: {:?}", why);
        }
    });

    // Spawn the web server in a separate task
    let web_handle = tokio::spawn(async move {
        let port = env::var("PORT").unwrap_or_else(|_| "10000".to_string());
        let addr = format!("0.0.0.0:{}", port);

        let router = Router::new()
            .route("/", get(home))
            .route("/healthcheck", get(healthcheck));

        println!("Web server listening on {}", addr);

        let listener = tokio::net::TcpListener::bind(&addr).await.unwrap();
        axum::serve(listener, router).await.unwrap();
    });

    // Setup shutdown signal handler
    tokio::select! {
        _ = client_handle => {
            println!("Discord client stopped");
        }
        _ = web_handle => {
            println!("Web server stopped");
        }
        _ = tokio::signal::ctrl_c() => {
            println!("Received shutdown signal, sending goodbye message...");

            // Send shutdown message
            let channel_id = ChannelId(1132852398654754866);
            let shutdown_message = "🔴 **Perna Bot está OFFLINE!** \nVolto em breve para sortear Mix! 👋";

            if let Err(why) = channel_id.say(&http, shutdown_message).await {
                println!("Error sending shutdown message: {:?}", why);
            }

            // Give some time for the message to be sent
            tokio::time::sleep(tokio::time::Duration::from_secs(2)).await;
        }
    }
}
