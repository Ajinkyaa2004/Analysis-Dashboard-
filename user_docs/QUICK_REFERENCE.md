# 🚀 Quick Reference Card

## CSV Files (Branch Sales)

### Must Have (3 columns minimum):
1. **Customer** → (Customer, Client, Customer Name, Client Name)
2. **Date** → (Date, Issue Date, Invoice Date, Order Date) - DD/MM/YYYY or MM/DD/YYYY
3. **Amount** → (Total, Amount, Sales, Revenue, Invoice Amount)

### Optional:
- Branch, Invoice No, Outstanding, Product, Quantity, etc.

---

## Excel File (Historical Sales)

### Structure:
- **Sheets:** One per year (e.g., "2023", "2024")
- **Layout:** Branches as ROWS, Weeks as COLUMNS
- **Format:** 
  ```
           Week 1    Week 2    Week 3
  NSW      45000     48000     52000
  QLD      38000     39000     41000
  WA       25000     26000     28000
  ```

---

## ✅ Valid CSV Examples

**Minimal (3 columns):**
```csv
Customer,Date,Total
ABC Ltd,15/01/2025,15000
XYZ Co,20/01/2025,25000
```

**With Options:**
```csv
Client Name,Invoice Date,Amount,Branch,Invoice No
ABC Ltd,15/01/2025,15000.50,NSW,INV-001
XYZ Co,20/01/2025,25000.00,QLD,INV-002
```

---

## ❌ Will NOT Work

- CSV without Date column
- CSV without Amount/Total column
- Excel with vertical layout (weeks as rows)
- Files without headers

---

## 🎯 Column Name Flexibility

The dashboard intelligently maps these variations:

| Required Field | Accepts Any Of |
|---------------|---------------|
| **Customer** | Customer, Client, Customer Name, Client Name, Cust |
| **Date** | Date, Issue Date, Invoice Date, Order Date, Sale Date |
| **Amount** | Total, Amount, Sales, Revenue, Invoice Amount |
| **Branch** | Branch, Location, Store, Office, Branch Name |
| **Invoice** | Invoice No, Invoice Number, Order No, Transaction ID |
| **Outstanding** | Outstanding, Due, Balance, Remaining, Unpaid |

---

## 🔍 Auto-Detected

You don't need to configure:
- ✅ Date format (DD/MM/YYYY vs MM/DD/YYYY)
- ✅ Currency symbol ($, ₹, €, £)
- ✅ Number of columns
- ✅ Branch names
- ✅ Excel sheets and weeks

---

## 🚨 Quick Errors

| Error Message | Fix |
|--------------|-----|
| "Date column not found" | Add column with "Date" in name |
| "Total column not found" | Add column with "Total" or "Amount" |
| "Cannot parse dates" | Use DD/MM/YYYY or MM/DD/YYYY format |
| "Excel structure not recognized" | Weeks must be columns, branches must be rows |

---

## ✅ Before Upload Checklist

**CSV:**
- [ ] Has headers
- [ ] Has Date column
- [ ] Has Amount/Total column
- [ ] Dates consistent format
- [ ] No blank rows

**Excel:**
- [ ] Weeks as columns
- [ ] Branches as rows
- [ ] Numeric values only
- [ ] Sheet per year

---

**See [USER_DATA_REQUIREMENTS.md](USER_DATA_REQUIREMENTS.md) for detailed guide.**
