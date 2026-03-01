# Excel Historical Data Template Guide

## How to Create Your Historical Data Excel File

### File Structure:
1. **File Format:** Save as `.xlsx` (Excel Workbook)
2. **Sheet Names:** One sheet per year (e.g., "2023", "2024", "2025")
3. **Layout:** Branches as ROWS, Weeks as COLUMNS

---

## Example Sheet Structure

**Sheet Name:** `2024`

### Layout:
```
A1: Branch    B1: Week 1    C1: Week 2    D1: Week 3    E1: Week 4    ...    BA1: Week 52
A2: NSW       B2: 45000     C2: 48000     D2: 52000     E2: 47000             BA2: 50000
A3: QLD       B3: 38000     C3: 39000     D3: 41000     E3: 40000             BA3: 42000
A4: WA        B4: 25000     C4: 26000     D4: 28000     E4: 27000             BA4: 29000
A5: VIC       B5: 35000     C5: 36000     D5: 37000     E5: 38000             BA5: 39000
```

---

## Step-by-Step Instructions

### 1. Create New Excel File
- Open Microsoft Excel, Google Sheets, or LibreOffice Calc
- Create a new blank workbook

### 2. Set Up First Sheet
- Rename Sheet1 to the year (e.g., "2024")
- **Cell A1:** Type "Branch" (optional header)
- **Cell B1:** Type "Week 1"
- **Cell C1:** Type "Week 2"
- Continue until **Week 52** (or Week 53 if your year has 53 weeks)

### 3. Add Branch Names
- **Cell A2:** First branch name (e.g., "NSW")
- **Cell A3:** Second branch name (e.g., "QLD")
- **Cell A4:** Third branch name (e.g., "WA")
- Add more rows for additional branches

### 4. Fill in Sales Data
- **Cell B2:** Week 1 sales for NSW (e.g., 45000)
- **Cell C2:** Week 2 sales for NSW (e.g., 48000)
- Continue filling each week's sales for each branch
- **Format:** Numbers only (no $ signs, no commas in cells - Excel formatting will display them)

### 5. Add More Years (Optional)
- Right-click on sheet tab → Duplicate
- Rename to next year (e.g., "2025")
- Update the sales data for that year

### 6. Save File
- File → Save As
- Choose format: **Excel Workbook (.xlsx)**
- Name it: `historical_sales.xlsx` or similar

---

## ✅ Valid Structure Example

**Sheet: 2024**
```
           Week 1    Week 2    Week 3    Week 4    Week 5    ...    Week 52
NSW         45000     48000     52000     47000     49000            50000
QLD         38000     39000     41000     40000     42000            42000
WA          25000     26000     28000     27000     29000            29000
VIC         35000     36000     37000     38000     39000            39000
```

**Sheet: 2025**
```
           Week 1    Week 2    Week 3    Week 4    Week 5    ...    Week 52
NSW         50000     52000     54000     51000     53000            55000
QLD         42000     43000     45000     44000     46000            46000
WA          29000     30000     32000     31000     33000            33000
VIC         39000     40000     41000     42000     43000            43000
```

---

## ❌ Common Mistakes to Avoid

### WRONG Layout (Weeks as Rows, Branches as Columns):
```
Week       NSW      QLD      WA
1          45000    38000    25000
2          48000    39000    26000
```
**Problem:** Dashboard expects weeks as columns!

### WRONG Headers (No "Week" prefix):
```
           1         2         3         4
NSW        45000     48000     52000     47000
```
**Problem:** Column headers should be "Week 1", "Week 2", etc.

### WRONG Data Format (Text or Formulas):
```
           Week 1         Week 2
NSW        "$45,000"      =B2*1.1
```
**Problem:** Use numbers only (45000, not "$45,000")

---

## 📊 Sample Data to Test

If you want to test the dashboard, use these sample values:

**2024 Data (52 weeks):**
- NSW: Start at 45000, increase by 5-10% randomly each week
- QLD: Start at 38000, increase by 5-10% randomly each week
- WA: Start at 25000, increase by 5-10% randomly each week

**2025 Data (52 weeks):**
- NSW: Start at 50000, increase by 5-10% randomly each week
- QLD: Start at 42000, increase by 5-10% randomly each week
- WA: Start at 29000, increase by 5-10% randomly each week

---

## 🎯 Quick Checklist

- [ ] File saved as .xlsx format
- [ ] Each sheet named by year (2023, 2024, 2025)
- [ ] Header row: "Branch", "Week 1", "Week 2", ..., "Week 52"
- [ ] Branch names in column A (rows 2, 3, 4, etc.)
- [ ] Sales numbers in intersecting cells
- [ ] Numbers only (no currency symbols in cells)
- [ ] Branch names match your CSV file branches
- [ ] 52 or 53 week columns (depending on calendar year)

---

## 💡 Tips

1. **Excel Formatting:** You can format cells as Currency (with $ or ₹) for display, but the underlying value must be numeric
2. **Formulas Allowed:** You can use formulas (like SUM for totals) but they should resolve to numbers
3. **Empty Cells:** Avoid blank cells in the data range - use 0 if no sales that week
4. **Consistent Weeks:** All branches should have the same number of weeks (don't leave some branches with fewer weeks)
5. **Branch Matching:** Use exact same branch names as in your CSV files (NSW, not New South Wales)

---

## 🔍 How Dashboard Uses This Data

The historical Excel file enables:
- ✅ Year-over-year comparison in Annual Sales Dashboard
- ✅ Quarterly performance analysis (Q1, Q2, Q3, Q4)
- ✅ Historical trend visualization
- ✅ Compare current CSV data against historical Excel data

**Without this file:** Dashboard still works but only shows current CSV data analysis

---

## 📞 Need Help?

If you're unsure about your Excel structure:
1. Upload it to the dashboard
2. Check the "Auto-Detected Configuration" in sidebar
3. It will show detected sheets and week count
4. If it shows an error, revise based on this guide

---

**Remember:** The Excel file is OPTIONAL. If you only want current sales analysis, just upload CSV files!
