/** @type {import('next').NextConfig} */
const nextConfig = {
    images: {
        remotePatterns: [
            {
                protocol: 'https',
                hostname: 'image.tmdb.org',
                pathname: '/t/p/**',
            },
            {
                protocol: 'https',
                hostname: 's4.anilist.co',
                pathname: '/file/**',
            },
            {
                protocol: 'https',
                hostname: 'm.media-amazon.com',
                pathname: '/**',
            },
            {
                protocol: 'https',
                hostname: 'ia.media-imdb.com',
                pathname: '/**',
            },
        ],
    },
}

module.exports = nextConfig
