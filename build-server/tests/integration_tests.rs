use actix_web::http::{Method, StatusCode};
use actix_web::test::read_body;
use actix_web::{test, App};
use chassis_build_server;
use chassis_build_server::job_routes::download_job_tar;
use chassis_build_server::{health, root, test as test_fn};

#[actix_web::test]
async fn test_root() {
    let app = App::new().service(root);
    let svc = test::init_service(app).await;
    let req = test::TestRequest::with_uri("/").to_request();
    let resp = test::call_service(&svc, req).await;
    assert_eq!(resp.status(), StatusCode::OK);
    assert_eq!(read_body(resp).await, "Alive!")
}

#[actix_web::test]
async fn test_health() {
    let app = App::new().service(health);
    let svc = test::init_service(app).await;
    let req = test::TestRequest::with_uri("/health").to_request();
    let resp = test::call_service(&svc, req).await;
    assert_eq!(resp.status(), StatusCode::OK);
}

#[actix_web::test]
async fn test_test_route_returns_gone() {
    let app = App::new().service(test_fn);
    let svc = test::init_service(app).await;
    let req = test::TestRequest::with_uri("/test")
        .method(Method::POST)
        .to_request();
    let resp = test::call_service(&svc, req).await;
    assert_eq!(resp.status(), StatusCode::GONE);
}

#[actix_web::test]
async fn test_download_tar_route_returns_gone() {
    let app = App::new().service(download_job_tar);
    let svc = test::init_service(app).await;
    let req = test::TestRequest::with_uri("/job/123/download-tar").to_request();
    let resp = test::call_service(&svc, req).await;
    assert_eq!(resp.status(), StatusCode::GONE);
}
