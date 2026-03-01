# 📋 Data Requirements Guide

**Last Updated:** March 2026  
**Version:** 2.0 (With Intelligent Column Mapping)

This guide explains how to prepare your CSV and Excel files for the Sales Analysis Dashboard.

---

## 📁 CSV Files (Branch Sales Data)

### File Structure

- **Format:** CSV (Comma-Separated Values)
- **Encoding:** UTF-8 (recommended) or ASCII
- **File Naming:** Any name (e.g., `NSW.csv`, `QLD.csv`, `branch_data.csv`)
- **Header Row:** Required (first row must contain column names)
- **Minimum Columns:** 3 required columns (see below)

---

### ✅ Required Columns

The dashboard uses **intelligent column mapping** to detect these 3 critical fields:

#### 1. **Customer/Client Column** (REQUIRED)
Identifies the customer name.

**Accepted Header Names:**
- `Customer`
- `Customer Name`
- `Client`
- `Client Name`
- `Cust Name`
- Any variation containing "customer" or "client"

**Format:**
- Text/String
- Example: `"ABC Company"`, `"John Doe"`, `"XYZ Ltd"`

**What Happens if Missing:**
- ⚠️ Dashboard will show a warning
- Creates placeholder "Unknown Customer"
- Analysis continues but customer-specific reports will be limited

---

#### 2. **Date Column** (REQUIRED - CRITICAL)
Records the sale/invoice date.

**Accepted Header Names:**
- `Issue Date`
- `Invoice Date`
- `Date`
- `Order Date`
- `Sale Date`
- `Transaction Date`
- Any variation containing "date"

**Format:**
- Date format: `DD/MM/YYYY` or `MM/DD/YYYY`
- Auto-detected from your data
- Example: `15/03/2025`, `03/15/2025`

**What Happens if Missing:**
- ❌ **ERROR - Dashboard cannot proceed**
- Date is essential for time-based analysis
- You must include this column

---

#### 3. **Total/Amount Column** (REQUIRED - CRITICAL)
Contains the sale amount or invoice total.

**Accepted Header Names:**
- `Total`
- `Amount`
- `Sales`
- `Revenue`
- `Invoice Amount`
- `Sale Amount`
- `Net Total`
- Any variation containing "total", "amount", "sales", or "revenue"

**Format:**
- Numeric (can include currency symbols: $, ₹, €, £)
- Commas allowed: `1,234.56`
- Example: `1234.56`, `$1,234.56`, `₹45000`

**What Happens if Missing:**
- ❌ **ERROR - Dashboard cannot proceed**
- Amount is essential for financial analysis
- You must include this column

---

### 🔵 Optional Columns (Auto-Detected)

These columns enhance functionality but are not required:

#### 4. **Branch Column**
If your CSV contains data for multiple branches.

**Accepted Names:**
- `Branch`
- `Branch Name`
- `Location`
- `Store`
- `Office`

**Format:** Text (e.g., `"NSW"`, `"QLD"`, `"Melbourne"`)

**If Missing:** Branch name will be taken from the uploaded file name

---

#### 5. **Invoice/Order ID Column**
Unique identifier for transactions.

**Accepted Names:**
- `Invoice No`
- `Invoice Number`
- `Invoice ID`
- `Order No`
- `Order Number`
- `Transaction ID`

**Format:** Text or Number (e.g., `"INV-12345"`, `54321`)

---

#### 6. **Outstanding/Due Amount Column**
Unpaid balance (if tracking receivables).

**Accepted Names:**
- `Outstanding`
- `Due`
- `Balance`
- `Remaining`
- `Unpaid`

**Format:** Numeric (same as Total column)

---

### 📊 Example CSV Files

#### ✅ **Acceptable CSV #1** (Minimal - 3 columns)
```csv
Customer Name,Invoice Date,Amount
ABC Company,15/01/2025,15000
XYZ Ltd,20/01/2025,25000
John Doe,25/01/2025,5000
```

