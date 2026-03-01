# 🚀 Deploy to Render.com + Hostinger Subdomain

## Why Render.com?

✅ **Perfect for Streamlit** - Native Python support  
✅ **Free tier available** - $0/month to start  
✅ **Custom domain support** - Connect dan.insightfusionanalytics.com  
✅ **Auto-deploy from Git** - Push and it deploys automatically  
✅ **HTTPS included** - Free SSL certificates  
✅ **Zero server management** - Fully managed platform  

---

## 📋 Complete Deployment Steps

### Step 1: Push to GitHub (5 minutes)

```bash
cd /Users/ajinkya/Desktop/weekly_sales_analysis-main

# Initialize git if not already done
git init

# Add all files
git add .

# Commit
git commit -m "Deploy sales dashboard to Render"

# Create repo on GitHub and push
# Go to https://github.com/new
# Create repository: weekly-sales-analysis (or any name)
# Then run:

git remote add origin https://github.com/YOUR_USERNAME/weekly-sales-analysis.git
git branch -M main
git push -u origin main
```

---

### Step 2: Deploy to Render.com (10 minutes)

#### 2.1 Create Render Account
1. Go to **https://render.com**
2. Click **"Get Started for Free"**
3. Sign up with GitHub (recommended) or email
4. Verify your email

#### 2.2 Create New Web Service
1. Click **"New +"** button (top right)
2. Select **"Web Service"**
3. Connect your GitHub account if not already connected
4. Find and select your **weekly-sales-analysis** repository
5. Click **"Connect"**

#### 2.3 Configure Web Service
Fill in these settings:

| Field | Value |
|-------|-------|
| **Name** | `sales-dashboard` (or any name) |
| **Region** | `Singapore` (closest to you) |
| **Branch** | `main` |
| **Root Directory** | Leave blank |
| **Environment** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0` |
| **Plan** | `Free` (or Starter $7/month for better performance) |

#### 2.4 Environment Variables (Advanced Settings)
Click **"Advanced"** and add these:

```
PYTHON_VERSION=3.11.0
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_ENABLE_CORS=false
```

#### 2.5 Deploy
1. Click **"Create Web Service"**
2. Wait 5-10 minutes for initial deployment
3. Watch the build logs
4. When done, you'll see: ✅ **Live** with a URL like:
   ```
   https://sales-dashboard-xxxx.onrender.com
   ```

---

### Step 3: Connect Hostinger Custom Domain (15 minutes)

#### 3.1 Get Render Domain
1. In Render dashboard, click your **sales-dashboard** service
2. Go to **"Settings"** tab
3. Scroll to **"Custom Domain"** section
4. Click **"Add Custom Domain"**
5. Enter: `dan.insightfusionanalytics.com`
6. Click **"Save"**
7. Render will show you CNAME instructions like:
   ```
   Name: dan
   Value: sales-dashboard-xxxx.onrender.com
   ```

#### 3.2 Configure Hostinger DNS
1. Login to **https://hpanel.hostinger.com**
2. Go to **Domains** → **insightfusionanalytics.com**
3. Click **"DNS / Name Servers"**
4. Click **"Add Record"**
5. Select **"CNAME"** type
6. Fill in:
   ```
   Name: dan
   Points to: sales-dashboard-xxxx.onrender.com
   TTL: 14400 (or default)
   ```
7. Click **"Add Record"**

#### 3.3 Wait for DNS Propagation
- **Typical time**: 10-30 minutes
- **Maximum**: 24-48 hours (rare)

**Check status:**
```bash
# Check if DNS is propagated
dig dan.insightfusionanalytics.com
nslookup dan.insightfusionanalytics.com
```

#### 3.4 Verify Custom Domain
1. Go back to Render dashboard
2. In **"Custom Domain"** section
3. Wait for green checkmark: ✅ **Verified**
4. SSL certificate automatically issued (5-10 mins)
5. Visit: **https://dan.insightfusionanalytics.com**

---

## 🎯 Final Result

Your dashboard will be accessible at:
- ✅ `https://dan.insightfusionanalytics.com` (custom domain)
- ✅ `https://sales-dashboard-xxxx.onrender.com` (Render domain)

Both URLs work with HTTPS automatically! 🔒

---

## 📊 Render Free Tier Limits

| Resource | Free Tier |
|----------|-----------|
| **Cost** | $0/month |
| **RAM** | 512 MB |
| **CPU** | Shared |
| **Bandwidth** | 100 GB/month |
| **Build Minutes** | 500 mins/month |
| **Instances** | Spins down after 15 mins inactivity |
| **Sleep Time** | ~30 secs to wake up |

### ⚠️ Free Tier Limitations:
- Service **sleeps after 15 minutes** of inactivity
- First request after sleep takes **30 seconds** to wake up
- Good for demos and testing
- For production → Upgrade to **Starter ($7/month)** for always-on

---

