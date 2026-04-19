/** @type {import('next').NextConfig} */
const nextConfig = {
  // Ensure NEXT_PUBLIC_API_URL is available at build time.
  // Set this env var in the Render dashboard before building.
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL ?? '',
  },
};

export default nextConfig;
