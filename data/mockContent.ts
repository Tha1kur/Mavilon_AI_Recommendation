import { Movie, Anime, Content } from '@/types/content';

// Mock movie data
export const mockMovies: Movie[] = [
    {
        id: 'm1',
        type: 'movie',
        title: 'Inception',
        posterUrl: 'https://image.tmdb.org/t/p/w500/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg',
        backdropUrl: 'https://image.tmdb.org/t/p/original/s3TBrRGB1iav7gFOCNx3H31MoES.jpg',
        genres: ['Sci-Fi', 'Thriller', 'Action'],
        rating: 8.8,
        year: 2010,
        duration: 148,
        overview: 'A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.',
        cast: ['Leonardo DiCaprio', 'Joseph Gordon-Levitt', 'Ellen Page'],
        director: 'Christopher Nolan',
        mood: ['Dark', 'Thriller', 'Sci-Fi'],
    },
    {
        id: 'm2',
        type: 'movie',
        title: 'Interstellar',
        posterUrl: 'https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg',
        backdropUrl: 'https://image.tmdb.org/t/p/original/pbrkL804c8yAv3zBZR4QPEafpAR.jpg',
        genres: ['Sci-Fi', 'Drama', 'Adventure'],
        rating: 8.6,
        year: 2014,
        duration: 169,
        overview: 'A team of explorers travel through a wormhole in space in an attempt to ensure humanity\'s survival.',
        cast: ['Matthew McConaughey', 'Anne Hathaway', 'Jessica Chastain'],
        director: 'Christopher Nolan',
        mood: ['Emotional', 'Sci-Fi'],
    },
    {
        id: 'm3',
        type: 'movie',
        title: 'The Dark Knight',
        posterUrl: 'https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg',
        backdropUrl: 'https://image.tmdb.org/t/p/original/hkBaDkMWbLaf8B1lsWsKX7Ew3Xq.jpg',
        genres: ['Action', 'Crime', 'Drama'],
        rating: 9.0,
        year: 2008,
        duration: 152,
        overview: 'When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests.',
        cast: ['Christian Bale', 'Heath Ledger', 'Aaron Eckhart'],
        director: 'Christopher Nolan',
        mood: ['Dark', 'Thriller', 'Action'],
    },
    {
        id: 'm4',
        type: 'movie',
        title: 'Blade Runner 2049',
        posterUrl: 'https://image.tmdb.org/t/p/w500/gajva2L0rPYkEWjzgFlBXCAVBE5.jpg',
        backdropUrl: 'https://image.tmdb.org/t/p/original/ilKE2RPpYJNiDkAGRH8FS3TM7W4.jpg',
        genres: ['Sci-Fi', 'Thriller', 'Mystery'],
        rating: 8.0,
        year: 2017,
        duration: 164,
        overview: 'A young blade runner\'s discovery of a long-buried secret leads him to track down former blade runner Rick Deckard.',
        cast: ['Ryan Gosling', 'Harrison Ford', 'Ana de Armas'],
        director: 'Denis Villeneuve',
        mood: ['Dark', 'Sci-Fi', 'Mystery'],
    },
    {
        id: 'm5',
        type: 'movie',
        title: 'La La Land',
        posterUrl: 'https://image.tmdb.org/t/p/w500/uDO8zWDhfWwoFdKS4fzkUJt0Rf0.jpg',
        backdropUrl: 'https://image.tmdb.org/t/p/original/fp6X1jcPYNx0Dqn6vxsP7KT1CWa.jpg',
        genres: ['Romance', 'Drama', 'Comedy'],
        rating: 8.0,
        year: 2016,
        duration: 128,
        overview: 'While navigating their careers in Los Angeles, a pianist and an actress fall in love while attempting to reconcile their aspirations for the future.',
        cast: ['Ryan Gosling', 'Emma Stone', 'John Legend'],
        director: 'Damien Chazelle',
        mood: ['Emotional', 'Romance'],
    },
];

