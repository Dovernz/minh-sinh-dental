/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*', // Chuyển tiếp các request /api sang Django backend
      },
    ]
  },
}

module.exports = nextConfig
