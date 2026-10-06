# Railway Deployment Guide

## Overview

Railway is a modern cloud platform that automatically deploys Docker applications. This guide walks through deploying the TMS Adapter to Railway.

## Prerequisites

1. Railway account (create at https://railway.app)
2. GitHub account with this repository
3. GitHub personal access token (optional, for CLI)

## Setup Steps

### Step 1: Connect GitHub to Railway

1. Go to https://railway.app
2. Click **New Project**
3. Select **Deploy from GitHub**
4. Authorize GitHub and select `tms-adapter` repository
5. Railway auto-detects `Dockerfile` and deploys

### Step 2: Set Environment Variables

In Railway Dashboard:

1. Go to **Project Settings**
2. Click **Variables**
3. Add these variables:

```
TMS_HOST=tramway.proxy.rlwy.net
TMS_PORT=17159
TMS_TOKEN=[from GitHub secrets]
FMCSA_WEB_KEY=[from GitHub secrets]
```

### Step 3: Add GitHub Secrets

For automated deployment, add to GitHub repository settings:

```
RAILWAY_TOKEN        → Railway API token
TMS_TOKEN            → Your TMS token
FMCSA_WEB_KEY        → Your FMCSA key
TMS_HOST             → tramway.proxy.rlwy.net
TMS_PORT             → 17159
```

Get `RAILWAY_TOKEN` from Railway Dashboard → Account Settings → Tokens

### Step 4: Automatic Deployment

Once connected, Railway automatically:
- Watches your `main` branch
- Builds Docker image on every push
- Runs tests
- Deploys on success
- Rolls back on failure

## Manual Deployment

### Using Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link project
railway link

# Deploy
railway up

# View logs
railway logs
```

### Using Docker

```bash
# Build locally
docker build -t tms-adapter:latest .

# Push to Railway
docker tag tms-adapter:latest railway.app/tms-adapter:latest
docker push railway.app/tms-adapter:latest
```

## Deployment File

`railway.json` configures Railway:
- Uses `Dockerfile` for build
- 1 replica by default
- Auto-restart policy
- Always-on deployment

## Accessing Your Service

After deployment:

1. **Get public URL:**
   - Railway Dashboard → Services → tms-adapter → Environment
   - Copy the `RAILWAY_PUBLIC_URL`

2. **Access service:**
   ```bash
   curl https://[your-railway-url].railway.app/
   ```

3. **View logs:**
   - Railway Dashboard → Services → tms-adapter → Logs

## Testing Deployment

### Check health
```bash
curl https://[your-railway-url].railway.app/
# Should return: TMS Adapter ready for use
```

### Run remote tests
```bash
# SSH into container
railway exec bash

# Run tests
pytest tests/ -v
```

## Scaling

### Horizontal Scaling (Multiple Replicas)

In Railway Dashboard:
1. Services → tms-adapter → Settings
2. Change "Replicas" to desired number
3. Railway auto-distributes traffic

### Vertical Scaling (More CPU/Memory)

In Railway Dashboard:
1. Services → tms-adapter → Settings
2. Select compute tier
3. Restart service

## Monitoring

### View Logs
```bash
railway logs --service tms-adapter --follow
```

### Monitor Resources
Railway Dashboard shows:
- CPU usage
- Memory usage
- Network I/O
- Uptime

### Alerts
Set up in Railway Dashboard:
- Deployment failures
- High CPU/Memory
- Service down

## Updating Code

### Auto-Deploy
```bash
git push origin main  # Triggers automatic deployment
```

### Manual Redeploy
Railway Dashboard → Services → tms-adapter → Redeploy

## Environment Management

### Production Environment
Railway creates `production` environment by default.

### Staging Environment
1. Railway Dashboard → New Environment
2. Name it "staging"
3. Set different variables if needed

### Switch Environments
```bash
railway env [production|staging]
railway up
```

## Troubleshooting

### Deployment Failed
```bash
# Check logs
railway logs

# Check Railway status
# Visit status.railway.app
```

### Service Not Starting
```bash
# Verify environment variables
railway variables

# Check Docker logs
railway logs --raw
```

### Connection Issues
```bash
# Verify TMS connectivity
railway exec curl tramway.proxy.rlwy.net:17159

# Check environment
railway exec env | grep TMS
```

### High Resource Usage
1. Check logs for memory leaks
2. Scale down replicas
3. Optimize code or container

## Cost Estimation

Railway pricing:
- **Free tier:** Limited hours/month
- **Hobby plan:** ~$5/month
- **Pro plan:** ~$20/month (recommended)

Cost depends on:
- CPU usage (hours × cores)
- Memory usage (hours × GB)
- Network bandwidth
- Disk storage

## Security

### Secrets Management
- Store secrets in GitHub (not in code)
- Railway auto-encrypts environment variables
- Never commit `.env` file

### Network Security
- Railway provides HTTPS by default
- Use VPC (Pro plan+) for private networking
- Whitelist IP if needed

### Logging
- Logs stored for 7 days (free) / 30 days (pro)
- Don't log sensitive data
- Use structured logging for debugging

## Backing Up & Recovery

### Database Backups (if added)
1. Railway Dashboard → Add Service → Database
2. Select PostgreSQL/MongoDB/MySQL
3. Auto-backups enabled by default

### Service Backup
```bash
# Backup code
git clone https://github.com/Yogavarshni4699/tms-adapter.git
```

### Restore from Backup
Railway auto-restores from latest working deployment.

## Custom Domain

### Add Custom Domain
1. Railway Dashboard → Services → tms-adapter → Settings
2. Click "Add custom domain"
3. Point your DNS to Railway-provided address

### Example
```
Your domain: tms-adapter.yourdomain.com
Points to:   [railway-provided-url].railway.app
```

## Links

- Railway Docs: https://docs.railway.app
- Railway Status: https://status.railway.app
- CLI Docs: https://docs.railway.app/reference/cli
- GitHub Actions: .github/workflows/deploy-railway.yml

## Next Steps

1. ✅ Create Railway account
2. ✅ Connect GitHub repository
3. ✅ Set environment variables
4. ✅ Trigger deployment
5. ✅ Get public URL
6. ✅ Integrate with HappyRobot

For support: https://railway.app/support
