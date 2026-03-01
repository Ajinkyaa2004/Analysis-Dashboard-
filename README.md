# 📊 Weekly Sales Analysis Dashboard

An interactive Streamlit dashboard for analyzing sales data across multiple branches (NSW, QLD, WA). Upload your CSV files and get instant visualizations and insights!

## 🌐 Live Demo
**Production URL:** https://dan.insightfusionanalytics.com

**Deployed on:** Render.com with Hostinger custom domain

## 🚀 Features

- **📤 Easy File Upload**: Upload CSV files for each branch through the sidebar
- **� Annual Sales Analysis Dashboard**: 
  - Upload historical sales data (Excel format)
  - View comprehensive annual sales overview with key metrics
  - Quarter-by-quarter analysis across multiple years
  - Week-by-week sales trends
  - Year-over-year comparative analysis
  - Branch performance comparison
- **📈 Weekly Sales Tracking**: Quarterly and weekly sales trends with historical data comparison
- **📅 Monthly Sales Analysis**: Visual representation of monthly sales by branch
- **🔍 Customer Trend Analysis**: Identify rising and dropping customers year-over-year
- **🧾 Customer Purchase Details**: Deep dive into individual customer purchase patterns
- **🎛️ Interactive Filters**: Filter by branch, customer, date range, financial year, and more
- **📊 Rich Visualizations**: Interactive charts powered by Plotly

## 📋 Requirements

- Python 3.8 or higher
- Required packages (see `requirements.txt`):
  - streamlit
  - pandas
  - matplotlib
  - seaborn
  - plotly
  - openpyxl

## 🛠️ Local Installation

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd weekly_sales_analysis-main
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the application
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📊 CSV File Format

Your CSV files should contain the following columns:
- Entity Name
- Branch Region
- Branch
- Division
- Due Date
- Top Level Customer ID
- Top Level Customer Name
- Customer ID
- Customer
- Billing Group ID
- Billing Group
- Invoice ID
- Invoice #
- Issue Date
- Total
- Outstanding
- Delivery
- Status

**Note**: The first row should contain your data (no header row in CSV). The app will assign column names automatically.

## 📈 Historical Sales Data Format (Excel)

For the Annual Sales Analysis Dashboard, upload an Excel file (.xlsx or .xls) with the following structure:

### Required Sheets
- **WA** (Western Australia)
- **QLD** (Queensland)  
- **NSW** (New South Wales)

### Sheet Structure
- **Row 1**: Financial year headers (e.g., '18/19', '19/20', '20/21')
- **Row 2**: Optional sub-headers
- **Row 3+**: Weekly sales data (Week 1, Week 2, ..., Week 52)

**Example Structure:**
| Week No | 18/19   | 19/20   | 20/21   |
|---------|---------|---------|---------|
| Week 1  | 125,000 | 130,000 | 145,000 |
| Week 2  | 128,000 | 132,000 | 148,000 |
| ...     | ...     | ...     | ...     |

📖 **For detailed format specifications, see [HISTORICAL_DATA_FORMAT.md](HISTORICAL_DATA_FORMAT.md)**

## 🌐 Deployment

### 🚀 Deploy to Render.com (Recommended - Current Setup)

**Quick Start:** See [RENDER_QUICK_START.md](RENDER_QUICK_START.md) for 20-minute deployment guide

**Detailed Guide:** See [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) for complete instructions

**Summary:**
1. Push your code to GitHub
2. Connect repository to Render.com
3. Configure custom domain (dan.insightfusionanalytics.com) via Hostinger DNS
4. Automatic HTTPS + auto-deploy on every push!

**Cost:** FREE (with 15-min sleep) or $7/month (always-on, faster)

**Why Render.com?**
- ✅ Native Python/Streamlit support
- ✅ Custom domain with free SSL
- ✅ Auto-deploy from GitHub
- ✅ Free tier available
- ✅ Zero server management

---

### Alternative Deployment Options

<details>
<summary>📘 Streamlit Community Cloud (FREE)</summary>

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Select your repo and deploy
5. Get public URL: `https://yourapp.streamlit.app`

**Note:** Custom domain requires paid plan
</details>

<details>
<summary>🐳 Docker</summary>

Already configured! See `Dockerfile` in repository.

```bash
docker build -t sales-dashboard .
docker run -p 8501:8501 sales-dashboard
```
</details>

<details>
<summary>☁️ VPS (DigitalOcean/AWS)</summary>

For full control, see [ARCHITECTURE.md](ARCHITECTURE.md) and VPS setup scripts.

**Cost:** $6-12/month
</details>

## 📖 Usage Guide

1. **Upload Files**: Use the sidebar to upload CSV files for NSW, QLD, and WA branches
2. **Wait for Processing**: The app will automatically process and load your data
3. **Apply Filters**: Use sidebar filters to narrow down your analysis
4. **Explore Visualizations**: Scroll through the dashboard to see various charts and insights
5. **Download Reports**: Use the download buttons to export filtered data

## 🔧 Troubleshooting

### App won't start
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.8+)

### Files not uploading
- Check CSV format matches the required structure
- Ensure file size is reasonable (< 200MB recommended)
- Verify no special characters in filenames

### Visualizations not showing
- Check browser console for errors
- Try clearing browser cache
- Ensure data has valid dates and numeric values

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 📧 Support

For questions or issues, please open an issue on GitHub or contact the development team.

---

**Built with ❤️ using Streamlit**
# Weekly-Sales-Analysis
