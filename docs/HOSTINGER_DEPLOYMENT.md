# 🌐 Deploying to dan.insightfusionanalytics.com with Hostinger

## ⚠️ Important Note
Vercel does NOT support Streamlit apps (it's for JavaScript frameworks). This guide shows you how to deploy your Streamlit app with your Hostinger domain.

## 🚀 Method 1: Streamlit Cloud + Hostinger DNS (Recommended - FREE)

### Step 1: Deploy on Streamlit Cloud

1. **Push your code to GitHub:**
   ```bash
   cd /Users/ajinkya/Desktop/weekly_sales_analysis-main
   git init
   git add .
   git commit -m "Initial deployment"
   git branch -M main
   git remote add origin https://github.com/YOUR_GITHUB_USERNAME/sales-dashboard.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud:**
   - Go to https://share.streamlit.io
   - Sign in with GitHub
   - Click "New app"
   - Select your repository: `YOUR_GITHUB_USERNAME/sales-dashboard`
   - Branch: `main`
   - Main file path: `app.py`
   - Click "Deploy"
   - Wait 2-3 minutes
   - You'll get a URL like: `https://your-app-name.streamlit.app`

### Step 2: Configure DNS on Hostinger

**Note:** Streamlit Cloud FREE tier doesn't support custom domains directly. You have 2 options:

#### Option A: Use CNAME (Redirect)
This will redirect dan.insightfusionanalytics.com to your Streamlit Cloud URL.

1. **Login to Hostinger:**
   - Go to https://hpanel.hostinger.com
   - Navigate to Domains → insightfusionanalytics.com → DNS / Nameservers

2. **Add CNAME Record:**
   ```
   Type: CNAME
   Name: dan
   Points to: your-app-name.streamlit.app
   TTL: 14400 (or default)
   ```

3. **Wait 10-30 minutes** for DNS propagation

4. **Access your app:** http://dan.insightfusionanalytics.com (will redirect to Streamlit URL)

**Limitation:** The URL will change to the Streamlit URL after loading.

#### Option B: Use HTML Redirect with iFrame
Create a simple HTML page on Hostinger that embeds your Streamlit app.

1. **Create index.html on Hostinger:**
   ```html
   <!DOCTYPE html>
   <html>
   <head>
       <title>Data Analysis Dashboard</title>
       <style>
           body, html { margin: 0; padding: 0; height: 100%; overflow: hidden; }
           iframe { width: 100%; height: 100%; border: none; }
       </style>
   </head>
   <body>
       <iframe src="https://your-app-name.streamlit.app" 
               allow="geolocation; microphone; camera; midi; encrypted-media"
               allowfullscreen>
       </iframe>
   </body>
   </html>
   ```

2. **Upload to Hostinger subdomain folder**

**Limitation:** Some Streamlit features might not work perfectly in iframe.

---

## 🏆 Method 2: VPS Hosting + Full Domain Control (Paid but Professional)

This gives you complete control with your custom domain working perfectly.

### Prerequisites:
- VPS or Cloud Server (DigitalOcean, AWS, Linode, etc.)
- Budget: $5-10/month

### Step 1: Set Up VPS Server

1. **Create a VPS:**
   - DigitalOcean: https://www.digitalocean.com (Recommended)
   - Choose: Ubuntu 22.04, $6/month droplet
   - Get your server IP address (e.g., 123.45.67.89)

2. **SSH into your server:**
   ```bash
   ssh root@123.45.67.89
   ```

3. **Install dependencies:**
   ```bash
   # Update system
   apt update && apt upgrade -y
   
   # Install Python and pip
   apt install python3-pip python3-venv nginx certbot python3-certbot-nginx -y
   
   # Create app directory
   mkdir -p /var/www/sales-dashboard
   cd /var/www/sales-dashboard
   
   # Clone your repository
   git clone https://github.com/YOUR_GITHUB_USERNAME/sales-dashboard.git .
   
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install requirements
   pip install -r requirements.txt
   ```

4. **Create systemd service:**
   ```bash
   cat > /etc/systemd/system/streamlit.service << 'EOF'
   [Unit]
   Description=Streamlit Sales Dashboard
   After=network.target
   
   [Service]
   Type=simple
   User=root
   WorkingDirectory=/var/www/sales-dashboard
   Environment="PATH=/var/www/sales-dashboard/venv/bin"
   ExecStart=/var/www/sales-dashboard/venv/bin/streamlit run app.py --server.port 8501 --server.address 127.0.0.1
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   EOF
   
   # Enable and start service
   systemctl enable streamlit
   systemctl start streamlit
   systemctl status streamlit
   ```

### Step 2: Configure Nginx Reverse Proxy

1. **Create Nginx configuration:**
   ```bash
   cat > /etc/nginx/sites-available/dan.insightfusionanalytics.com << 'EOF'
   server {
       listen 80;
       server_name dan.insightfusionanalytics.com;
   
       location / {
           proxy_pass http://127.0.0.1:8501;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           proxy_read_timeout 86400;
       }
       
       location /_stcore/stream {
           proxy_pass http://127.0.0.1:8501/_stcore/stream;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
           proxy_read_timeout 86400;
       }
   }
   EOF
   
   # Enable site
   ln -s /etc/nginx/sites-available/dan.insightfusionanalytics.com /etc/nginx/sites-enabled/
   
   # Test and reload Nginx
   nginx -t
   systemctl reload nginx
   ```

### Step 3: Configure DNS on Hostinger

1. **Login to Hostinger:**
   - Go to https://hpanel.hostinger.com
   - Navigate to Domains → insightfusionanalytics.com → DNS / Nameservers

2. **Add A Record:**
   ```
   Type: A
   Name: dan
   Points to: 123.45.67.89 (your VPS IP)
   TTL: 14400
   ```

3. **Wait 10-30 minutes** for DNS propagation

4. **Test:** http://dan.insightfusionanalytics.com

### Step 4: Add SSL Certificate (HTTPS)

```bash
# Get SSL certificate from Let's Encrypt
certbot --nginx -d dan.insightfusionanalytics.com

# Follow prompts:
# - Enter email
# - Agree to terms
# - Choose redirect HTTP to HTTPS (option 2)

# Certificate auto-renews
# Test auto-renewal:
certbot renew --dry-run
```

**Result:** Your app will be at https://dan.insightfusionanalytics.com 🎉

---

## 🔧 Method 3: Hostinger Shared Hosting (Limited - NOT Recommended)

Hostinger shared hosting typically doesn't support Python/Streamlit apps. You would need:
- VPS hosting from Hostinger (paid upgrade)
- Then follow Method 2 above

---

## 📊 Comparison

| Method | Cost | Custom Domain | HTTPS | Best For |
|--------|------|---------------|-------|----------|
| Streamlit Cloud + CNAME | FREE | Redirect only | ✅ | Quick demo |
| VPS + Full Setup | $5-10/mo | ✅ Perfect | ✅ | Production |
| Hostinger Shared | ❌ Won't work | - | - | - |

---

## ✅ Recommended Path for You

**For Professional Deployment:**

1. **Immediate/Demo:** Use Streamlit Cloud (FREE) + Option A above
2. **Production/Business:** Use VPS (Method 2) - $6/month on DigitalOcean

**I recommend Method 2 (VPS)** because:
- ✅ Full control of domain (no redirects)
- ✅ Professional HTTPS
- ✅ Custom branding at dan.insightfusionanalytics.com
- ✅ Better performance
- ✅ Can scale as needed
- ✅ Only $6/month

---

## 🚀 Quick Start: VPS Method (Recommended)

### One-Time Setup:
```bash
# 1. Create DigitalOcean account
# 2. Create droplet (Ubuntu 22.04, $6/month)
# 3. Get IP address

# 4. SSH and run setup script:
curl -O https://gist.githubusercontent.com/YOUR_GIST/streamlit-setup.sh
chmod +x streamlit-setup.sh
sudo ./streamlit-setup.sh
```

### Configure Hostinger DNS:
- Add A record: dan → YOUR_VPS_IP
- Wait 30 minutes

### Done! 🎉
Visit: https://dan.insightfusionanalytics.com

---

## 🔐 Security Checklist

- [ ] Enable UFW firewall: `ufw allow 22,80,443/tcp && ufw enable`
- [ ] Set up fail2ban: `apt install fail2ban -y`
- [ ] Regular updates: `apt update && apt upgrade -y`
- [ ] Backup your data regularly
- [ ] Use strong SSH keys
- [ ] Disable root login after creating sudo user

---

## 📞 Need Help?

- DigitalOcean Docs: https://docs.digitalocean.com
- Hostinger Support: https://support.hostinger.com
- Nginx Docs: https://nginx.org/en/docs/
- Let's Encrypt: https://letsencrypt.org/getting-started/

---

**Choose your method and follow the steps. Method 2 (VPS) is highly recommended for your use case!**
