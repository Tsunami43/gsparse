# GSParse - Google Sheets Parser Library

Library for extracting data from Google Sheets by URL. Supports working with multiple worksheets in a single spreadsheet.

## Features

- 📊 Working with multiple worksheets in a single spreadsheet
- 🔗 Loading data by Google Sheets URL
- 📝 Parsing CSV data from buffer
- 🎯 Convenient API for working with cells and ranges
- 🔍 Data search by value or regular expression
- 📋 Export to various formats

## Installation

```bash
pip install -e .
```

## Quick Start

### Basic Usage

```python
from gsparse import GSParseClient

# Create client
client = GSParseClient()

# Load spreadsheet by URL
url = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit"
spreadsheet = client.load_spreadsheet(url)

# Get first worksheet
worksheet = spreadsheet.get_first_worksheet()

# Work with cells
cell = worksheet.get_cell(1, 1)  # A1
print(f"Cell A1 value: {cell.value}")

# Get range
range_obj = worksheet.get_range(1, 10, 1, 3)  # A1:C10
cells = worksheet.get_cells_in_range(range_obj)
```

### Working with CSV Data

```python
# Load from CSV string
csv_data = """Name,Age,City
John,25,Moscow
Mary,30,St. Petersburg"""

worksheet = client.load_from_csv_string(csv_data, "My Data")

# Export to dictionary
data_dict = worksheet.get_data_as_dict()
for row in data_dict:
    print(row)
```

### Data Search

```python
# Search by value
found_cells = client.find_data(url, "Moscow")

# Search by regular expression
pattern_cells = client.find_by_pattern(url, r"^\d+$")  # numbers only
```

## API Reference

### GSParseClient

Main class for working with the library.

#### Methods

- `load_spreadsheet(url)` - Loads entire spreadsheet
- `load_worksheet(url, worksheet_name)` - Loads specific worksheet
- `load_from_csv_string(csv_string, worksheet_name)` - Loads from CSV string
- `find_data(url, value)` - Search cells by value
- `find_by_pattern(url, pattern)` - Search by regular expression

### Spreadsheet

Represents Google Sheets table with multiple worksheets.

#### Properties

- `title` - Spreadsheet title
- `worksheets` - List of worksheets
- `worksheet_count` - Number of worksheets

#### Methods

- `get_worksheet(name)` - Get worksheet by name
- `get_worksheet_by_index(index)` - Get worksheet by index
- `export_to_dict(headers_row)` - Export all worksheets to dictionary

### Worksheet

Represents worksheet in spreadsheet.

#### Properties

- `name` - Worksheet name
- `row_count` - Number of rows
- `column_count` - Number of columns

#### Methods

- `get_cell(row, column)` - Get cell
- `get_range(start_row, end_row, start_column, end_column)` - Get range
- `get_data_as_dict(headers_row)` - Export to dictionary
- `find_cells_by_value(value)` - Search cells by value

### Cell

Represents cell in spreadsheet.

#### Properties

- `row` - Row number
- `column` - Column number
- `value` - Cell value
- `address` - Cell address (A1, B2, etc.)
- `is_empty` - Whether cell is empty

## Project Structure

```
src/gsparse/
├── __init__.py              # Main module
├── client.py                # Main client
├── core/                    # Core entities
│   ├── cell.py             # Cell
│   ├── range.py            # Cell range
│   ├── worksheet.py        # Worksheet
│   └── spreadsheet.py      # Spreadsheet
├── downloaders/            # Downloaders
│   └── google_sheets_downloader.py
├── parsers/                # Parsers
│   ├── base_parser.py      # Base parser
│   └── csv_parser.py       # CSV parser
└── utils/                  # Utilities
    ├── url_utils.py        # URL handling
    └── data_utils.py       # Data processing
```

## Requirements

- Python >= 3.10
- requests >= 2.31.0
- chardet >= 5.2.0

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Code check
ruff check src/
```

## License

MIT License
