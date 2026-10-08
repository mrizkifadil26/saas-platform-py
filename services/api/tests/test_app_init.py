from api.app import create_app


def test_create_app_smoke():
    app = create_app()
    assert app is not None


# def test_lifespan_runs():
#     app = create_app()

#     with TestClient(app) as client:
#         assert hasattr(app.state, "app_users_sessionmaker")
#         r = client.get("/health")

#         assert r.status_code == 200
