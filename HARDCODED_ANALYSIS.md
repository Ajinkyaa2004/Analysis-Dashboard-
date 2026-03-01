# 🔍 Hardcoded Elements Analysis

## ✅ **NOT Hardcoded (Flexible)**

### 1. **CSV File Names** ✅
- **NOT hardcoded!** File names can be anything
- Uploaders are dynamically generated based on branch names
- You can name files: `sales_data.csv`, `2024_NSW.csv`, `anything.csv`

### 2. **Branch Names** ✅
- **NOT hardcoded!** Defaults to NSW, QLD, WA but fully configurable
- Auto-detects from Excel sheets
- Can be changed in Advanced Settings

### 3. **Number of Branches** ✅
- **NOT hardcoded!** Can have 2, 3, 5, 10 branches
- Dynamically creates file uploaders for each

### 4. **Column Count** ✅ (Partially)
- Auto-detects column count
- Works with 8, 10, 17, 18, 19, or any number of columns

## ❌ **STILL HARDCODED (Will Cause Errors)**

### 1. **Required Column Names** ❌ **CRITICAL ISSUE**

The code **REQUIRES** these exact column names to exist:
- `Customer` (line 287)
- `Issue Date` (line 292, 294)
- `Total` (line 298)

**Location:** [`app.py:287-300`](app.py#L287-L300)
```python
df['Customer'] = df['Customer'].astype(str).str.strip()  # ❌ Will fail if 'Customer' doesn't exist
df['Issue Date'] = pd.to_datetime(df['Issue Date'], ...)  # ❌ Will fail if 'Issue Date' doesn't exist  
df['Total'] = pd.to_numeric(df['Total'].astype(str)...) # ❌ Will fail if 'Total' doesn't exist
return df.dropna(subset=['Issue Date', 'Total', 'Branch'])
```

---

## 🧪 **Testing Your Scenarios**

### **Scenario 1: 8 Columns**
```
Entity Name, Branch Region, Branch, Division, Due Date, 
Top Level Customer ID, Top Level Customer Name, Customer ID
```

**Result:** ❌ **WILL FAIL**
- **Error:** `KeyError: 'Customer'` or `KeyError: 'Issue Date'` or `KeyError: 'Total'`
- **Reason:** These required columns don't exist in your file

---

### **Scenario 2: 10 Columns**
```
Entity Name, Branch Region, Branch, Division, Due Date, 
Top Level Customer ID, Top Level Customer Name, Customer ID, 
Customer, Billing Group ID
```

**Result:** ❌ **WILL FAIL**
- **Error:** `KeyError: 'Issue Date'` or `KeyError: 'Total'`
- **Reason:** Has 'Customer' ✅ but missing 'Issue Date' and 'Total'

---

### **Scenario 3: 17 Columns (Missing Status)**
```
Entity Name, Branch Region, Branch, Division, Due Date, 
Top Level Customer ID, Top Level Customer Name, Customer ID, 
Customer, Billing Group ID, Billing Group, Invoice ID, 
Invoice #, Issue Date, Total, Outstanding, Delivery
```

**Result:** ✅ **WILL WORK!**
- Has 'Customer' ✅
- Has 'Issue Date' ✅
- Has 'Total' ✅
- Missing 'Status' is OK (not required)
- **Auto-detects:** 17 columns, uses them without warning

---

### **Scenario 4: 18 Columns (Standard)**
```
Entity Name, Branch Region, Branch, Division, Due Date, 
Top Level Customer ID, Top Level Customer Name, Customer ID, 
Customer, Billing Group ID, Billing Group, Invoice ID, 
Invoice #, Issue Date, Total, Outstanding, Delivery, Status
```

**Result:** ✅ **WILL WORK PERFECTLY!**
- All required columns present
- Auto-detects perfectly

---

## 📊 **Summary Table**

| Scenario | Columns | Has Customer? | Has Issue Date? | Has Total? | Result |
|----------|---------|---------------|-----------------|------------|--------|
| Scenario 1 | 8 | ❌ | ❌ | ❌ | **FAIL** |
| Scenario 2 | 10 | ✅ | ❌ | ❌ | **FAIL** |
| Scenario 3 | 17 | ✅ | ✅ | ✅ | **WORKS** |
| Scenario 4 | 18 | ✅ | ✅ | ✅ | **WORKS** |

---

## 🚨 **Critical Requirements**

For the dashboard to work, your CSV files **MUST** have these columns:
1. ✅ **Customer** (or Customer ID, Customer Name, etc.)
2. ✅ **Issue Date** (or Date, Invoice Date, etc.)
3. ✅ **Total** (or Amount, Sales, etc.)

**All other columns are optional.**

---

## 🔧 **What Needs to Be Fixed**

To make it truly flexible, we need to:
1. **Column Mapping System** - Let users map their column names to required fields
2. **Smart Column Detection** - Auto-detect columns like:
   - "Customer ID" → maps to "Customer"
   - "Date", "Invoice Date" → maps to "Issue Date"
   - "Amount", "Sales" → maps to "Total"
3. **Fallback Values** - Create dummy values if columns don't exist

Would you like me to implement flexible column mapping?
