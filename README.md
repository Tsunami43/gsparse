# GSParse

[![PyPI version](https://img.shields.io/pypi/v/gsparse?color=green)](https://pypi.org/project/gsparse/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

**GSParse** is a lightweight library for extracting data from **public Google Sheets** by URL — no API keys, no OAuth, no service accounts. It downloads a spreadsheet's export, parses every worksheet, and gives you a clean, convenient API for cells, rows, columns, ranges, search, and export.

```python
from gsparse import GSParseClient

client = GSParseClient()
spreadsheet = client.load_spreadsheet("https://docs.google.com/spreadsheets/d/<SHEET_ID>/edit")

for worksheet in spreadsheet:
    print(worksheet.name, worksheet.row_count, "x", worksheet.column_count)
```

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
  - [Loading data](#loading-data)
  - [Worksheets](#worksheets)
  - [Cells and ranges](#cells-and-ranges)
  - [Exporting to dictionaries](#exporting-to-dictionaries)
  - [Searching](#searching)
  - [Cleaning data](#cleaning-data)
  - [Parsing from a CSV string](#parsing-from-a-csv-string)
- [API Reference](#api-reference)
- [Notes & Limitations](#notes--limitations)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- 📊 Reads **all worksheets** of a spreadsheet in one call (XLSX)
- 🔗 Loads directly by Google Sheets URL — no credentials required
- 🧩 Convenient object model: `Spreadsheet` → `Worksheet` → `Cell` / `Range`
- 🔍 Search by exact value or regular expression
- 📋 Export worksheets to lists of dictionaries (records)
- 🧹 Helpers to strip empty rows/columns
- 🔤 Optional `preserve_strings` mode to keep every value as text
- 🔄 Automatic retries and encoding auto-detection
- ⚡ Supports both XLSX (default) and CSV formats

## Installation

```bash
pip install gsparse
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add gsparse
```

**Requirements:** Python ≥ 3.10 · `requests` · `chardet` · `openpyxl`

## Quick Start

```python
from gsparse import GSParseClient

client = GSParseClient()

url = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit"
spreadsheet = client.load_spreadsheet(url)

# Inspect the workbook
print("Title:", spreadsheet.title)
print("Sheets:", spreadsheet.worksheet_names)

# Grab the first worksheet
worksheet = spreadsheet.get_first_worksheet()

# Read a single cell (1-based coordinates)
cell = worksheet.get_cell(1, 1)  # A1
print(cell.address, "=", cell.value)

# Export rows as dictionaries (first row is used as headers)
for row in worksheet.get_data_as_dict():
    print(row)
```

## Usage

### Loading data

```python
# Load the whole spreadsheet (XLSX — reads every worksheet)
spreadsheet = client.load_spreadsheet(url)

# Load a single worksheet by name
worksheet = client.load_worksheet(url, "Sheet1")

# Load the first worksheet
worksheet = client.load_worksheet(url)
```

By default values keep their native types (numbers stay numbers). Pass
`preserve_strings=True` to the client if you want every cell returned as a string:

```python
client = GSParseClient(preserve_strings=True)
```

### Worksheets

```python
spreadsheet.worksheet_count          # number of sheets
spreadsheet.worksheet_names          # ["Sheet1", "Data", ...]

spreadsheet.get_worksheet("Data")    # by name (or None)
spreadsheet.get_worksheet_by_index(0)
spreadsheet.get_first_worksheet()
spreadsheet.get_last_worksheet()

# Dict-like and iterable access
sheet = spreadsheet["Data"]
if "Data" in spreadsheet:
    ...
for sheet in spreadsheet:
    print(sheet.name)
```

### Cells and ranges

```python
worksheet = spreadsheet.get_first_worksheet()

# Single cell (row, column), both starting at 1
cell = worksheet.get_cell(2, 3)      # C2
print(cell.address, cell.value, cell.is_empty)

# A range: get_range(start_row, end_row, start_column, end_column)
rng = worksheet.get_range(1, 10, 1, 3)          # A1:C10
cells = worksheet.get_cells_in_range(rng)

# ...or build a range from an A1 address
rng = worksheet.get_range_by_address("A1:C10")

# Whole rows / columns
first_row = worksheet.get_row(1)
first_col = worksheet.get_column(1)

# Raw values as lists of lists
rows = worksheet.get_rows()
columns = worksheet.get_columns()
```

### Exporting to dictionaries

```python
# A single worksheet -> list of records
records = worksheet.get_data_as_dict(headers_row=1)

# Every worksheet at once -> {sheet_name: [records, ...]}
data = spreadsheet.export_to_dict(headers_row=1)

# Straight from a URL
data = client.export_to_dict(url, headers_row=1)
```

### Searching

```python
# Exact value across all worksheets
cells = client.find_data(url, "Moscow")

# Regular expression
numbers = client.find_by_pattern(url, r"^\d+$")

# Or on already-loaded objects
worksheet.find_cells_by_value("Moscow")
worksheet.find_cells_by_pattern(r"@\w+\.\w+")     # emails
spreadsheet.find_cells_by_value(42)
```

### Cleaning data

```python
# Return a new, cleaned worksheet (originals untouched)
clean = worksheet.remove_empty_rows()
clean = worksheet.remove_empty_columns()
clean = worksheet.clean_data()                     # both

# ...or mutate in place
worksheet.clean_data_inplace()
```

### Parsing from a CSV string

Useful for tests or data you already have in memory. The delimiter is auto-detected:

```python
csv_data = """Name,Age,City
John,25,Moscow
Mary,30,St. Petersburg"""

worksheet = client.load_from_csv_string(csv_data, "My Data")
print(worksheet.get_data_as_dict())
```

## API Reference

### `GSParseClient(timeout=30, max_retries=3, preserve_strings=False)`

| Method | Description |
| --- | --- |
| `load_spreadsheet(url, format_type="xlsx")` | Load the whole spreadsheet |
| `load_worksheet(url, worksheet_name=None, format_type="xlsx")` | Load one worksheet (first if name is `None`) |
| `load_from_csv_string(csv_string, worksheet_name="Sheet1")` | Parse a worksheet from a CSV string |
| `export_to_dict(url, headers_row=1, format_type="xlsx")` | Export all worksheets to records |
| `find_data(url, value, format_type="xlsx")` | Find cells by exact value |
| `find_by_pattern(url, pattern, format_type="xlsx")` | Find cells by regular expression |
| `get_sheet_info(url)` | Basic info about the spreadsheet |
| `list_worksheets(url)` | Map of `{worksheet_name: gid}` |

### `Spreadsheet`

**Properties:** `title`, `worksheets`, `url`, `worksheet_count`, `worksheet_names`

**Methods:** `get_worksheet(name)`, `get_worksheet_by_index(index)`, `get_first_worksheet()`, `get_last_worksheet()`, `add_worksheet(ws)`, `remove_worksheet(name)`, `get_all_cells()`, `get_data_summary()`, `find_cells_by_value(value)`, `find_cells_by_pattern(pattern)`, `export_to_dict(headers_row=1)`

Also supports iteration (`for ws in spreadsheet`), membership (`name in spreadsheet`) and indexing (`spreadsheet[name]`).

### `Worksheet`

**Properties:** `name`, `data`, `row_count`, `column_count`

**Methods:** `get_cell(row, column)`, `get_range(start_row, end_row, start_column, end_column)`, `get_range_by_address(address)`, `get_all_cells()`, `get_cells_in_range(range_obj)`, `get_row(n)`, `get_column(n)`, `get_rows()`, `get_columns()`, `get_data_as_dict(headers_row=1)`, `find_cells_by_value(value)`, `find_cells_by_pattern(pattern)`, `remove_empty_rows()`, `remove_empty_columns()`, `clean_data()` (plus `*_inplace()` variants)

### `Cell`

**Properties:** `row`, `column`, `value`, `formatted_value`, `formula`, `address` (e.g. `"B2"`), `is_empty`

### `Range`

**Properties:** `start_row`, `end_row`, `start_column`, `end_column`, `worksheet_name`, `address`, `row_count`, `column_count`, `cell_count`

**Methods:** `contains_cell(row, column)`, `get_cells(data)`, `Range.from_address("Sheet1!A1:B2")`

## Notes & Limitations

- **The spreadsheet must be publicly accessible** ("Anyone with the link"). GSParse reads the public export endpoint and does not authenticate.
- **All coordinates are 1-based** — `get_cell(1, 1)` is `A1`.
- **Prefer XLSX** (the default): it reads every worksheet. The `csv` format is **deprecated** — Google's CSV export only returns a single sheet, so it emits a `DeprecationWarning`.
- If an XLSX download fails, the client automatically falls back to CSV.

## Development

```bash
# Install the project with its dev dependency group
uv sync                     # installs the "dev" group by default

# Run the test suite
uv run pytest               # or just: pytest

# Lint
uv run ruff check src/      # or just: ruff check src/
```

> Using plain `pip`? Install the package in editable mode and add the tools
> manually: `pip install -e . pytest ruff` (the dev tools live in a PEP 735
> `[dependency-groups]` block, which `uv sync` picks up automatically).

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request on
[GitHub](https://github.com/Tsunami43/gsparse).

## License

Released under the [MIT License](LICENSE).
