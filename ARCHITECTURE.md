# 🌐 Deployment Architecture

## Current Setup: dan.insightfusionanalytics.com

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  User Browser → dan.insightfusionanalytics.com             │
│         ↓                                                   │
│   [Hostinger DNS]                                           │
│         ↓                                                   │
│   A Record: dan → 123.45.67.89 (VPS IP)                   │
│         ↓                                                   │
│   [DigitalOcean VPS - Ubuntu 22.04]                        │
│         ↓                                                   │
│   Port 80/443 → [Nginx Reverse Proxy]                     │
│         ↓                                                   │
│   HTTPS/SSL via Let's Encrypt                              │
│         ↓                                                   │
│   Nginx → localhost:8501                                    │
│         ↓                                                   │
│   [Streamlit App via systemd]                              │
│         ↓                                                   │
│   Python 3.11 + Virtual Environment                         │
│         ↓                                                   │
│   Your Dashboard (app.py)                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Components Explained

### 1. **Domain & DNS (Hostinger)**
- **Main Domain**: insightfusionanalytics.com
- **Subdomain**: dan.insightfusionanalytics.com
- **Purpose**: Points visitors to your VPS server
- **Configuration**: A Record → VPS IP address

### 2. **VPS Server (DigitalOcean)**
- **OS**: Ubuntu 22.04 LTS
- **Specs**: 1 GB RAM, 1 CPU, 25 GB SSD
- **Cost**: $6/month
- **Purpose**: Hosts your application
- **IP**: Public IP address (e.g., 123.45.67.89)

### 3. **Nginx (Web Server)**
- **Purpose**: Reverse proxy and SSL termination
- **Ports**: 
  - 80 (HTTP) → Redirects to HTTPS
  - 443 (HTTPS) → Proxies to Streamlit
- **Configuration**: `/etc/nginx/sites-available/dan.insightfusionanalytics.com`

### 4. **SSL/HTTPS (Let's Encrypt)**
- **Provider**: Free SSL from Let's Encrypt
- **Tool**: Certbot
- **Auto-renewal**: Every 90 days
- **Purpose**: Secure HTTPS connection (🔒 padlock)

### 5. **Streamlit Application**
- **Service**: systemd (streamlit.service)
- **Port**: 8501 (localhost only)
- **Purpose**: Runs your dashboard
- **Auto-restart**: Yes, on failure or reboot

### 6. **Python Environment**
- **Version**: Python 3.11
- **Type**: Virtual environment (venv)
- **Location**: `/var/www/sales-dashboard/venv`
- **Packages**: From requirements.txt

---

## Traffic Flow

### User Request:
```
1. User types: https://dan.insightfusionanalytics.com
2. Browser DNS lookup → Hostinger DNS
3. DNS returns VPS IP: 123.45.67.89
4. Browser connects to VPS on port 443 (HTTPS)
5. Nginx receives request
6. Nginx checks SSL certificate
7. Nginx forwards to localhost:8501
8. Streamlit processes request
9. Response → Nginx → Browser
10. Dashboard loads for user
```

### File Upload:
```
1. User uploads CSV via browser
2. File sent via HTTPS to Nginx
3. Nginx forwards to Streamlit (max 200MB)
4. Streamlit processes in memory
5. Visualizations generated
6. Results sent back to browser
```

---

## Security Layers

```
┌─────────────────────────────────────┐
│ 1. Firewall (UFW)                   │
│    ✓ Only ports 22, 80, 443 open    │
├─────────────────────────────────────┤
│ 2. SSL/TLS Encryption               │
│    ✓ HTTPS only (A+ rating)         │
├─────────────────────────────────────┤
│ 3. Nginx Security Headers           │
│    ✓ XSS protection                 │
│    ✓ CORS configured                │
├─────────────────────────────────────┤
│ 4. Streamlit (localhost only)       │
│    ✓ Not exposed to internet        │
│    ✓ Only Nginx can access          │
├─────────────────────────────────────┤
│ 5. Fail2ban                         │
│    ✓ Blocks brute force attacks     │
└─────────────────────────────────────┘
```

---

## File Structure on VPS

```
/var/www/sales-dashboard/
├── app.py                    # Main Streamlit app
├── requirements.txt          # Python dependencies
├── .streamlit/
│   └── config.toml          # Streamlit configuration
├── venv/                     # Virtual environment
│   ├── bin/
│   ├── lib/
│   └── ...
└── .git/                     # Git repository

/etc/nginx/sites-available/
└── dan.insightfusionanalytics.com    # Nginx config

/etc/systemd/system/
└── streamlit.service        # Systemd service file

/etc/letsencrypt/
└── live/dan.insightfusionanalytics.com/
    ├── fullchain.pem        # SSL certificate
    └── privkey.pem          # Private key
```

---

## Monitoring & Maintenance

### Service Status:
```bash
# Check Streamlit
systemctl status streamlit

# Check Nginx
systemctl status nginx

# Check SSL expiry
certbot certificates
```

### Logs:
```bash
# Streamlit logs
journalctl -u streamlit -f

# Nginx access logs
tail -f /var/log/nginx/access.log

# Nginx error logs
tail -f /var/log/nginx/error.log

# System logs
dmesg | tail
```

### Updates:
```bash
# System updates
apt update && apt upgrade -y

# App updates
cd /var/www/sales-dashboard
git pull
systemctl restart streamlit

# Python packages
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

---

## Alternative Architectures

### A. Streamlit Cloud (Simpler, Limited)
```
User → Streamlit Cloud → Database (optional)
✓ FREE
✗ No custom domain (free tier)
✗ 1GB resource limit
```

### B. Docker Container (More Portable)
```
User → VPS/Cloud → Docker → Streamlit Container
✓ Easy deployment
✓ Consistent environment
✗ Slightly more complex setup
```

### C. Kubernetes (Enterprise Scale)
```
User → Load Balancer → K8s Cluster → Multiple Pods
✓ High availability
✓ Auto-scaling
✗ Complex setup
✗ Higher cost
```

---

## Your Current Setup (Recommended)

**Why this architecture?**

✅ **Professional**: Own domain with HTTPS
✅ **Affordable**: Only $6/month
✅ **Scalable**: Easy to upgrade VPS
✅ **Reliable**: systemd auto-restart
✅ **Secure**: Multiple security layers
✅ **Fast**: Dedicated resources
✅ **Simple**: Easy to maintain and update

**Perfect for:**
- Business dashboards
- Client presentations
- Internal tools
- Production applications

---

## Performance Specs

| Metric | Specification |
|--------|--------------|
| RAM | 1 GB |
| CPU | 1 vCPU |
| Storage | 25 GB SSD |
| Bandwidth | 1 TB/month |
| Max File Upload | 200 MB |
| Response Time | < 500ms (avg) |
| Concurrent Users | 20-50 (depends on data) |
| Uptime | 99.9% (DigitalOcean SLA) |

**To scale up:**
- Upgrade droplet to 2GB RAM ($12/month)
- Add load balancer for high traffic
- Move data processing to background workers
- Implement Redis caching

---

**This architecture gives you a production-ready, professional deployment at minimal cost!** 🚀
