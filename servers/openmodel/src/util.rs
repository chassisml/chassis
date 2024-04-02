use std::time::Duration;

use tokio::sync::broadcast::Receiver;
use tokio::time::sleep;
use tracing::info;

/// Handler for performing a graceful server shutdown.
///
/// This async func will block until it receives a message on the supplied channel, then return.
/// This method is suitable for passing into the `graceful_shutdown` methods of servers from
/// Hyper, Tonic, Axum, etc.
pub async fn graceful_shutdown(mut rx: Receiver<()>) -> () {
    // Wait for a signal, then delay for a short time before returning.
    // Once this function returns, the tonic server will shut down.
    let _ = rx.recv().await;
    info!("Starting graceful shutdown in 1 second.");
    sleep(Duration::from_secs(1)).await;
    ()
}
