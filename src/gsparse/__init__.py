"""Google Sheets Parser Library.

Library for extracting data from Google Sheets by URL.
Supports working with multiple worksheets in a single spreadsheet.
"""

import logging

from .client import GSParseClient
from .core.cell import Cell
from .core.range import Range
from .core.spreadsheet import Spreadsheet
from .core.worksheet import Worksheet
from .downloaders.google_sheets_downloader import GoogleSheetsDownloader
from .parsers.csv_parser import CSVParser

# Configure logging
logging.basicConfig(
	level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

__version__ = '0.2.1'
__all__ = [
	'Spreadsheet',
	'Worksheet',
	'Cell',
	'Range',
	'GoogleSheetsDownloader',
	'CSVParser',
	'GSParseClient',
	'logger',
]
