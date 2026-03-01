# Historical Sales Data Format Guide

## Overview
This guide explains the expected format for uploading historical sales data to the Annual Sales Analysis Dashboard.

## File Requirements

### File Type
- **Format**: Excel file (.xlsx or .xls)
- **Sheets Required**: Three separate sheets named:
  - `WA` (Western Australia)
  - `QLD` (Queensland)
  - `NSW` (New South Wales)

### Sheet Structure

Each sheet should follow this structure:

#### Row 1: Header Row 1 (Financial Years)
Contains the financial year labels (e.g., '18/19', '19/20', '20/21', etc.)

```
| Week No | 18/19 | 19/20 | 20/21 | 21/22 | 22/23 | ... |
```

#### Row 2: Header Row 2 (Optional sub-headers)
Can contain additional header information

#### Row 3 onwards: Data Rows
Contains weekly sales data:

```
| Week 1  | 125000 | 130000 | 145000 | 150000 | 155000 | ... |
| Week 2  | 128000 | 132000 | 148000 | 152000 | 158000 | ... |
| Week 3  | 130000 | 135000 | 150000 | 155000 | 160000 | ... |
| ...     | ...    | ...    | ...    | ...    | ...    | ... |
| Week 52 | 135000 | 140000 | 155000 | 160000 | 165000 | ... |
```

### Important Notes

1. **Week Identification**: 
   - First column must contain week identifiers in format "Week 1", "Week 2", etc.
   - Valid weeks: Week 1 through Week 52

2. **Financial Year Format**:
   - Use format 'YY/YY' (e.g., '18/19', '19/20')
   - Must contain a '/' character for proper identification

3. **Sales Values**:
   - Can include commas (e.g., "125,000")
   - Can be numbers without formatting
   - Avoid text or special characters in data cells

4. **Summary Rows**:
   - Rows like "Q1 Total", "Q2 Total", "Totals" will be automatically filtered out
   - Only rows containing "Week" followed by a number will be included

## Example Data Structure

### Sample WA Sheet:

| (blank)       | 18/19    | 19/20    | 20/21    | 21/22    |
|---------------|----------|----------|----------|----------|
| (sub-header)  | Sales    | Sales    | Sales    | Sales    |
| Week 1        | 125,000  | 130,000  | 145,000  | 150,000  |
| Week 2        | 128,000  | 132,000  | 148,000  | 152,000  |
| Week 3        | 130,000  | 135,000  | 150,000  | 155,000  |
| ...           | ...      | ...      | ...      | ...      |
| Week 13       | 135,000  | 140,000  | 155,000  | 160,000  |
| Q1 Total      | 1,690,000| 1,755,000| 1,950,000| 2,015,000|
| Week 14       | 140,000  | 145,000  | 160,000  | 165,000  |
| ...           | ...      | ...      | ...      | ...      |

## Dashboard Features

Once your historical data is uploaded, the dashboard will provide:

### 📈 Overview Tab
- Total sales across all years
- Average weekly sales
- Total weeks and financial years analyzed
- Year-over-year growth analysis
- Branch performance comparison

### 📊 Quarter Analysis Tab
- Quarterly sales summaries
- Quarter-by-quarter comparisons across years
- Branch-wise quarterly performance

### 📅 Week Analysis Tab
- Week-by-week sales trends
- Custom week range selection
- Quarter filtering options

### 📉 Comparative Analysis Tab
- Side-by-side year comparisons
- Week-by-week variance analysis
- Growth percentage calculations
- Detailed comparison tables

## Uploading Your File

1. Open the dashboard
2. Look for the sidebar on the left
3. Find the section "📊 Upload Historical Sales Data"
4. Click on the file uploader
5. Select your Excel file
6. The dashboard will automatically process and display your data

## Troubleshooting

### Common Issues:

1. **"Sheet not found" error**
   - Ensure your Excel file has sheets exactly named: WA, QLD, NSW
   - Sheet names are case-sensitive

2. **"No data loaded" message**
   - Check that your data starts from row 3 (rows 1-2 are headers)
   - Verify week labels contain "Week" followed by a number

3. **Missing data points**
   - Ensure all sales values are numeric
   - Remove any merged cells in the data area
   - Check for hidden rows that might contain invalid data

4. **Incorrect financial years**
   - Financial year labels must contain a '/' character
   - Use consistent format across all columns (e.g., 'YY/YY')

## Need Help?

If you encounter any issues:
1. Verify your Excel file follows the format specified above
2. Check that all three sheets (WA, QLD, NSW) are present
3. Ensure data is in the correct rows (data starting from row 3)
4. Look for any error messages in the dashboard for specific guidance
