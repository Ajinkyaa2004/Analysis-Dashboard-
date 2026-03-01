# 🚀 Deployment Checklist

Use this checklist to ensure your deployment is successful.

## ✅ Pre-Deployment Checklist

- [x] requirements.txt is complete with version numbers
- [x] .gitignore file exists
- [x] README.md with deployment instructions
- [x] Streamlit config file (.streamlit/config.toml)
- [x] Procfile for Heroku deployment
- [x] setup.sh for Heroku deployment
- [x] Dockerfile for Docker deployment
- [x] .dockerignore for Docker
- [x] runtime.txt for platform specification
- [ ] Test app locally with `streamlit run app.py`
- [ ] Test file upload with sample CSV files
- [ ] Verify all visualizations work correctly

## 🌐 Streamlit Cloud Deployment (Recommended)

### Quick Deploy Steps:
1. Push code to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Ready for deployment"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin main
   ```

2. Deploy on Streamlit Cloud:
   - Visit: https://share.streamlit.io
   - Sign in with GitHub
   - Click "New app"
   - Repository: YOUR_USERNAME/YOUR_REPO
   - Branch: main
   - Main file: app.py
   - Click "Deploy"

3. Wait 2-5 minutes for deployment

### What Streamlit Cloud Provides:
- ✅ FREE hosting
- ✅ Automatic HTTPS
- ✅ Auto-redeployment on git push
- ✅ Custom subdomain: yourapp.streamlit.app
- ✅ 1GB RAM, 1 CPU core (free tier)

### Limitations:
- 200MB file upload limit (already configured)
- App sleeps after 7 days of inactivity
- Public by default (can be made private on paid plans)

## 🐳 Docker Deployment

### Build and Test Locally:
```bash
# Build image
docker build -t sales-dashboard .

# Run container
docker run -p 8501:8501 sales-dashboard

# Test
open http://localhost:8501
```

### Deploy to Cloud:
```bash
# Tag for Docker Hub
docker tag sales-dashboard YOUR_USERNAME/sales-dashboard:latest

# Push to Docker Hub
docker push YOUR_USERNAME/sales-dashboard:latest

# Pull and run on any server
docker pull YOUR_USERNAME/sales-dashboard:latest
docker run -d -p 8501:8501 YOUR_USERNAME/sales-dashboard:latest
```

## 🔨 Heroku Deployment

### Prerequisites:
- Heroku account (free tier available)
- Heroku CLI installed

### Deploy Steps:
```bash
# Login to Heroku
heroku login

# Create new app
heroku create your-app-name

# Verify files
git add Procfile setup.sh requirements.txt
git commit -m "Add Heroku config"

# Deploy
git push heroku main

# Open app
heroku open

# View logs
heroku logs --tail
```

### Note:
Heroku free tier was discontinued in November 2022. Consider:
- Heroku Eco plan ($5/month)
- Render.com (free tier available)
- Railway.app (free tier available)

## ☁️ AWS EC2 Deployment

### Launch Instance:
1. Choose Ubuntu Server 22.04 LTS
2. Instance type: t2.micro (free tier eligible)
3. Configure security group:
   - SSH (port 22) from your IP
   - Custom TCP (port 8501) from anywhere

### Setup on EC2:
```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-public-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3-pip -y

# Clone repository
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

# Install dependencies
pip3 install -r requirements.txt

# Run in background
nohup streamlit run app.py --server.port 8501 --server.address 0.0.0.0 &

# Access app
# http://your-ec2-public-ip:8501
```

### Production Setup (PM2):
```bash
# Install Node.js and PM2
sudo apt install nodejs npm -y
sudo npm install -g pm2

# Create ecosystem file
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [{
    name: 'sales-dashboard',
    script: 'streamlit',
    args: 'run app.py --server.port 8501 --server.address 0.0.0.0',
    interpreter: 'none',
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
  }]
}
EOF

# Start with PM2
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

## 🔐 Security Considerations

### Before Going Live:
- [ ] Remove or secure any sensitive data from CSVs
- [ ] Update .gitignore to exclude data files if needed
- [ ] Set up authentication if required (Streamlit supports basic auth)
- [ ] Configure HTTPS (automatic on Streamlit Cloud)
- [ ] Set appropriate file size limits
- [ ] Consider rate limiting for uploads

### For Production:
- [ ] Add error logging
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Document API keys (if any) in secrets management
- [ ] Test with production-like data volumes

## 🧪 Testing Deployment

### Local Testing:
```bash
# Test requirements installation
pip install -r requirements.txt

# Test app runs
streamlit run app.py

# Check all features:
# - File upload works
# - All 3 branches can be uploaded
# - Visualizations render
# - Filters work correctly
# - No console errors
```

### Post-Deployment Testing:
- [ ] Upload test CSV files
- [ ] Navigate through all sections
- [ ] Test all filters
- [ ] Verify charts render correctly
- [ ] Check mobile responsiveness
- [ ] Test with larger file sizes
- [ ] Verify error messages display properly when files missing

## 📊 Monitoring

### Streamlit Cloud:
- View logs in Streamlit Cloud dashboard
- Check app health: https://yourapp.streamlit.app/_stcore/health

### Other Platforms:
```bash
# View application logs
heroku logs --tail  # Heroku
docker logs CONTAINER_ID  # Docker
pm2 logs  # PM2 on EC2
```

## 🔄 Updating Deployment

### Streamlit Cloud:
Just push to GitHub - auto-deploys!
```bash
git add .
git commit -m "Update"
git push origin main
```

### Heroku:
```bash
git push heroku main
```

### Docker:
```bash
docker build -t sales-dashboard .
docker tag sales-dashboard YOUR_USERNAME/sales-dashboard:latest
docker push YOUR_USERNAME/sales-dashboard:latest
# Pull and restart on server
```

### EC2:
```bash
git pull
pm2 restart sales-dashboard
```

## 📞 Support Resources

- Streamlit Docs: https://docs.streamlit.io
- Streamlit Community: https://discuss.streamlit.io
- Heroku Docs: https://devcenter.heroku.com
- Docker Docs: https://docs.docker.com
- AWS EC2 Docs: https://docs.aws.amazon.com/ec2

## 🎉 Success!

Your app is deployment-ready! Choose your preferred platform and follow the steps above.

**Recommended for beginners**: Start with Streamlit Cloud - it's free, easy, and perfect for this app!
