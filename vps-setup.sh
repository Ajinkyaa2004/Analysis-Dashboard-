#!/bin/bash

# Streamlit Dashboard VPS Setup Script
# For Ubuntu 22.04 LTS
# Usage: sudo bash vps-setup.sh

set -e

echo "======================================"
echo "Streamlit Dashboard VPS Setup"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root${NC}" 
   exit 1
fi

echo -e "${GREEN}Step 1: Updating system...${NC}"
apt update && apt upgrade -y

echo -e "${GREEN}Step 2: Installing dependencies...${NC}"
apt install -y python3-pip python3-venv nginx certbot python3-certbot-nginx git ufw fail2ban

echo -e "${GREEN}Step 3: Configuring firewall...${NC}"
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

echo -e "${GREEN}Step 4: Enter your GitHub repository URL:${NC}"
read -p "GitHub URL (e.g., https://github.com/username/repo.git): " REPO_URL

echo -e "${GREEN}Step 5: Enter your domain name:${NC}"
read -p "Domain (e.g., dan.insightfusionanalytics.com): " DOMAIN_NAME

# Create app directory
echo -e "${GREEN}Step 6: Setting up application...${NC}"
mkdir -p /var/www/sales-dashboard
cd /var/www/sales-dashboard

# Clone repository
if [ -d ".git" ]; then
    echo "Repository already exists, pulling latest changes..."
    git pull
else
    echo "Cloning repository..."
    git clone "$REPO_URL" .
fi

# Create virtual environment
echo -e "${GREEN}Step 7: Creating virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# Install requirements
echo -e "${GREEN}Step 8: Installing Python packages...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Create systemd service
echo -e "${GREEN}Step 9: Creating systemd service...${NC}"
cat > /etc/systemd/system/streamlit.service << EOF
[Unit]
Description=Streamlit Sales Dashboard
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/sales-dashboard
Environment="PATH=/var/www/sales-dashboard/venv/bin"
ExecStart=/var/www/sales-dashboard/venv/bin/streamlit run app.py --server.port 8501 --server.address 127.0.0.1 --server.headless true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
systemctl daemon-reload
systemctl enable streamlit
systemctl start streamlit

# Check if service started
if systemctl is-active --quiet streamlit; then
    echo -e "${GREEN}✓ Streamlit service started successfully${NC}"
else
    echo -e "${RED}✗ Failed to start Streamlit service${NC}"
    journalctl -u streamlit -n 50
    exit 1
fi

# Create Nginx configuration
echo -e "${GREEN}Step 10: Configuring Nginx...${NC}"
cat > /etc/nginx/sites-available/$DOMAIN_NAME << EOF
server {
    listen 80;
    server_name $DOMAIN_NAME;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 86400;
        proxy_buffering off;
    }
    
    location /_stcore/stream {
        proxy_pass http://127.0.0.1:8501/_stcore/stream;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_read_timeout 86400;
    }

    client_max_body_size 200M;
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/$DOMAIN_NAME /etc/nginx/sites-enabled/

# Remove default site if exists
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
if nginx -t; then
    echo -e "${GREEN}✓ Nginx configuration valid${NC}"
    systemctl reload nginx
else
    echo -e "${RED}✗ Nginx configuration error${NC}"
    exit 1
fi

# Get server IP
SERVER_IP=$(curl -s ifconfig.me)

echo ""
echo "======================================"
echo -e "${GREEN}Setup Complete!${NC}"
echo "======================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Configure DNS on Hostinger:"
echo "   - Login to https://hpanel.hostinger.com"
echo "   - Go to Domains → insightfusionanalytics.com → DNS"
echo "   - Add A Record:"
echo "     Type: A"
echo "     Name: dan"
echo -e "     Points to: ${YELLOW}$SERVER_IP${NC}"
echo "     TTL: 14400"
echo ""
echo "2. After DNS propagation (10-30 minutes), enable HTTPS:"
echo -e "   ${YELLOW}sudo certbot --nginx -d $DOMAIN_NAME${NC}"
echo ""
echo "3. Test your app:"
echo -e "   ${YELLOW}http://$DOMAIN_NAME${NC} (or http://$SERVER_IP:80 now)"
echo ""
echo "Useful commands:"
echo "  - Check service status: systemctl status streamlit"
echo "  - View logs: journalctl -u streamlit -f"
echo "  - Restart service: systemctl restart streamlit"
echo "  - Update app: cd /var/www/sales-dashboard && git pull && systemctl restart streamlit"
echo ""
echo "======================================"
