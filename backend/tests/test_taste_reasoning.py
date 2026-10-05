import pytest
from services.taste_reasoning import TasteReasoning as Taste


def test_confidence_increases_and_saturates():
    values = [Taste.compute_taste_confidence(n) for n in range(101)]
    assert values == sorted(values)
    assert values[0] == 0
    assert values[-1] == 1
    assert all(0 <= v <= 1 for v in values)


def test_exploration_is_reproducible_and_disabled_for_cold_start():
    assert not Taste.should_explore(0, 0, random_seed=0)
    assert Taste.should_explore(0.3, 6, random_seed=0.01)
    assert not Taste.should_explore(0.3, 6, random_seed=0.9)


def test_exploration_expands_beyond_existing_genres():
    adjacent = Taste.get_adjacent_genres(["Sci-Fi", "Action"])
    assert "Thriller" in adjacent
    assert not adjacent.intersection({"Sci-Fi", "Action"})
    assert Taste.get_adjacent_genres([]) == set()
    assert Taste.compute_exploration_bonus(["Thriller"], ["Sci-Fi"], False) == 0


def test_missing_moods_do_not_create_a_match():
    assert Taste.compute_mood_match_score(None, "Action", ["Action"]) == 0
    assert Taste.compute_mood_match_score(["Romance"], "Action", []) == 0
    assert Taste.compute_mood_match_score(["Action"], "Action", ["Action"]) == pytest.approx(1)


def test_rating_and_popularity_order_without_unbounded_scores():
    ratings = [Taste.compute_rating_boost(x) for x in [0, 3, 6, 7, 8, 10]]
    assert ratings == sorted(ratings)
    assert all(0 <= v <= 1 for v in ratings)
    assert Taste.compute_popularity_score(None) == 0
    assert Taste.compute_popularity_score(0) == 0
    assert Taste.compute_popularity_score(10) < Taste.compute_popularity_score(100)
    assert Taste.compute_popularity_score(1e20) == 1


def test_recency_and_diversity_boundaries():
    assert Taste.compute_recency_score(0, 2026) == 0
    assert Taste.compute_recency_score(2027, 2026) == 1
    assert Taste.compute_recency_score(1990, 2026) < Taste.compute_recency_score(2020, 2026)
    assert Taste.compute_diversity_penalty(0.5) == 0
    assert Taste.compute_diversity_penalty(0.9) > 0
