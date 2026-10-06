# Railway Quick Start (5 Minutes)

## 1. Create Railway Account
Visit https://railway.app and sign up with GitHub

## 2. Create New Project
- Click **New Project**
- Select **Deploy from GitHub**
- Authorize and select `tms-adapter` repo

## 3. Set Secrets in GitHub
Go to repo Settings → Secrets → New repository secret

Add these 2 secrets:
```
RAILWAY_TOKEN        (get from Railway Dashboard → Account → Tokens)
TMS_TOKEN            (your TMS token)
FMCSA_WEB_KEY        (your FMCSA key)
```

## 4. Set Variables in Railway
Railway Dashboard → Project → Variables

Add these:
```
TMS_HOST=tramway.proxy.rlwy.net
TMS_PORT=17159
TMS_TOKEN=${{ TMS_TOKEN }}          (references GitHub secret)
FMCSA_WEB_KEY=${{ FMCSA_WEB_KEY }}  (references GitHub secret)
```

## 5. Deploy
Push to main branch:
```bash
git push origin main
```

GitHub Actions automatically:
- ✅ Runs tests
- ✅ Builds Docker image
- ✅ Deploys to Railway
- ✅ Shows logs

## 6. Get Your URL
Railway Dashboard → Services → tms-adapter → Environment

Copy the `RAILWAY_PUBLIC_URL` - that's your service URL!

## 7. Test It
```bash
curl https://[your-railway-url].railway.app/
```

Should show: `TMS Adapter ready for use`

## 8. View Logs
```bash
# Using Railway CLI
railway logs --follow

# Or in Dashboard: Services → tms-adapter → Logs
```

## That's It! 🎉

Your TMS Adapter is now live on Railway!

### Next Steps
- Integrate with HappyRobot workflow
- Use `RAILWAY_PUBLIC_URL` as `TMS_ADAPTER_BASE_URL`
- Build HTTP wrapper for `/loads/search`, `/loads/{id}`, `/loads/{id}/book` endpoints

### Useful Commands
```bash
# Install Railway CLI
npm install -g @railway/cli

# View logs
railway logs --follow

# Shell into container
railway exec bash

# Check environment
railway variables

# Restart service
railway restart
```

### Links
- Your Railway Project: https://railway.app/dashboard
- Docs: https://docs.railway.app
- Support: https://railway.app/support
