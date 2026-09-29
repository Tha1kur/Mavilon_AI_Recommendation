import asyncio
import sys
import os

# Add backend to path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.tmdb_service import tmdb_service
from services.recommendation_service import recommendation_service
from services.taste_reasoning import taste_reasoning
from models.content import Movie

async def verify_pipeline():
    print("--- Starting Verification ---")
    
    print("\n1. Testing AniList Fetch & Normalization (Popularity & Configs)...")
    trending_anime = await tmdb_service.get_trending_anime(limit=10)
    if not trending_anime:
        print("❌ Failed to fetch anime")
        return
        
    print(f"✅ Fetched {len(trending_anime)} anime.")
    sample = trending_anime[0]
    print(f"Sample Anime: {sample.title}")
    print(f" - Rating: {sample.rating}")
    print(f" - Popularity: {sample.popularity}")
    print(f" - Mood: {sample.mood}")
    print(f" - Studio/Characters: {sample.studio} / {sample.characters[:2] if sample.characters else 'None'}")
    
    print("\n2. Testing Math Functions...")
    rating_boost = taste_reasoning.compute_rating_boost(sample.rating)
    pop_score = taste_reasoning.compute_popularity_score(sample.popularity)
    recency = taste_reasoning.compute_recency_score(sample.year, 2026, 0.05)
    print(f" - Rating Boost ({sample.rating}): {rating_boost:.3f}")
    print(f" - Pop Score ({sample.popularity}): {pop_score:.3f}")
    print(f" - Recency ({sample.year}): {recency:.3f}")
    
    print("\n3. Testing Recommendation Pipeline (No Taste Profile)...")
    recommendation_service.load_model()
    # Wait for model to load
    import time
    while not recommendation_service.is_model_ready:
        time.sleep(0.5)
        
    print("✅ Model Loaded.")
    
    # Test text parsing
    text = recommendation_service._get_content_text(sample)
    print(f"Parsed Text Length: {len(text)} chars")
    print(f"Preview: {text[:100]}...")
    
    recs = recommendation_service.get_personalized_recommendations(
        all_content=trending_anime,
        user_taste_embedding=None,
        mood="Action",
        limit=3,
        ensure_diversity=True,
    )
    
    print(f"\n✅ Fetched {len(recs)} fallback recommendations (No Profile, Action Mood):")
    for r in recs:
        # returns Tuple of (content, score, exploration)
        content = r[0]
        score = r[1]
        print(f"  - {content.title} (Score: {score:.3f}, Moods: {content.mood})")
        
    print("\n4. Testing Pipeline (Simulated Taste Profile)...")
    # Simulate a user embedding by encoding a strong Action/Sci-Fi preface
    simulated_taste = recommendation_service.model.encode(
         "I love massive explosions, high stakes action, space warfare, futuristic cybernetics, and intense thrillers.",
         convert_to_numpy=True
    )
    
    # Run personalized recommendations
    personalized_recs = recommendation_service.get_personalized_recommendations(
        all_content=trending_anime,
        user_taste_embedding=simulated_taste,
        mood=None,  # Dynamic mood instead of hard filter
        limit=5,
        ensure_diversity=True,
        interaction_count=15,
        favorite_genres={"Action": 5, "Sci-Fi": 4, "Thriller": 2},
        favorite_moods={"Action": 5, "Dark": 3}
    )
    
    print(f"\n✅ Fetched {len(personalized_recs)} personalized recommendations:")
    for i, (content, score, is_exp) in enumerate(personalized_recs):
        print(f"  {i+1}. {content.title}")
        print(f"     Score: {score:.3f} {'[EXPLORE]' if is_exp else ''} | Rating: {content.rating} | Pop: {content.popularity:.1f} | Genres: {content.genres}")
        
    print("\n✅ Verification Script Complete.")

if __name__ == "__main__":
    asyncio.run(verify_pipeline())
