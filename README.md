# Enterprise Application Capability Mapper

A local Streamlit app for importing L1-L3 business capability data from a semicolon-delimited CSV and rendering a layered capability map.

## Features

- Upload `;` delimited CSV with columns `A;B;C;D`
- Edit rows by adding or deleting entries
- Default sort on columns A, B, C in descending order
- Render a three-layer capability view:
  - L1 headline boxes
  - L2 grouped capability containers
  - L3 clickable capabilities linked to the URL in column D

## Run locally

Activate the virtual environment and start Streamlit:

```bash
source .venv/bin/activate
streamlit run app.py
```

## CSV format

The CSV should use semicolons as delimiters and contain at least four columns:

- `A` = L1 capability
- `B` = L2 capability
- `C` = L3 capability
- `D` = link or process diagram URL for L3

Example:

```csv
A;B;C;D
Corporate;Finance;Accounts payable;https://example.com/process1
Corporate;Finance;Accounts receivable;https://example.com/process2
Corporate;Sales;Order management;https://example.com/process3
```
