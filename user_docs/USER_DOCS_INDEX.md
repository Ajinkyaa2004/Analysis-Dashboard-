# 📚 User Documentation Index

Welcome! This folder contains all the documentation you need to prepare your data files for the Sales Analysis Dashboard.

---

## 📖 Documentation Files

### 1. **[USER_DATA_REQUIREMENTS.md](USER_DATA_REQUIREMENTS.md)** 📋
**Read this first!** Complete guide covering:
- CSV file requirements and format
- Excel historical data structure
- Required vs optional columns
- Acceptable column name variations
- Common errors and solutions
- Auto-detection features
- Before-upload checklist

**Who should read:** Anyone preparing data files for the first time

---

### 2. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** 🚀
**TL;DR version** - Quick reference card with:
- Minimum requirements summary
- Valid/invalid examples
- Column name flexibility table
- Quick error solutions
- Upload checklist

**Who should read:** Returning users who need a quick refresher

---

### 3. **[EXCEL_TEMPLATE_GUIDE.md](EXCEL_TEMPLATE_GUIDE.md)** 📊
**Excel-specific guide** covering:
- Step-by-step Excel file creation
- Sheet structure and layout
- Common mistakes to avoid
- Sample data suggestions
- Best practices

**Who should read:** Users preparing historical sales data in Excel

---

## 📁 Template Files

### 4. **[TEMPLATE_CSV_MINIMAL.csv](TEMPLATE_CSV_MINIMAL.csv)** (3 columns)
Bare minimum CSV with only required fields:
- Customer Name
- Date
- Amount

**Use case:** Simplest possible format, when you only need basic sales tracking

---

### 5. **[TEMPLATE_CSV_FULL.csv](TEMPLATE_CSV_FULL.csv)** (6 columns)
Complete CSV with all common fields:
- Customer
- Invoice Date
- Total
- Branch
- Invoice No
- Outstanding

**Use case:** Full-featured sales tracking with branch, invoice numbers, and receivables

---

## 🎯 Quick Start Guide

### For New Users:

1. **Read** [USER_DATA_REQUIREMENTS.md](USER_DATA_REQUIREMENTS.md) (15 min read)
2. **Download** appropriate template:
   - [TEMPLATE_CSV_MINIMAL.csv](TEMPLATE_CSV_MINIMAL.csv) for simple needs
   - [TEMPLATE_CSV_FULL.csv](TEMPLATE_CSV_FULL.csv) for complete tracking
3. **Fill in** your data (replace sample rows with your actual sales)
4. **Create** one CSV file per branch (e.g., NSW.csv, QLD.csv, WA.csv)
5. **Upload** to dashboard

### For Excel Historical Data:

1. **Read** [EXCEL_TEMPLATE_GUIDE.md](EXCEL_TEMPLATE_GUIDE.md)
2. **Create** Excel file with:
   - One sheet per year (e.g., "2024", "2025")
   - Weeks as columns (Week 1 to Week 52)
   - Branches as rows
3. **Upload** to dashboard (optional, for historical comparison)

---

## ✅ Minimum Requirements Summary

### CSV Files (Required):
- **Must have:** Customer, Date, Amount columns (or variations)
- **Format:** CSV with headers
- **Files:** One per branch

### Excel File (Optional):
- **Must have:** Branches as rows, weeks as columns
- **Format:** .xlsx with one sheet per year
- **Purpose:** Historical comparison and trend analysis

---

## 🔍 Smart Features

The dashboard includes **Intelligent Column Mapping** that automatically detects:

| You Name It | Dashboard Understands |
|-------------|----------------------|
| "Client Name" | → Customer |
| "Invoice Date" | → Date |
| "Amount" | → Total |
| "Location" | → Branch |
| "Order No" | → Invoice Number |

**Over 30+ column name variations supported!**

---

## 🚨 Common Issues & Quick Fixes

