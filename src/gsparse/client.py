"""Main client for working with Google Sheets."""

import logging
import warnings
from typing import Any

from .core.spreadsheet import Spreadsheet
from .core.worksheet import Worksheet
from .downloaders.google_sheets_downloader import GoogleSheetsDownloader
from .parsers.csv_parser import CSVParser
from .parsers.xlsx_parser import XLSXParser
from .utils.url_utils import URLUtils

logger = logging.getLogger(__name__)


class GSParseClient:
	"""Main client for working with Google Sheets.

	Provides convenient interface for loading and parsing Google Sheets.
	"""

	def __init__(self, timeout: int = 30, max_retries: int = 3):
		"""Initialize client.

		Args:
			timeout: Request timeout in seconds
			max_retries: Maximum number of retry attempts
		"""
		self.downloader = GoogleSheetsDownloader(timeout, max_retries)
		self.csv_parser = CSVParser()
		self.xlsx_parser = XLSXParser()

	def load_spreadsheet(self, url: str, format_type: str = 'xlsx') -> Spreadsheet:
		"""Loads and parses Google Sheets table.

		Args:
			url: Google Sheets table URL
			format_type: Export format type ("xlsx" or "csv")

		Returns:
			Spreadsheet object

		Raises:
			ValueError: If URL is invalid
			Exception: If loading or parsing error occurred
		"""
		if not URLUtils.is_google_sheets_url(url):
			raise ValueError(f'Invalid Google Sheets URL: {url}')

		# Show deprecation warning for CSV format
		if format_type == 'csv':
			warnings.warn(
				"CSV format is deprecated as it only downloads the current sheet. Use 'xlsx' format instead.",
				DeprecationWarning,
				stacklevel=2,
			)

		if format_type == 'xlsx':
			# For XLSX, download the entire workbook and parse all sheets
			try:
				data = self.downloader.download_sheet(url, 'xlsx')
				spreadsheet = self.xlsx_parser.parse_workbook(data)
				spreadsheet.url = url
				return spreadsheet
			except Exception as e:
				# Fallback to CSV if XLSX fails
				logger.warning(f'XLSX download failed, falling back to CSV: {e}')
				format_type = 'csv'

		# For CSV format (or fallback)
		worksheets_info = self.downloader.list_worksheets(url)

		if not worksheets_info:
			# If unable to get worksheet info, load only the first sheet
			data = self.downloader.download_sheet(url, 'csv')
			worksheet = self.csv_parser.parse(data, 'Sheet1')
			return Spreadsheet(title='Imported Sheet', worksheets=[worksheet], url=url)

		# Load all worksheets
		worksheets = []
		for sheet_name, gid in worksheets_info.items():
			try:
				data = self.downloader.download_sheet(url, 'csv', gid)
				worksheet = self.csv_parser.parse(data, sheet_name)
				worksheets.append(worksheet)
			except Exception as e:
				# If unable to load worksheet, skip it
				print(f"Warning: failed to load worksheet '{sheet_name}': {e}")
				continue

		if not worksheets:
			raise Exception('Failed to load any worksheets')

		return Spreadsheet(title=worksheets[0].name, worksheets=worksheets, url=url)

	def load_worksheet(
		self, url: str, worksheet_name: str | None = None, format_type: str = 'xlsx'
	) -> Worksheet:
		"""Loads specific worksheet from Google Sheets.

		Args:
			url: Google Sheets table URL
			worksheet_name: Worksheet name (if None, loads first)
			format_type: Export format type ("xlsx" or "csv")

		Returns:
			Worksheet object
		"""
		spreadsheet = self.load_spreadsheet(url, format_type)

		if worksheet_name:
			worksheet = spreadsheet.get_worksheet(worksheet_name)
			if not worksheet:
				raise ValueError(f"Worksheet '{worksheet_name}' not found")
			return worksheet
		else:
			first_worksheet = spreadsheet.get_first_worksheet()
			if not first_worksheet:
				raise ValueError('Spreadsheet contains no worksheets')
			return first_worksheet

	def load_from_csv_string(
		self, csv_string: str, worksheet_name: str = 'Sheet1'
	) -> Worksheet:
		"""Loads data from CSV string.

		Args:
			csv_string: CSV string
			worksheet_name: Worksheet name

		Returns:
			Worksheet object
		"""
		# Detect delimiter automatically
		detected_delimiter = self.csv_parser.detect_delimiter(
			csv_string.encode('utf-8')
		)

		# Create parser with detected delimiter
		parser = CSVParser(delimiter=detected_delimiter)

		return parser.parse_from_string(csv_string, worksheet_name)

	def get_sheet_info(self, url: str) -> dict[str, Any]:
		"""Gets information about the table.

		Args:
			url: Google Sheets table URL

		Returns:
			Dictionary with table information
		"""
		return self.downloader.get_sheet_info(url)

	def list_worksheets(self, url: str) -> dict[str, str] | None:
		"""Gets list of worksheets in the table.

		Args:
			url: Google Sheets table URL

		Returns:
			Dictionary {worksheet_name: gid} or None
		"""
		return self.downloader.list_worksheets(url)

	def export_to_dict(
		self, url: str, headers_row: int = 1, format_type: str = 'xlsx'
	) -> dict[str, list[dict[str, Any]]]:
		"""Exports table to dictionary.

		Args:
			url: Google Sheets table URL
			headers_row: Row number with headers
			format_type: Export format type ("xlsx" or "csv")

		Returns:
			Dictionary where keys are worksheet names, values are lists of dictionaries
		"""
		spreadsheet = self.load_spreadsheet(url, format_type)
		return spreadsheet.export_to_dict(headers_row)

	def find_data(self, url: str, value: Any, format_type: str = 'xlsx') -> list[Any]:
		"""Finds all cells with specified value.

		Args:
			url: Google Sheets table URL
			value: Value to search for
			format_type: Export format type ("xlsx" or "csv")

		Returns:
			List of found cells
		"""
		spreadsheet = self.load_spreadsheet(url, format_type)
		return spreadsheet.find_cells_by_value(value)

	def find_by_pattern(
		self, url: str, pattern: str, format_type: str = 'xlsx'
	) -> list[Any]:
		"""Finds cells by regular expression.

		Args:
			url: Google Sheets table URL
			pattern: Regular expression
			format_type: Export format type ("xlsx" or "csv")

		Returns:
			List of found cells
		"""
		spreadsheet = self.load_spreadsheet(url, format_type)
		return spreadsheet.find_cells_by_pattern(pattern)