#### ✅ **Acceptable CSV #2** (With optional columns)
```csv
Client,Date,Total,Branch,Invoice No,Outstanding
ABC Company,15/01/2025,15000.50,NSW,INV-001,2000
XYZ Ltd,20/01/2025,25000.00,QLD,INV-002,0
John Doe,25/01/2025,5000.75,WA,INV-003,500
```

#### ✅ **Acceptable CSV #3** (Different names, full structure)
```csv
Customer,Issue Date,Invoice Amount,Location,Order Number,Due Amount,Product,Quantity,Unit Price,Discount,Tax,Payment Method,Sales Rep,Notes,Region,Category,Status,Created By
ABC Company,15/01/2025,$15000.00,NSW,ORD-12345,2000,Widget,10,1500,0,0,Credit,John,,,Electronics,Paid,Admin
XYZ Ltd,20/02/2025,$25000.00,QLD,ORD-12346,0,Gadget,5,5000,0,0,Cash,Jane,,,Hardware,Pending,Admin
```

#### ❌ **NOT Acceptable CSV #1** (Missing Date)
```csv
Customer,Amount
ABC Company,15000
XYZ Ltd,25000
```
**Error:** No date column found. Cannot proceed.

#### ❌ **NOT Acceptable CSV #2** (Missing Amount)
```csv
Customer,Invoice Date,Product
ABC Company,15/01/2025,Widget
XYZ Ltd,20/01/2025,Gadget
```
**Error:** No total/amount column found. Cannot proceed.

#### ⚠️ **Warning CSV** (Missing Customer)
```csv
Invoice Date,Amount
15/01/2025,15000
20/01/2025,25000
```
**Warning:** No customer column found. Will use "Unknown Customer" placeholder. Analysis continues but limited customer insights.

---

### 📋 CSV Best Practices

