/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Expose only public env vars to the browser
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_APP_NAME: process.env.NEXT_PUBLIC_APP_NAME,
  },
};

module.exports = nextConfig;