## 🚀 Upgrade to Starter Plan (Recommended)

**Benefits:**
- ✅ No sleep/downtime
- ✅ Always instant access
- ✅ Better performance
- ✅ More RAM (512MB → 2GB)
- ✅ Only $7/month

**How to upgrade:**
1. Dashboard → **sales-dashboard** → **Settings**
2. Scroll to **"Instance Type"**
3. Select **"Starter"**
4. Click **"Save Changes"**

---

## 🔄 Auto-Deploy (Built-in!)

Every time you push to GitHub, Render automatically:
1. Detects the push
2. Pulls latest code
3. Runs build command
4. Deploys new version
5. Zero downtime

**To update your app:**
```bash
# Make changes to app.py or other files
git add .
git commit -m "Update dashboard features"
git push

# Render automatically deploys! 🎉
```

---

## 🐛 Troubleshooting

### Issue 1: Build Failed
**Check:**
- requirements.txt has correct versions
- Build logs in Render dashboard
- Python version compatibility

**Fix:**
```bash
# Test locally first
pip install -r requirements.txt
streamlit run app.py
```

### Issue 2: App Not Loading
**Check:**
- Start command includes `--server.port=$PORT --server.address=0.0.0.0`
- No hardcoded port numbers in app.py
- Logs in Render dashboard

### Issue 3: Custom Domain Not Working
**Check:**
- DNS propagation (wait 30 mins)
- CNAME record points to exact Render URL
- No typos in domain name
- SSL certificate issued (green checkmark in Render)

**Verify DNS:**
```bash
nslookup dan.insightfusionanalytics.com
# Should show: dan.insightfusionanalytics.com CNAME sales-dashboard-xxxx.onrender.com
```

### Issue 4: App Freezes/Slow
**Cause:** Free tier has limited resources

**Solutions:**
- Optimize data loading
- Cache computations with `@st.cache_data`
- Upgrade to Starter plan ($7/month)

---

## 🔒 Security Checklist

✅ **HTTPS Enabled** - Automatic with Render + custom domain  
✅ **Environment Variables** - Store secrets in Render dashboard  
✅ **File Upload Limits** - Already set to 200MB in .streamlit/config.toml  
✅ **CORS Protection** - Enabled in Streamlit config  
✅ **No Exposed Ports** - Render handles all networking  

---

## 📱 Monitoring & Logs

### View Logs:
1. Render Dashboard → **sales-dashboard**
2. Click **"Logs"** tab
3. See real-time logs

### Metrics:
1. Click **"Metrics"** tab
2. View:
   - CPU usage
   - Memory usage
   - Request count
   - Response times

### Alerts:
1. Go to **"Settings"**
2. Scroll to **"Notifications"**
3. Add email for deploy notifications

---

## 💰 Cost Comparison

| Platform | Free Tier | Paid Tier | Custom Domain | Auto-Deploy |
|----------|-----------|-----------|---------------|-------------|
| **Render** | ✅ $0 (sleeps) | $7/mo (always-on) | ✅ Yes | ✅ Yes |
| Heroku | ❌ None | $5/mo | ✅ Yes | ✅ Yes |
| DigitalOcean | ❌ None | $6/mo | ✅ Yes | ⚠️ Manual |
| Streamlit Cloud | ✅ $0 | ❌ No paid | ⚠️ Limited | ✅ Yes |
| AWS/Azure | ⚠️ Complex | $10+/mo | ✅ Yes | ⚠️ Complex |

**Winner: Render.com** 🏆
- Best balance of ease + features + price
- Perfect for Streamlit apps
- Great free tier for testing

---

## 🎓 Quick Commands Reference

```bash
# Push updates
git add .
git commit -m "Update"
git push

# Check DNS propagation
nslookup dan.insightfusionanalytics.com

# Test locally before deploying
streamlit run app.py

# View Render logs (if installed Render CLI)
render logs sales-dashboard
```

---

## 🆘 Support

**Render Support:**
- Docs: https://render.com/docs
- Community: https://community.render.com
- Status: https://status.render.com

**Hostinger Support:**
- Support: https://www.hostinger.com/support
- DNS Help: Check hPanel DNS management

---

## ✅ Success Checklist

Before considering deployment complete:

- [ ] Code pushed to GitHub
- [ ] Render service created and deployed (green)
- [ ] Render URL works (https://sales-dashboard-xxxx.onrender.com)
- [ ] Custom domain added in Render
- [ ] CNAME record added in Hostinger DNS
- [ ] DNS propagated (nslookup shows CNAME)
- [ ] SSL certificate issued (green checkmark in Render)
- [ ] https://dan.insightfusionanalytics.com loads
- [ ] File upload works on live site
- [ ] All visualizations render correctly
- [ ] Auto-deploy tested (push → auto-update)

---

**You're all set! 🎉 Your dashboard will be live at dan.insightfusionanalytics.com**

**Deployment time: ~30 minutes total**
