# Deployment Configuration

This document explains how to configure the frontend for deployment to Vercel.

## Environment Variables

The frontend requires one environment variable to connect to the backend API:

- `NEXT_PUBLIC_API_URL`: The URL of your backend API service

### Local Development

1. Copy the example environment file:
   ```bash
   cp .env.local.example .env.local
   ```

2. Update the `NEXT_PUBLIC_API_URL` in `.env.local` to point to your local backend:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

### Vercel Deployment

1. In your Vercel project dashboard, go to Settings > Environment Variables

2. Add the following environment variable:
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: The URL of your deployed backend API (e.g., `https://your-backend-api.vercel.app`)

3. Redeploy your application to apply the new environment variable

## Dependencies

The project requires the following additional dependencies that have been added:
- `axios`: For making HTTP requests to the backend API
- `@types/node`: For TypeScript support of Node.js types

## Notes

- The `NEXT_PUBLIC_` prefix is required for Next.js to expose the variable to the browser
- The frontend is now configured to work with any backend URL by simply changing the environment variable
- No code changes are required when deploying to different environments