// Mock anime data
export const mockAnime: Anime[] = [
    {
        id: 'a1',
        type: 'anime',
        title: 'Death Note',
        posterUrl: 'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx1535-lawCwhzhi96X.jpg',
        backdropUrl: 'https://s4.anilist.co/file/anilistcdn/media/anime/banner/1535.jpg',
        genres: ['Mystery', 'Psychological', 'Thriller'],
        rating: 8.6,
        year: 2006,
        episodes: 37,
        overview: 'A high school student discovers a supernatural notebook that allows him to kill anyone by writing their name, leading to a cat-and-mouse game with a detective.',
        characters: ['Light Yagami', 'L Lawliet', 'Ryuk'],
        studio: 'Madhouse',
        mood: ['Dark', 'Thriller', 'Mystery'],
    },
    {
        id: 'a2',
        type: 'anime',
        title: 'Steins;Gate',
        posterUrl: 'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx9253-7pdcVzQSkKxT.jpg',
        backdropUrl: 'https://s4.anilist.co/file/anilistcdn/media/anime/banner/9253.jpg',
        genres: ['Sci-Fi', 'Thriller', 'Drama'],
        rating: 9.1,
        year: 2011,
        episodes: 24,
        overview: 'A group of friends discover a way to send messages to the past, but their experiments have unforeseen consequences that threaten the fabric of reality.',
        characters: ['Okabe Rintarou', 'Makise Kurisu', 'Mayuri Shiina'],
        studio: 'White Fox',
        mood: ['Sci-Fi', 'Thriller', 'Emotional'],
    },
    {
        id: 'a3',
        type: 'anime',
        title: 'Attack on Titan',
        posterUrl: 'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx16498-73IhOXpJZiMF.jpg',
        backdropUrl: 'https://s4.anilist.co/file/anilistcdn/media/anime/banner/16498-8jpFCOcDmneX.jpg',
        genres: ['Action', 'Drama', 'Fantasy'],
        rating: 8.5,
        year: 2013,
        episodes: 75,
        overview: 'Humanity lives within cities surrounded by enormous walls as a defense against gigantic humanoid Titans that devour humans seemingly without reason.',
        characters: ['Eren Yeager', 'Mikasa Ackerman', 'Armin Arlert'],
        studio: 'Wit Studio',
        mood: ['Dark', 'Action', 'Thriller'],
    },
    {
        id: 'a4',
        type: 'anime',
        title: 'Your Name',
        posterUrl: 'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx21519-fPhvy69vnQqS.png',
        backdropUrl: 'https://s4.anilist.co/file/anilistcdn/media/anime/banner/21519-VI5cEOwnGONE.jpg',
        genres: ['Romance', 'Drama', 'Fantasy'],
        rating: 8.4,
        year: 2016,
        episodes: 1,
        overview: 'Two strangers find themselves linked in a bizarre way. When a connection forms, will distance be the only thing to keep them apart?',
        characters: ['Tachibana Taki', 'Miyamizu Mitsuha'],
        studio: 'CoMix Wave Films',
        mood: ['Emotional', 'Romance', 'Fantasy'],
    },
    {
        id: 'a5',
        type: 'anime',
        title: 'Cowboy Bebop',
        posterUrl: 'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx1-CXtrrkMpJ8Zq.png',
        backdropUrl: 'https://s4.anilist.co/file/anilistcdn/media/anime/banner/1.jpg',
        genres: ['Action', 'Sci-Fi', 'Adventure'],
        rating: 8.8,
        year: 1998,
        episodes: 26,
        overview: 'The futuristic misadventures and tragedies of an easygoing bounty hunter and his partners.',
        characters: ['Spike Spiegel', 'Jet Black', 'Faye Valentine'],
        studio: 'Sunrise',
        mood: ['Action', 'Sci-Fi', 'Emotional'],
    },
    {
        id: 'a6',
        type: 'anime',
        title: 'Psycho-Pass',
        posterUrl: 'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx13601-i42VFuHpqEOJ.jpg',
        backdropUrl: 'https://s4.anilist.co/file/anilistcdn/media/anime/banner/13601.jpg',
        genres: ['Sci-Fi', 'Psychological', 'Thriller'],
        rating: 8.3,
        year: 2012,
        episodes: 22,
        overview: 'In a futuristic world where criminal intent is analyzed by the Sibyl System, a young inspector questions the nature of justice.',
        characters: ['Tsunemori Akane', 'Kougami Shinya', 'Makishima Shougo'],
        studio: 'Production I.G',
        mood: ['Dark', 'Sci-Fi', 'Thriller'],
    },
];

// Combined content
export const mockContent: Content[] = [...mockMovies, ...mockAnime];

// Trending content (mix of movies and anime)
export const trendingContent: Content[] = [
    mockMovies[0], // Inception
    mockAnime[0],  // Death Note
    mockMovies[2], // The Dark Knight
    mockAnime[1],  // Steins;Gate
    mockMovies[3], // Blade Runner 2049
    mockAnime[2],  // Attack on Titan
];

// Recommended content
export const recommendedContent: Content[] = [
    mockMovies[1], // Interstellar
    mockAnime[3],  // Your Name
    mockMovies[4], // La La Land
    mockAnime[4],  // Cowboy Bebop
    mockAnime[5],  // Psycho-Pass
    mockMovies[0], // Inception
];