1. **Always include headers** in the first row
2. **Don't use special characters** in column names (stick to letters, numbers, spaces)
3. **Consistent date format** within each file (don't mix DD/MM/YYYY and MM/DD/YYYY)
4. **Remove extra rows** (summaries, totals, blank rows) at top or bottom
5. **One transaction per row** (don't merge cells)
6. **Avoid formulas** - export calculated values only
7. **Remove formatting** (colors, borders) when exporting
8. **Use UTF-8 encoding** if you have special characters (₹, €, etc.)

---

## 📊 Historical Data (Excel File)

### File Structure

- **Format:** Excel (.xlsx) or (.xls)
- **File Naming:** Any name (e.g., `historical_data.xlsx`, `weekly_sales.xlsx`)
- **Multiple Sheets:** Supported (one per year, e.g., "2023", "2024", "2025")

---

### ✅ Excel Sheet Requirements

#### Sheet Structure
Each sheet should contain **weekly sales data** with:

**Required Columns:**
1. **Week Number** - Column header: `Week 1`, `Week 2`, ..., `Week 52` (or up to 53)
2. **Branch Rows** - Row labels: Branch names (`NSW`, `QLD`, `WA`, etc.)

#### Example Sheet Structure:

**Sheet Name:** `2024`

```
           Week 1    Week 2    Week 3    Week 4    ...    Week 52
NSW         45000     48000     52000     47000           50000
QLD         38000     39000     41000     40000           42000
WA          25000     26000     28000     27000           29000
VIC         35000     36000     37000     38000           39000
```

#### ✅ **Acceptable Format 1** (Horizontal layout - Week columns)
```
Branch    Week 1    Week 2    Week 3    Week 4
NSW       45000     48000     52000     47000
QLD       38000     39000     41000     40000
WA        25000     26000     28000     27000
```

#### ✅ **Acceptable Format 2** (With quarter summaries)
```
           Week 1    Week 2    ...    Q1 Total    Week 14    ...    Q2 Total
NSW         45000     48000           585000      47000              610000
QLD         38000     39000           494000      40000              520000
```

#### ❌ **NOT Acceptable Format** (Vertical layout)
```
Week    NSW     QLD     WA
1       45000   38000   25000
2       48000   39000   26000
3       52000   41000   28000
```
**Error:** Dashboard expects branches as rows, weeks as columns.

---

### 📊 Historical Data Best Practices

1. **Sheet Names:** Use year numbers (`2023`, `2024`, `2025`) or descriptive names (`Sales_2024`)
2. **Week Numbering:** Start from Week 1, sequential (Week 1, 2, 3... 52/53)
3. **Consistent Branches:** Use same branch names across all sheets
4. **Numeric Values Only:** Don't include currency symbols or commas in cells
5. **No Blank Rows/Columns:** Between data (summaries at end are OK)
6. **Match CSV Branches:** Branch names should match your CSV file branches

---

## 🔍 Auto-Detection Features

The dashboard automatically detects:

✅ **CSV Structure:**
- Number of columns
- Header row presence
- Column name variations

✅ **Date Format:**
- DD/MM/YYYY (e.g., 15/03/2025)
- MM/DD/YYYY (e.g., 03/15/2025)

✅ **Currency Symbol:**
- $ (Dollar)
- ₹ (Rupee)
- € (Euro)
- £ (Pound)
- or none

✅ **Excel Structure:**
- Sheet names (years)
- Week count (52 or 53 weeks)
- Branch names

✅ **Column Mappings:**
- Intelligent matching of column names
- Shows detected mappings in sidebar

---

## 🚨 Common Errors & Solutions

### Error: "Date column not found"
**Solution:** Ensure you have a column with "date" in the name (e.g., "Invoice Date", "Date", "Order Date")

### Error: "Total/Amount column not found"
**Solution:** Include a column with "total", "amount", "sales", or "revenue" in the name

### Error: "Cannot parse dates"
**Solution:** 
- Check date format (DD/MM/YYYY or MM/DD/YYYY)
- Ensure dates are valid (not text like "TBD" or "N/A")
- No blank cells in date column

### Error: "Excel file structure not recognized"
**Solution:**
- Ensure weeks are columns (Week 1, Week 2, etc.)
- Branches are rows
- Sheet names are years or descriptive

### Warning: "Customer column not found"
**Solution:** Add a column with "Customer" or "Client" in the name (or accept placeholder values)

### Warning: "Column count mismatch"
**Solution:** This is usually OK - the dashboard adapts. Only concerning if you see errors loading data.

---

## ✅ Quick Checklist Before Upload

### CSV Files:
- [ ] Has header row with column names
- [ ] Contains Customer/Client column (or accept warning)
- [ ] Contains Date column (REQUIRED)
- [ ] Contains Total/Amount column (REQUIRED)
- [ ] Dates are in consistent format (DD/MM/YYYY or MM/DD/YYYY)
- [ ] Amount values are numeric
- [ ] No blank rows at top/bottom
- [ ] Saved as .csv file

### Excel Files:
- [ ] Saved as .xlsx or .xls
- [ ] Each sheet represents a year
- [ ] Weeks are columns (Week 1, Week 2, etc.)
- [ ] Branches are rows
- [ ] Values are numeric (no currency symbols in cells)
- [ ] Branch names match CSV files
- [ ] No blank rows/columns in data area

---

## 📞 Support

If you encounter issues:
1. Check this guide's error solutions
2. Review the **"Auto-Detected Configuration"** in the dashboard sidebar
3. Verify your file matches the acceptable examples
4. Check that required columns (Date, Total) are present

---

## 🎯 Summary: Minimum Requirements

**To use the dashboard, you MUST have:**

### CSV Files (Branch Data):
- ✅ At least 3 columns: Customer (or equivalent), Date, Amount
- ✅ Header row with column names
- ✅ CSV format (.csv)

### Excel File (Historical - Optional):
- ✅ One or more sheets (named by year)
- ✅ Branches as rows, weeks as columns
- ✅ Excel format (.xlsx or .xls)

**That's it! The dashboard handles the rest automatically.** 🎉

---

*The intelligent column mapping system makes the dashboard flexible to accept various column naming conventions. As long as your columns contain key words like "customer", "date", "total", "amount", etc., the system will detect and map them correctly.*
