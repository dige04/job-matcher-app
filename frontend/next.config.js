/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Enable standalone output for containerization
  output: 'standalone',
  // If your app uses absolute imports like "@/components", set baseUrl in tsconfig and a path mapping.
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
};

module.exports = nextConfig;
