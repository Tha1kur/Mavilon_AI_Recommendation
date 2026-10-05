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


@pytest.mark.parametrize("body", [{}, {"session_id": None}])
def test_new_session_body_forms(users_api, body):
    client, sessions, User, TasteProfile = users_api
    response = client.post("/api/users/session", json=body)
    assert response.status_code == 200
    data = response.json()
    assert data["is_new"] is True
    with sessions() as db:
        user = db.query(User).one()
        assert data == {"session_id": user.session_id, "user_id": user.id, "is_new": True}
        assert db.query(TasteProfile).filter_by(user_id=user.id).count() == 1


def test_repeated_return_preserves_identity_and_profile(users_api):
    client, sessions, User, TasteProfile = users_api
    first = client.post("/api/users/session").json()
    with sessions() as db:
        profile = db.query(TasteProfile).one()
        profile.favorite_genres = {"Drama": 2.75}
        db.commit()
    for _ in range(3):
        response = client.post("/api/users/session", json={"session_id": first["session_id"]})
        assert response.status_code == 200
        assert response.json() == {**first, "is_new": False}
    with sessions() as db:
        assert db.query(User).count() == 1
        assert db.query(TasteProfile).one().favorite_genres == {"Drama": 2.75}


def test_unknown_session_is_not_created(users_api):
    client, sessions, User, _ = users_api
    response = client.post("/api/users/session", json={"session_id": "unknown-test-identity"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Session not found"}
    with sessions() as db:
        assert db.query(User).count() == 0


@pytest.mark.parametrize("body", [
    {"session_id": ""}, {"session_id": 123}, {"session_id": []},
    {"session_id": {}}, {"session_id": True}, {"sessionId": "typo"},
])
def test_invalid_session_body_does_not_create_user(users_api, body):
    client, sessions, User, _ = users_api
    assert client.post("/api/users/session", json=body).status_code == 422
    with sessions() as db:
        assert db.query(User).count() == 0


def test_query_transport_is_rejected_even_with_valid_body(users_api):
    client, sessions, User, _ = users_api
    sid = client.post("/api/users/session").json()["session_id"]
    for body in (None, {"session_id": sid}):
        response = client.post("/api/users/session", params={"session_id": sid}, json=body)
        assert response.status_code == 400
        assert sid not in response.text
    with sessions() as db:
        assert db.query(User).count() == 1


def test_existing_legacy_opaque_identity_can_return(users_api):
    client, sessions, User, _ = users_api
    # Old clients could persist non-UUID fallback identifiers.
    with sessions() as db:
        user = User(session_id="fallback_test_legacy")
        db.add(user)
        db.commit()
        user_id = user.id
    response = client.post("/api/users/session", json={"session_id": "fallback_test_legacy"})
    assert response.json() == {"session_id": "fallback_test_legacy", "user_id": user_id, "is_new": False}
    with sessions() as db:
        assert db.query(User).count() == 1


@pytest.mark.parametrize("stored", [None, {}, []])
def test_empty_profile_has_score_maps(users_api, stored):
    client, sessions, User, TasteProfile = users_api
    sid = client.post("/api/users/session").json()["session_id"]
    with sessions() as db:
        profile = db.query(TasteProfile).one()
        profile.favorite_genres = stored
        profile.favorite_moods = stored
        db.commit()
    response = client.get(f"/api/users/{sid}/profile")
    assert response.status_code == 200
    assert response.json() == {"favorite_genres": {}, "favorite_moods": {}, "interaction_count": 0}


def test_missing_profile_has_empty_score_maps(users_api):
    client, sessions, User, TasteProfile = users_api
    sid = client.post("/api/users/session").json()["session_id"]
    with sessions() as db:
        db.delete(db.query(TasteProfile).one())
        db.commit()
    assert client.get(f"/api/users/{sid}/profile").json() == {
        "favorite_genres": {}, "favorite_moods": {}, "interaction_count": 0,
    }


def test_profile_preserves_fractional_scores_moods_and_count(users_api):
    client, sessions, User, TasteProfile = users_api
    sid = client.post("/api/users/session").json()["session_id"]
    expected = {"favorite_genres": {"Action": 1.95, "Drama": 0.125},
                "favorite_moods": {"Dark": 2.75, "Calm": 0.5}, "interaction_count": 7}
    with sessions() as db:
        profile = db.query(TasteProfile).one()
        for key, value in expected.items():
            setattr(profile, key, value)
        db.commit()
    response = client.get(f"/api/users/{sid}/profile")
    assert response.status_code == 200
    assert response.json() == expected


def test_legacy_profile_lists_keep_labels_with_service_default_scores(users_api):
    client, sessions, User, TasteProfile = users_api
    sid = client.post("/api/users/session").json()["session_id"]
    with sessions() as db:
        profile = db.query(TasteProfile).one()
        profile.favorite_genres = ["Action", "Drama"]
        profile.favorite_moods = ["Dark"]
        db.commit()
    data = client.get(f"/api/users/{sid}/profile").json()
    assert data["favorite_genres"] == {"Action": 1.0, "Drama": 1.0}
    assert data["favorite_moods"] == {"Dark": 1.0}


def test_session_storage_failure_is_sanitized(users_api, monkeypatch):
    client, sessions, User, _ = users_api
    from routers.users import user_service
    def fail(*args):
        raise RuntimeError("private database details")
    monkeypatch.setattr(user_service, "get_or_create_user", fail)
    response = client.post("/api/users/session")
    assert response.status_code == 500
    assert response.json() == {"detail": "Failed to create session"}


def test_invalid_populated_profile_is_error_not_empty_success(users_api):
    client, sessions, User, TasteProfile = users_api
    sid = client.post("/api/users/session").json()["session_id"]
    with sessions() as db:
        profile = db.query(TasteProfile).one()
        profile.favorite_genres = {"Action": "not-a-score"}
        db.commit()
    response = client.get(f"/api/users/{sid}/profile")
    assert response.status_code == 500
    assert response.json() == {"detail": "Failed to get profile"}
