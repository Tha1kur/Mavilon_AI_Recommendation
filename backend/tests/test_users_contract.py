"""Real routes/database, isolated model constructor. Known defects remain failing."""
import importlib

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture
def users_api(monkeypatch, tmp_path):
    # Import-time model loading is an application defect. Replace only that
    # external boundary; exercise real HTTP parsing and persistence below.
    monkeypatch.chdir(tmp_path)
    import sentence_transformers
    monkeypatch.setattr(sentence_transformers, "SentenceTransformer", lambda *a, **k: object())
    users = importlib.import_module("routers.users")
    from database import Base
    from models.user import User, TasteProfile
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    sessions = sessionmaker(bind=engine)

    def database_session():
        with sessions() as session:
            yield session

    app = FastAPI()
    app.include_router(users.router, prefix="/api/users")
    app.dependency_overrides[users.get_db] = database_session
    try:
        with TestClient(app) as client:
            yield client, sessions, User, TasteProfile
    finally:
        engine.dispose()


def test_new_session_persists_once(users_api):
    client, sessions, User, _ = users_api
    response = client.post("/api/users/session")
    assert response.status_code == 200
    data = response.json()
    assert data["is_new"] is True
    with sessions() as db:
        assert db.query(User).filter_by(session_id=data["session_id"]).count() == 1


def test_returning_session_matches_actual_frontend_request(users_api):
    # ROADMAP APP-01: frontend sends JSON; backend currently reads query params.
    client, sessions, User, _ = users_api
    first = client.post("/api/users/session").json()["session_id"]
    response = client.post("/api/users/session", json={"session_id": first})
    assert response.status_code == 200
    assert response.json()["session_id"] == first
    with sessions() as db:
        assert db.query(User).count() == 1


def test_populated_profile_matches_persisted_and_frontend_shape(users_api):
    # ROADMAP APP-02: persisted score maps must survive the response contract.
    client, sessions, User, TasteProfile = users_api
    sid = client.post("/api/users/session").json()["session_id"]
    with sessions() as db:
        user = db.query(User).filter_by(session_id=sid).one()
        profile = db.query(TasteProfile).filter_by(user_id=user.id).one()
        profile.favorite_genres = {"Action": 1.0}
        profile.favorite_moods = {"Thriller": 0.5}
        profile.interaction_count = 1
        db.commit()
    response = client.get(f"/api/users/{sid}/profile")
    assert response.status_code == 200
    assert response.json()["favorite_genres"] == {"Action": 1.0}
