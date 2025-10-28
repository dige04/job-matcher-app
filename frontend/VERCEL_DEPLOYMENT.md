# Vercel Deployment Guide

This guide explains how to deploy the Job Matcher frontend to Vercel using the provided configuration.

## Prerequisites

1. A Vercel account (sign up at [vercel.com](https://vercel.com))
2. A GitHub, GitLab, or Bitbucket account connected to Vercel
3. The frontend code pushed to a repository

## Environment Variables

The frontend requires one environment variable to connect to the backend API:

- `NEXT_PUBLIC_API_URL`: The URL of your backend API service

### Setting up Environment Variables in Vercel

1. In your Vercel project dashboard, go to **Settings** > **Environment Variables**
2. Add the following environment variable:
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: The URL of your deployed backend API (e.g., `https://your-backend-api.vercel.app`)
   - Environments: Select Production, Preview, and Development as needed
3. Redeploy your application to apply the new environment variable

## Deployment Options

### Option 1: Through Vercel Dashboard (Recommended)

1. Log in to your Vercel dashboard
2. Click **Add New...** > **Project**
3. Import your Git repository
4. Vercel will automatically detect that it's a Next.js project
5. Configure the project:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend` (if deploying from monorepo)
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
   - **Install Command**: `npm install`
6. Add environment variables as described above
7. Click **Deploy**

### Option 2: Using Vercel CLI

1. Install the Vercel CLI:
   ```bash
   npm i -g vercel
   ```

2. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

3. Run the deployment command:
   ```bash
   vercel --prod
   ```

4. Follow the prompts to configure your project

### Option 3: From Monorepo Root

If deploying from the root of the monorepo:

1. Create a `vercel.json` file in the root directory:
   ```json
   {
     "version": 2,
     "builds": [
       {
         "src": "frontend/package.json",
         "use": "@vercel/next"
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "/frontend/$1"
       }
     ]
   }
   ```

2. Deploy with:
   ```bash
   vercel --prod
   ```

## Configuration Details

The `vercel.json` file includes:

- **Build Configuration**: Optimized for Next.js with standalone output
- **Region**: Set to Singapore (sin1) for better performance in Asia
- **Rewrites**: API routes are proxied to the backend service
- **Headers**: Security headers for enhanced protection
- **Functions**: Node.js 18.x runtime for API routes

## Custom Domains

To add a custom domain:

1. In your Vercel project dashboard, go to **Settings** > **Domains**
2. Add your domain name
3. Configure DNS records as instructed by Vercel
4. Wait for SSL certificate provisioning

## Performance Optimization

The configuration includes:

- **Static Generation**: Pages are pre-rendered at build time when possible
- **Image Optimization**: Next.js Image component is used for optimized images
- **Code Splitting**: Automatic code splitting for optimal loading
- **Caching**: API responses are cached for 24 hours

## Monitoring and Debugging

- **Logs**: Access deployment logs in the Vercel dashboard
- **Analytics**: Built-in analytics for performance monitoring
- **Error Tracking**: Integration with error tracking services

## Troubleshooting

### Build Errors

1. Check that all dependencies are in `package.json`
2. Verify environment variables are correctly set
3. Review build logs in the Vercel dashboard

### Runtime Errors

1. Check that `NEXT_PUBLIC_API_URL` is accessible
2. Verify the backend API is deployed and accessible
3. Check browser console for any client-side errors

### Performance Issues

1. Enable Vercel Analytics for performance insights
2. Check Core Web Vitals in the Vercel dashboard
3. Optimize images and large assets

## Rollback

If you need to rollback to a previous deployment:

1. Go to the **Deployments** tab in your Vercel dashboard
2. Find the previous successful deployment
3. Click the three-dot menu and select **Promote to Production**

## Next Steps

1. Set up a custom domain
2. Configure analytics and monitoring
3. Set up preview deployments for pull requests
4. Configure team members and access controls