# MAVILON AI Recommendation

**Discover Stories with Intelligence**

MAVILON AI Recommendation is a next-generation AI-powered cinematic discovery platform that helps users discover movies and anime based on mood, taste, genre, and story preference.

## 🎬 Features

- **AI-Powered Recommendations**: Intelligent content discovery using advanced semantic embeddings
- **Personalized Experience**: System learns your taste and adapts over time
- **AI Explanations**: Understand why each recommendation is suggested
- **Mood-Based Discovery**: Find content based on your current mood (Dark, Emotional, Thriller, Romance, Sci-Fi, Action, Comedy)
- **Cross-Domain Search**: Seamlessly discover both movies and anime
- **Natural Language Chat**: Ask AI in plain English (e.g., "dark psychological anime")
- **Watch History**: Track what you've watched and get better recommendations
- **Favorites**: Save content you love for easy access
- **Content Detail Pages**: Deep dive into movies and anime with trailers, cast, and similar content
- **Smart AI Search**: Natural language queries with intelligent filtering
- **3D Interactive Cards**: Premium UI with 3D hover effects and smooth animations
- **Cinematic Experience**: Dark theme with glassmorphism, neon accents, and particle effects
- **Production-Ready**: Caching, logging, metrics, and error handling

## 🚀 Tech Stack

### Frontend
- **Next.js 15** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Framer Motion** - Smooth animations
- **Three.js** - 3D particle effects
- **Lucide React** - Beautiful icons

### Backend
- **FastAPI** - High-performance Python API
- **Sentence Transformers** - AI-powered semantic embeddings
- **HTTPX** - Async HTTP client for API calls

### Data Sources
- **TMDB API** - Movie database
- **AniList API** - Anime database

## 📦 Installation

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+ and pip
- TMDB API key (free at https://www.themoviedb.org/settings/api)

### Frontend Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd Mavilon_AI_Recommendation
```

2. Install frontend dependencies:
```bash
npm install
```

3. Set up frontend environment variables:
```bash
cp .env.local.example .env.local
```

Edit `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend Setup

4. Navigate to backend directory:
```bash
cd backend
```

5. Create Python virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

6. Install backend dependencies:
```bash
pip install -r requirements.txt
```

7. Set up backend environment variables:
```bash
cp .env.example .env
```

Edit `backend/.env` and add your TMDB API key:
```env
TMDB_API_KEY=your_tmdb_api_key_here
BACKEND_PORT=8000
FRONTEND_URL=http://localhost:3000
```

### Running the Application

8. Start the backend server (in `backend/` directory):
```bash
source .venv/bin/activate  # If not already activated
uvicorn main:app --reload --port 8000
```

9. In a new terminal, start the frontend (from project root):
```bash
npm run dev
```

10. Open [http://localhost:3000](http://localhost:3000) in your browser

The backend API will be available at [http://localhost:8000](http://localhost:8000)

### Verifying Setup

11. Check backend health status:
```bash
curl http://localhost:8000/health
```

You should see a JSON response with `"status": "healthy"`. If `tmdb_configured` is `false`, the system will use OMDb fallback for movies.

## 🔧 Troubleshooting

### TMDB API Key Issues

**Problem**: Movie endpoints return "Movie data unavailable" or trending section shows limited content.

**Solution**: 
1. Verify your TMDB API key is set in `backend/.env`:
   ```bash
   cat backend/.env | grep TMDB_API_KEY
   ```
2. Make sure it's not the placeholder value `your_tmdb_api_key_here`
3. Get a free API key at https://www.themoviedb.org/settings/api
4. Restart the backend server after updating `.env`

### Backend Not Starting

**Problem**: Backend crashes on startup or shows import errors.

**Solution**:
1. Ensure virtual environment is activated:
   ```bash
   cd backend
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
2. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Check Python version (requires 3.9+):
   ```bash
   python --version
   ```

### Frontend Can't Connect to Backend

**Problem**: Frontend shows API errors or "Failed to load" messages.

**Solution**:
1. Verify backend is running on port 8000:
   ```bash
   curl http://localhost:8000/health
   ```
2. Check `NEXT_PUBLIC_API_URL` in `.env.local` is set to `http://localhost:8000`
3. Clear browser cache and reload

### No Trending Movies Showing

**Problem**: Anime shows but no movies in trending section.

**Solution**: This is expected if TMDB API key is not configured. The system will fall back to OMDb's popular movies list. For best experience, configure your TMDB API key.

### Database Errors

**Problem**: SQLite database errors or permission issues.

**Solution**:
1. Delete the database file and let it recreate:
   ```bash
   rm backend/mavilon_users.db
   ```
2. Restart the backend server - it will create a fresh database

## 🎨 Design Philosophy

MAVILON AI Recommendation is designed to feel:
- **Emotional** - Connect with stories on a deeper level
- **Cinematic** - Immersive visual experience
- **Magical** - Delightful interactions and animations
- **Intelligent** - AI-powered personalization
- **Premium** - High-quality, polished interface

## 🗺️ Development Roadmap

### Phase 1: Frontend Foundation ✅
- [x] Project setup with Next.js
- [x] Design system and theme
- [x] Animated background with particles
- [x] Core UI components
- [x] Home screen with hero section
- [x] Trending and recommended sections
- [x] 3D content cards

### Phase 2: Backend & AI Integration ✅
- [x] FastAPI backend setup
- [x] TMDB API integration
- [x] AniList API integration
- [x] AI recommendation engine with embeddings
- [x] Real-time content fetching
- [x] Search functionality
- [x] Mood-based recommendations
- [x] Cross-domain recommendations (movie ↔ anime)

### Phase 3: Personalization & User Intelligence ✅
- [x] User session management (lightweight identity)
- [x] SQLite database for interaction tracking
- [x] User taste profile generation with embeddings
- [x] Personalized recommendation engine
- [x] AI explanation system
- [x] Interaction tracking (clicks, views, searches)
- [x] Taste profile evolution over time

### Phase 4: Production Readiness & Content Depth ✅
- [x] Content detail pages with trailers
- [x] Watch history tracking
- [x] Favorites management
- [x] AI chat assistant for natural language discovery
- [x] In-memory caching for performance
- [x] Structured logging (JSON for production)
- [x] Request ID tracking and metrics
- [x] Global error handling
- [x] Production-ready deployment configuration

### Phase 5: Future Enhancements
- [ ] User authentication (OAuth, email/password)
- [ ] Social features (sharing, reviews)
- [ ] Advanced filters and sorting
- [ ] Multi-language support
- [ ] Mobile app (React Native)
- [ ] Recommendation explanations with visualizations
- [ ] Content ratings and reviews

## 🎯 Key Features (Detailed)

### Mood-Based Discovery
Select your current mood and get personalized recommendations:
- 🌑 Dark - Intense, gritty stories
- 💔 Emotional - Touching, heartfelt narratives
- 😱 Thriller - Edge-of-your-seat suspense
- 💕 Romance - Love stories and relationships
- 🚀 Sci-Fi - Futuristic and speculative fiction
- 💥 Action - High-octane adventures
- 😂 Comedy - Light-hearted entertainment

### Smart Search
Ask AI in natural language:
- "Recommend dark psychological anime"
- "Find sci-fi movies like Interstellar"
- "Show me emotional romance with happy ending"

### 3D Interactive Cards
- Hover to see 3D tilt effect
- Glow animations
- Floating action buttons
- Smooth transitions

## 📄 License

This project is proprietary and confidential.

## 🤝 Contributing

This is a private project. Contributions are not currently accepted.

---

**Built with ❤️ for cinematic storytelling**
