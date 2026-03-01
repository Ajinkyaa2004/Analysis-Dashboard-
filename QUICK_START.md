# 🚀 Quick Deployment to dan.insightfusionanalytics.com

## ⚡ Fast Track Guide (30 Minutes Total)

### What You Need:
- ✅ Existing domain: insightfusionanalytics.com on Hostinger
- ✅ Target subdomain: dan.insightfusionanalytics.com
- ✅ VPS Server (recommended: DigitalOcean $6/month)

---

## 📋 Step-by-Step Instructions

### 1️⃣ Create VPS Server (5 minutes)

1. **Sign up on DigitalOcean:**
   - Visit: https://www.digitalocean.com
   - Create account (get $200 free credit for 60 days with some promotions)

2. **Create a Droplet:**
   - Click "Create" → "Droplets"
   - Choose Image: **Ubuntu 22.04 LTS**
   - Choose Plan: **Basic $6/month** (1 GB RAM, 1 CPU)
   - Choose Region: **Closest to your users** (e.g., Bangalore, Singapore)
   - Authentication: **SSH Key** (recommended) or **Password**
   - Click "Create Droplet"

3. **Note your server IP:**
   - Wait 1 minute for droplet creation
   - Copy the IP address (e.g., `123.45.67.89`)

---

### 2️⃣ Deploy Your App (10 minutes)

1. **Push code to GitHub (if not done):**
   ```bash
   cd /Users/ajinkya/Desktop/weekly_sales_analysis-main
   
   # Initialize git
   git init
   git add .
   git commit -m "Initial deployment"
   
   # Create repo on GitHub.com first, then:
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/sales-dashboard.git
   git push -u origin main
   ```

2. **SSH into your server:**
   ```bash
   # Replace with your server IP
   ssh root@123.45.67.89
   ```

3. **Run the automated setup script:**
   ```bash
   # Download setup script from your repo (after pushing code)
   # OR upload vps-setup.sh from your local folder
   
   # If you have the file locally, upload it:
   # On your Mac:
   scp /Users/ajinkya/Desktop/weekly_sales_analysis-main/vps-setup.sh root@123.45.67.89:/root/
   
   # Then on server, make it executable and run:
   chmod +x /root/vps-setup.sh
   sudo bash /root/vps-setup.sh
   ```

4. **Follow the prompts:**
   - Enter your GitHub repository URL
   - Enter your domain: `dan.insightfusionanalytics.com`
   - Wait for completion

5. **Test on server IP:**
   ```bash
   # Open in browser (replace with your IP)
   http://123.45.67.89
   ```

---

### 3️⃣ Configure Hostinger DNS (5 minutes)

1. **Login to Hostinger:**
   - Visit: https://hpanel.hostinger.com
   - Login with your credentials

2. **Navigate to DNS:**
   - Go to **Domains**
   - Click on **insightfusionanalytics.com**
   - Click **DNS / Nameservers**

3. **Add A Record:**
   - Click **Add New Record** or **Manage**
   - Select **Type**: `A`
   - Enter **Name**: `dan`
   - Enter **Points to**: `123.45.67.89` (your server IP)
   - **TTL**: `14400` (or leave default)
   - Click **Add Record** or **Save**

4. **Wait for DNS propagation:**
   - Usually takes 10-30 minutes
   - Can take up to 24 hours in rare cases

5. **Check DNS propagation:**
   ```bash
   # On your local computer
   nslookup dan.insightfusionanalytics.com
   ```

---

### 4️⃣ Enable HTTPS (5 minutes)

1. **After DNS is working, SSH back into server:**
   ```bash
   ssh root@123.45.67.89
   ```

2. **Run Certbot to get SSL certificate:**
   ```bash
   sudo certbot --nginx -d dan.insightfusionanalytics.com
   ```

3. **Follow the prompts:**
   - Enter email address
   - Agree to terms (Y)
   - Share email? (N)
   - Redirect HTTP to HTTPS? **Choose 2**

4. **Done!** Certificate auto-renews every 90 days.

---

### 5️⃣ Test Your Deployment (2 minutes)

1. **Open in browser:**
   ```
   https://dan.insightfusionanalytics.com
   ```

2. **Test file upload:**
   - Upload NSW.csv
   - Upload QLD.csv  
   - Upload WA.csv
   - Verify visualizations load

3. **Check all features:**
   - ✅ File uploads work
   - ✅ All charts render
   - ✅ Filters work
   - ✅ HTTPS padlock shows

---

## 🎉 Success!

Your app is now live at:
### https://dan.insightfusionanalytics.com

---

## 🔧 Useful Commands

### Check app status:
```bash
systemctl status streamlit
```

### View live logs:
```bash
journalctl -u streamlit -f
```

### Restart app:
```bash
systemctl restart streamlit
```

### Update app with new code:
```bash
cd /var/www/sales-dashboard
git pull
systemctl restart streamlit
```

### Check Nginx status:
```bash
systemctl status nginx
```

### View Nginx error logs:
```bash
tail -f /var/log/nginx/error.log
```

---

## 🆘 Troubleshooting

### App not loading?
```bash
# Check if Streamlit is running
systemctl status streamlit

# Check logs
journalctl -u streamlit -n 100

# Restart service
systemctl restart streamlit
```

### Domain not working?
```bash
# Check DNS
nslookup dan.insightfusionanalytics.com

# Check Nginx configuration
nginx -t

# Restart Nginx
systemctl restart nginx
```

### SSL certificate issues?
```bash
# Try again
certbot --nginx -d dan.insightfusionanalytics.com

# Force renewal
certbot renew --force-renewal
```

### File upload not working?
Check Nginx file size limit in `/etc/nginx/sites-available/dan.insightfusionanalytics.com`:
```nginx
client_max_body_size 200M;
```

---

## 💰 Cost Breakdown

| Service | Cost | Purpose |
|---------|------|---------|
| Hostinger Domain | Already paid | DNS management |
| DigitalOcean VPS | $6/month | Server hosting |
| SSL Certificate | FREE | Let's Encrypt HTTPS |
| **Total** | **$6/month** | Full deployment |

---

## 📱 What You Get

✅ Custom domain: **dan.insightfusionanalytics.com**
✅ HTTPS/SSL: Secure connection
✅ Full control: Your own server
✅ Scalable: Upgrade anytime
✅ Professional: Production-ready
✅ Fast: Dedicated resources

---

## 🔄 Future Updates

When you make changes to your code:

```bash
# 1. Commit changes locally
cd /Users/ajinkya/Desktop/weekly_sales_analysis-main
git add .
git commit -m "Updated features"
git push origin main

# 2. SSH to server and update
ssh root@123.45.67.89
cd /var/www/sales-dashboard
git pull
systemctl restart streamlit

# 3. Changes live in 10 seconds!
```

---

## 📞 Need Help?

- **DNS Issues**: Contact Hostinger Support
- **VPS Issues**: DigitalOcean has 24/7 chat support
- **App Issues**: Check logs with `journalctl -u streamlit -f`

---

**You're all set! Enjoy your professional deployment! 🚀**