| Issue | Solution | Reference |
|-------|----------|-----------|
| Dashboard shows "Date column not found" | Add column with "Date" in name | [USER_DATA_REQUIREMENTS.md](USER_DATA_REQUIREMENTS.md#2-date-column-required---critical) |
| Dashboard shows "Amount column not found" | Add column with "Total" or "Amount" | [USER_DATA_REQUIREMENTS.md](USER_DATA_REQUIREMENTS.md#3-totalamount-column-required---critical) |
| Excel data not loading | Check weeks are columns, not rows | [EXCEL_TEMPLATE_GUIDE.md](EXCEL_TEMPLATE_GUIDE.md#-common-mistakes-to-avoid) |
| Dates not parsing | Use DD/MM/YYYY or MM/DD/YYYY format | [USER_DATA_REQUIREMENTS.md](USER_DATA_REQUIREMENTS.md#2-date-column-required---critical) |
| Customer column warning | Add "Customer" or "Client" column | [USER_DATA_REQUIREMENTS.md](USER_DATA_REQUIREMENTS.md#1-customerclient-column-required) |

---

## 📞 Support Workflow

If you encounter issues:

1. **Check** error message in dashboard
2. **Refer** to [USER_DATA_REQUIREMENTS.md](USER_DATA_REQUIREMENTS.md) error section
3. **Verify** your file against template files
4. **Review** "Auto-Detected Configuration" in dashboard sidebar
5. **Compare** your structure to examples in documentation

---

## 🎓 Learning Path

### Beginner (Just getting started):
1. Read [QUICK_REFERENCE.md](QUICK_REFERENCE.md) (5 mins)
2. Download [TEMPLATE_CSV_MINIMAL.csv](TEMPLATE_CSV_MINIMAL.csv)
3. Edit with your data
4. Upload and test

### Intermediate (Want full features):
1. Read [USER_DATA_REQUIREMENTS.md](USER_DATA_REQUIREMENTS.md) (15 mins)
2. Download [TEMPLATE_CSV_FULL.csv](TEMPLATE_CSV_FULL.csv)
3. Add all your columns (Branch, Invoice No, etc.)
4. Upload and explore all dashboard features

### Advanced (Historical analysis):
1. Follow Intermediate path first
2. Read [EXCEL_TEMPLATE_GUIDE.md](EXCEL_TEMPLATE_GUIDE.md) (10 mins)
3. Create Excel file with weekly historical data
4. Upload both CSV and Excel files
5. Enjoy year-over-year comparisons and trends

---

## 🎯 File Preparation Checklist

### Before Creating Files:
- [ ] Identify your branches (e.g., NSW, QLD, WA)
- [ ] Decide which columns you need (minimum: Customer, Date, Amount)
- [ ] Choose date format convention (DD/MM/YYYY or MM/DD/YYYY)
- [ ] Gather historical data if needed (weekly sales by branch)

### CSV Files:
- [ ] One file per branch
- [ ] Headers in first row
- [ ] Minimum 3 columns (Customer, Date, Amount)
- [ ] Dates in consistent format
- [ ] Numbers only in amount column ($ and commas auto-handled)
- [ ] No blank rows in data

### Excel File (if using):
- [ ] .xlsx format
- [ ] One sheet per year
- [ ] Weeks as columns (Week 1, Week 2, ... Week 52)
- [ ] Branches as rows
- [ ] Numeric values only
- [ ] Branch names match CSV files

---

## 💡 Pro Tips

1. **Start Simple:** Use minimal template first, add columns later if needed
2. **Consistent Naming:** Use same branch names across all files
3. **Clean Data:** Remove blank rows, summary rows, and formatting before upload
4. **Test First:** Upload with small sample (10 rows) to verify structure
5. **Check Auto-Detection:** Always review "Auto-Detected Configuration" after upload
6. **Column Names:** Don't worry about exact names - dashboard maps variations automatically

---

## 📊 What You Get

With properly formatted files, the dashboard provides:

### CSV Analysis:
- ✅ Annual sales dashboard (4 tabs)
- ✅ Monthly branch sales comparison
- ✅ Customer trend analysis (drop vs rise)
- ✅ Detailed customer purchase reports
- ✅ Interactive filters (branch, customer, date range)

### With Historical Excel Data:
- ✅ All CSV features PLUS
- ✅ Year-over-year comparisons
- ✅ Quarterly performance analysis
- ✅ Historical trend visualization
- ✅ Week-by-week breakdowns

---

## 🆘 Still Stuck?

If documentation doesn't answer your question:
1. Upload your file anyway - dashboard provides specific error messages
2. Check error message against [USER_DATA_REQUIREMENTS.md](USER_DATA_REQUIREMENTS.md)
3. Review "Auto-Detected Configuration" section in sidebar
4. Ensure required columns (Date, Amount) exist with those keywords in name

---

## 📝 Document Version

- **Version:** 2.0
- **Last Updated:** March 2026
- **Features:** Intelligent Column Mapping System
- **Compatibility:** All CSV structures with required columns

---

**Happy analyzing! 📈**
