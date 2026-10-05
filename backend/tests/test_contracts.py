import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError
from models.content import Movie, Anime, RecommendRequest


@pytest.mark.parametrize("limit", [0, -1, 21])
def test_recommendation_request_rejects_out_of_bounds_limits(limit):
    with pytest.raises(ValidationError):
        RecommendRequest(limit=limit)


def test_recommendation_request_defaults_and_http_validation():
    # Exercise the real request model through FastAPI without importing main,
    # which downloads models and mutates a working-directory database.
    app = FastAPI()
    @app.post("/request")
    def request(body: RecommendRequest):
        return body
    with TestClient(app) as client:
        assert client.post("/request", json={}).json()["limit"] == 6
        assert client.post("/request", json={"limit": 21}).status_code == 422


@pytest.mark.parametrize("model,kind", [(Movie, "movie"), (Anime, "anime")])
def test_content_contract_preserves_client_field_names(model, kind):
    item = model(id=f"{kind}_1", title="Fixture", posterUrl="https://example.invalid/poster",
                 genres=[], rating=7, overview="Fixture overview")
    payload = item.model_dump()
    assert payload["type"] == kind
    assert payload["posterUrl"].endswith("/poster")
    assert payload["year"] is None
