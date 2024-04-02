use openmodel_server::OpenModelServer;

#[tokio::main]
async fn main() -> Result<(), anyhow::Error> {
    OpenModelServer::build()
        .enable_v2_service(true)
        .start()
        .await
}
