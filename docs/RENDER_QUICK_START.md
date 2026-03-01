should# 🚀 Quick Start: Deploy to dan.insightfusionanalytics.com

## Simple 3-Step Process (20 minutes)

### What You Need:
- ✅ GitHub Account (free)
- ✅ Render.com Account (free)
- ✅ Hostinger domain: insightfusionanalytics.com

**Cost: $0/month (Free tier)** or **$7/month (Starter - no sleep, faster)**

---

## Step 1: Push to GitHub (5 minutes)

```bash
cd /Users/ajinkya/Desktop/weekly_sales_analysis-main

# Initialize git repository
git init

# Add all files
git add .

# Commit
git commit -m "Deploy sales dashboard"

# Go to https://github.com/new and create a repository
# Name it: weekly-sales-analysis
# Don't initialize with README (we already have code)

# Push to GitHub (replace YOUR_USERNAME with your GitHub username)
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/weekly-sales-analysis.git
git push -u origin main
```

✅ **Done!** Your code is now on GitHub.

---

## Step 2: Deploy to Render.com (10 minutes)

### 2.1 Create Account
1. Go to **https://render.com**
2. Click **"Get Started for Free"**
3. **Sign in with GitHub** (easiest option)
4. Authorize Render to access your repositories

### 2.2 Create Web Service
1. Click **"New +"** button (top right corner)
2. Select **"Web Service"**
3. Find your **weekly-sales-analysis** repository
4. Click **"Connect"**

### 2.3 Configure Settings
Fill in these values:

```
Name: sales-dashboard
Region: Singapore (or closest to you)
Branch: main
Root Directory: (leave empty)
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
Instance Type: Free (or Starter for $7/month - no sleep)
```

### 2.4 Add Environment Variables
Click **"Advanced"** → Add these environment variables:

```
PYTHON_VERSION = 3.11.0
STREAMLIT_SERVER_HEADLESS = true
STREAMLIT_SERVER_ENABLE_CORS = false
```

### 2.5 Deploy!
1. Click **"Create Web Service"**
2. Wait 5-10 minutes for build & deploy
3. Watch the logs - you'll see:
   ```
   ==> Building...
   ==> Downloading dependencies...
   ==> Starting service...
   ==> Your service is live 🎉
   ```
4. Copy your Render URL: `https://sales-dashboard-xxxx.onrender.com`
5. Test it - click the URL to verify your dashboard works!

✅ **Done!** Your dashboard is live on Render.

---

## Step 3: Connect Custom Domain (5 minutes setup + 10 mins DNS)

### 3.1 Add Custom Domain in Render
1. In Render dashboard, go to your **sales-dashboard** service
2. Click **"Settings"** tab
3. Scroll to **"Custom Domain"** section
4. Click **"Add Custom Domain"**
5. Enter: `dan.insightfusionanalytics.com`
6. Click **"Save"**
7. **Copy the CNAME value** shown (looks like: `sales-dashboard-xxxx.onrender.com`)

### 3.2 Configure Hostinger DNS
1. Login to **https://hpanel.hostinger.com**
2. Go to **Domains**
3. Click on **insightfusionanalytics.com**
4. Click **"DNS / Name Servers"**
5. Click **"Add Record"**
6. Configure CNAME:
   ```
   Type: CNAME
   Name: dan
   Points to: sales-dashboard-xxxx.onrender.com
   TTL: 14400 (leave default)
   ```
7. Click **"Add Record"**

### 3.3 Wait for DNS Propagation
- **Typical wait:** 10-30 minutes
- **Check status:**  
  ```bash
  nslookup dan.insightfusionanalytics.com
  ```

### 3.4 Verify SSL Certificate
1. Go back to Render **"Settings"** → **"Custom Domain"**
2. Wait for green checkmark next to your domain (5-10 mins after DNS propagates)
3. SSL certificate automatically issued by Render!

✅ **Done!** Visit: **https://dan.insightfusionanalytics.com** 🎉

---

## 🎯 Final Checklist

After deployment, verify:

- [ ] Dashboard loads at: https://dan.insightfusionanalytics.com
- [ ] HTTPS (🔒 padlock) is showing
- [ ] File upload buttons appear in sidebar
- [ ] Upload NSW.csv, QLD.csv, WA.csv files
- [ ] All visualizations render correctly
- [ ] No console errors (F12 → Console)

---

## 📊 What You Get

### Free Tier:
- ✅ 512 MB RAM
- ✅ 100 GB bandwidth/month
- ✅ Custom domain + SSL
- ✅ Auto-deploy from GitHub
- ⚠️ Service sleeps after 15 mins inactivity
- ⚠️ Takes ~30 seconds to wake up on first request

### Starter Plan ($7/month):
- ✅ Always-on (no sleep!)
- ✅ Instant access
- ✅ Better performance
- ✅ More resources

**To upgrade:** Render Dashboard → Settings → Instance Type → Starter

---

## 🔄 Auto-Deploy (Already Working!)

Every time you push to GitHub, Render automatically:
1. Detects the push
2. Rebuilds your app
3. Deploys new version
4. Zero downtime!

**Try it:**
```bash
# Make a change to app.py
# Then:
git add .
git commit -m "Update dashboard"
git push

# Watch Render dashboard - it auto-deploys! 🚀
```

---

## 🐛 Troubleshooting

### Issue: Build failed on Render
**Check:** Build logs in Render dashboard  
**Fix:** Verify requirements.txt has correct versions

### Issue: App not loading
**Check:** Start command includes `--server.port=$PORT --server.address=0.0.0.0`  
**Fix:** Review logs in Render dashboard

### Issue: Custom domain not working
**Wait:** DNS can take 10-30 minutes to propagate  
**Check:** `nslookup dan.insightfusionanalytics.com` should show CNAME record  
**Fix:** Verify CNAME in Hostinger points to correct Render URL

### Issue: App is slow/freezing
**Cause:** Free tier has limited resources  
**Fix:** Upgrade to Starter plan ($7/month) or optimize caching with `@st.cache_data`

---

## 🆘 Need Help?

**Render Support:**
- Docs: https://render.com/docs/web-services
- Community: https://community.render.com

**Hostinger Support:**
- Help: https://www.hostinger.com/support
- DNS Guide: Search for "CNAME record" in support

---

## ✅ You're Live!

Your dashboard is now:
- 🌐 Live at: **https://dan.insightfusionanalytics.com**
- 🔒 Secured with HTTPS
- 🚀 Auto-deploys from GitHub
- 💰 Free tier (or $7/month for always-on)

**Share your dashboard link with clients or team! 🎉**

---

## 📚 Additional Resources

- [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) - Detailed deployment guide
- [README.md](README.md) - Project documentation
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture (for VPS reference)
