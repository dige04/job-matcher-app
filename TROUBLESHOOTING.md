# Deployment Troubleshooting Guide

This guide provides solutions to common issues that may occur during deployment of the Job Matcher application.

## Table of Contents

1. [Frontend Issues](#frontend-issues)
2. [Backend Issues](#backend-issues)
3. [Container Issues](#container-issues)
4. [Platform-Specific Issues](#platform-specific-issues)
5. [Network and Connectivity Issues](#network-and-connectivity-issues)
6. [Performance Issues](#performance-issues)
7. [Debugging Tools and Techniques](#debugging-tools-and-techniques)

## Frontend Issues

### Build Errors

#### Issue: TypeScript compilation errors
**Symptoms:**
- Build fails with TypeScript errors
- Type errors in the console

**Solutions:**
1. Check TypeScript configuration in `tsconfig.json`
2. Ensure all types are properly imported
3. Run `npm run build` locally to reproduce the error
4. Fix type errors in the code

```bash
# Check TypeScript version
npm list typescript

# Run TypeScript compiler directly
npx tsc --noEmit
```

#### Issue: Module not found errors
**Symptoms:**
- Build fails with "Module not found" errors
- Missing dependencies

**Solutions:**
1. Check that all dependencies are in `package.json`
2. Run `npm install` to ensure all dependencies are installed
3. Verify import paths are correct
4. Check for case sensitivity in import paths

```bash
# Clean install
rm -rf node_modules package-lock.json
npm install

# Check for missing dependencies
npm ls
```

#### Issue: ESLint errors preventing build
**Symptoms:**
- Build fails due to ESLint errors
- Linting warnings in the console

**Solutions:**
1. Fix ESLint errors in the code
2. Temporarily disable strict linting in `next.config.js`
3. Configure ESLint rules appropriately

```javascript
// In next.config.js
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true, // Only for temporary use
  },
};
```

### Runtime Errors

#### Issue: API connection errors
**Symptoms:**
- Frontend cannot connect to backend API
- CORS errors in browser console
- Network errors in API calls

**Solutions:**
1. Verify `NEXT_PUBLIC_API_URL` is correctly set
2. Check that the backend is running and accessible
3. Verify CORS configuration on the backend
4. Check network connectivity between services

```bash
# Test API connectivity
curl -I https://your-backend-api.com/health

# Check CORS headers
curl -H "Origin: https://your-frontend-domain.com" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS \
     https://your-backend-api.com/some-endpoint
```

#### Issue: Environment variables not loading
**Symptoms:**
- `process.env` variables are undefined
- Configuration values are missing

**Solutions:**
1. Ensure variables have `NEXT_PUBLIC_` prefix
2. Check that `.env.local` exists and is properly formatted
3. Restart the development server after changes
4. Verify variables are set in the deployment platform

```javascript
// Debug environment variables in the browser
console.log('API URL:', process.env.NEXT_PUBLIC_API_URL);
console.log('All env vars:', process.env);
```

#### Issue: Page not found errors
**Symptoms:**
- 404 errors on certain routes
- Navigation not working

**Solutions:**
1. Check file structure in `app/` directory
2. Verify route names match file/folder names
3. Ensure dynamic routes are properly configured
4. Check for trailing slashes in URLs

### Performance Issues

#### Issue: Slow page load times
**Symptoms:**
- Pages take a long time to load
- Large bundle sizes

**Solutions:**
1. Optimize images and assets
2. Implement code splitting
3. Use Next.js Image component for images
4. Enable static generation where possible

```bash
# Analyze bundle size
npm run build
npx @next/bundle-analyzer

# Check for large dependencies
npm ls --depth=0 | grep -E '[0-9]+\.[0-9]+\.[0-9]+.*MB'
```

## Backend Issues

### Startup Issues

#### Issue: Model loading failures
**Symptoms:**
- Application fails to start
- Model loading errors in logs
- FileNotFoundError for model files

**Solutions:**
1. Verify model artifacts are in the correct directory
2. Check that `ARTIFACT_DIR` is correctly set
3. Ensure model URLs are accessible (if using cloud storage)
4. Verify file permissions on model files

```python
# Debug model loading
import os
print(f"ARTIFACT_DIR: {os.getenv('ARTIFACT_DIR')}")
print(f"Files in artifacts: {os.listdir(os.getenv('ARTIFACT_DIR'))}")
```

#### Issue: Port binding errors
**Symptoms:**
- Application fails to start with port errors
- "Address already in use" errors

**Solutions:**
1. Check if the port is already in use
2. Verify `API_PORT` environment variable
3. Ensure the port is exposed in the Dockerfile
4. Check firewall settings

```bash
# Check port usage
netstat -tulpn | grep :8000
lsof -i :8000

# Kill process using the port
sudo kill -9 <PID>
```

#### Issue: Environment variable errors
**Symptoms:**
- Application fails to start
- Missing or invalid environment variables

**Solutions:**
1. Verify `.env` file exists and is properly formatted
2. Check that all required variables are set
3. Validate variable values
4. Ensure variables are correctly passed to the container

```python
# Debug environment variables
import os
required_vars = ['ARTIFACT_DIR', 'ALLOWED_ORIGINS']
for var in required_vars:
    value = os.getenv(var)
    if value is None:
        print(f"Missing required variable: {var}")
    else:
        print(f"{var}: {value}")
```

### Runtime Issues

#### Issue: API endpoint errors
**Symptoms:**
- API endpoints return 500 errors
- Unexpected responses from API

**Solutions:**
1. Check application logs for error details
2. Verify request format and headers
3. Check that required parameters are provided
4. Validate input data

```bash
# Test API endpoints
curl -X POST https://your-api.com/endpoint \
     -H "Content-Type: application/json" \
     -d '{"key": "value"}' \
     -v
```

#### Issue: CORS errors
**Symptoms:**
- Browser console shows CORS errors
- Requests blocked by CORS policy

**Solutions:**
1. Verify `ALLOWED_ORIGINS` includes the frontend domain
2. Check that preflight requests are handled
3. Ensure appropriate headers are returned
4. Verify the frontend URL is correctly configured

```python
# Debug CORS configuration
from fastapi.middleware.cors import CORSMiddleware

# Log CORS configuration
print(f"Allowed origins: {app.middleware_stack.middleware[0].allow_origins}")
print(f"Allowed methods: {app.middleware_stack.middleware[0].allow_methods}")
```

#### Issue: Memory errors
**Symptoms:**
- Application crashes with out-of-memory errors
- Slow performance due to memory pressure

**Solutions:**
1. Increase container memory limits
2. Optimize model loading and inference
3. Implement memory cleanup
4. Monitor memory usage

```python
# Monitor memory usage
import psutil
import os

process = psutil.Process(os.getpid())
print(f"Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB")
```

## Container Issues

### Build Issues

#### Issue: Docker build failures
**Symptoms:**
- Docker build fails with errors
- Layer caching issues

**Solutions:**
1. Check Dockerfile syntax
2. Verify all required files are included
3. Clear Docker cache if needed
4. Check base image availability

```bash
# Clear Docker cache
docker system prune -a

# Build with no cache
docker build --no-cache -t image-name .
```

#### Issue: Large image sizes
**Symptoms:**
- Docker images are too large
- Slow deployment times

**Solutions:**
1. Use multi-stage builds
2. Optimize Dockerfile layers
3. Remove unnecessary dependencies
4. Use .dockerignore to exclude files

```dockerfile
# Example of optimized Dockerfile
FROM python:3.9-slim as base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM base as runtime
COPY . .
CMD ["python", "app.py"]
```

### Runtime Issues

#### Issue: Container fails to start
**Symptoms:**
- Container exits immediately
- Health check failures

**Solutions:**
1. Check container logs for errors
2. Verify entrypoint and command
3. Check that required ports are exposed
4. Ensure environment variables are set

```bash
# Check container logs
docker logs container-name

# Run container interactively for debugging
docker run -it --entrypoint /bin/bash image-name
```

#### Issue: Permission errors
**Symptoms:**
- Permission denied errors
- File access issues

**Solutions:**
1. Check file permissions in the container
2. Verify user configuration
3. Ensure volumes are correctly mounted
4. Check that the application runs as the correct user

```bash
# Check file permissions in container
docker run --rm -it image-name ls -la /app/backend/artifacts

# Run as specific user
docker run --user 1000:1000 image-name
```

## Platform-Specific Issues

### Vercel Issues

#### Issue: Build timeouts
**Symptoms:**
- Vercel build times out
- Deployment fails during build

**Solutions:**
1. Optimize build process
2. Reduce bundle size
3. Use Vercel's build caching
4. Consider upgrading to a paid plan

#### Issue: Environment variables not working
**Symptoms:**
- Environment variables not loaded
- Configuration issues

**Solutions:**
1. Verify variables are set in Vercel dashboard
2. Check variable names and values
3. Redeploy after changing variables
4. Ensure variables have correct scope

### AWS ECS Issues

#### Issue: Task fails to start
**Symptoms:**
- ECS tasks fail to start
- Container exit errors

**Solutions:**
1. Check task definition configuration
2. Verify IAM roles and permissions
3. Check resource allocation (CPU, memory)
4. Review CloudWatch logs

```bash
# Check ECS task status
aws ecs describe-tasks --cluster cluster-name --tasks task-id

# View CloudWatch logs
aws logs tail /ecs/service-name --follow
```

#### Issue: Load balancer issues
**Symptoms:**
- Load balancer health checks failing
- Traffic not routing correctly

**Solutions:**
1. Verify health check configuration
2. Check target group settings
3. Ensure security groups allow traffic
4. Verify listener rules

### Google Cloud Run Issues

#### Issue: Service not responding
**Symptoms:**
- Cloud Run service returns errors
- Cold start issues

**Solutions:**
1. Check service configuration
2. Verify resource allocation
3. Review Cloud Run logs
4. Optimize startup time

```bash
# Check Cloud Run service status
gcloud run services describe service-name --region region

# View logs
gcloud logs read "resource.type=cloud_run_revision" --limit 50
```

### Railway Issues

#### Issue: Build failures
**Symptoms:**
- Railway build fails
- Deployment errors

**Solutions:**
1. Check build logs in Railway dashboard
2. Verify nixpacks configuration
3. Ensure all dependencies are specified
4. Check for platform-specific issues

## Network and Connectivity Issues

### DNS Issues

#### Issue: Domain not resolving
**Symptoms:**
- Domain name not resolving
- DNS propagation delays

**Solutions:**
1. Check DNS configuration
2. Verify domain registration
3. Use DNS lookup tools to debug
4. Wait for DNS propagation

```bash
# Check DNS resolution
nslookup your-domain.com
dig your-domain.com

# Check propagation
whois your-domain.com
```

### SSL/TLS Issues

#### Issue: Certificate errors
**Symptoms:**
- SSL certificate errors
- HTTPS not working

**Solutions:**
1. Verify certificate configuration
2. Check certificate validity
3. Ensure proper domain configuration
4. Use certificate debugging tools

```bash
# Check SSL certificate
openssl s_client -connect your-domain.com:443

# Check certificate details
curl -vI https://your-domain.com
```

## Performance Issues

### Frontend Performance

#### Issue: Slow page loads
**Symptoms:**
- Pages load slowly
- Poor Core Web Vitals

**Solutions:**
1. Optimize images and assets
2. Implement lazy loading
3. Use CDN for static assets
4. Enable compression

```bash
# Analyze performance with Lighthouse
npx lighthouse https://your-domain.com --output html --output-path ./lighthouse-report.html
```

### Backend Performance

#### Issue: Slow API responses
**Symptoms:**
- API endpoints respond slowly
- High response times

**Solutions:**
1. Optimize database queries
2. Implement caching
3. Use connection pooling
4. Profile the application

```python
# Profile Python code
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your code here

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

## Debugging Tools and Techniques

### Logging

#### Frontend Logging
```javascript
// Add logging to your application
console.log('Debug info:', data);
console.error('Error:', error);

// Use a logging library
import winston from 'winston';
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.Console(),
  ],
});
```

#### Backend Logging
```python
# Configure logging
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info('Application started')
```

### Monitoring

#### Frontend Monitoring
- Use Vercel Analytics for performance insights
- Implement error tracking with Sentry
- Use browser developer tools for debugging

#### Backend Monitoring
- Use platform monitoring tools (CloudWatch, Cloud Monitoring)
- Implement application performance monitoring (APM)
- Set up alerts for critical metrics

### Debugging Commands

#### Frontend
```bash
# Check build output
npm run build

# Run tests
npm test

# Check dependencies
npm ls

# Analyze bundle
npx @next/bundle-analyzer
```

#### Backend
```bash
# Run application locally
python app.py

# Run tests
python -m pytest

# Check dependencies
pip freeze

# Run with debugger
python -m pdb app.py
```

#### Container
```bash
# Build image
docker build -t image-name .

# Run container
docker run -p 8000:8000 image-name

# Check logs
docker logs container-name

# Debug in container
docker run -it --entrypoint /bin/bash image-name
```

## Getting Help

If you're still experiencing issues after trying these solutions:

1. Check the platform-specific documentation
2. Review application logs for detailed error messages
3. Search for similar issues in community forums
4. Create a minimal reproduction case
5. Contact support for your deployment platform

For additional help with the Job Matcher application, refer to the [Deployment Guide](DEPLOYMENT_GUIDE.md) and [Environment Variables Documentation](ENVIRONMENT_VARIABLES.md).