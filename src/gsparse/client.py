"""Main client for working with Google Sheets."""

import logging
from typing import Optional, Dict, Any, List
from .core.spreadsheet import Spreadsheet
from .core.worksheet import Worksheet
from .downloaders.google_sheets_downloader import GoogleSheetsDownloader
from .parsers.csv_parser import CSVParser
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
		self.parser = CSVParser()
	
	def load_spreadsheet(self, url: str) -> Spreadsheet:
		"""Loads and parses Google Sheets table.
		
		Args:
			url: Google Sheets table URL
			
		Returns:
			Spreadsheet object
			
		Raises:
			ValueError: If URL is invalid
			Exception: If loading or parsing error occurred
		"""
		if not URLUtils.is_google_sheets_url(url):
			raise ValueError(f"Невалидный URL Google Sheets: {url}")
		
		# Получаем информацию о листах
		worksheets_info = self.downloader.list_worksheets(url)
		
		if not worksheets_info:
			# Если не удалось получить информацию о листах, 
			# загружаем только первый лист
			data = self.downloader.download_sheet(url, "csv")
			worksheet = self.parser.parse(data, "Sheet1")
			return Spreadsheet(
				title="Imported Sheet",
				worksheets=[worksheet],
				url=url
			)
		
		# Загружаем все листы
		worksheets = []
		for sheet_name, gid in worksheets_info.items():
			try:
				data = self.downloader.download_sheet(url, "csv", gid)
				worksheet = self.parser.parse(data, sheet_name)
				worksheets.append(worksheet)
			except Exception as e:
				# Если не удалось загрузить лист, пропускаем его
				print(f"Предупреждение: не удалось загрузить лист '{sheet_name}': {e}")
				continue
		
		if not worksheets:
			raise Exception("Не удалось загрузить ни одного листа")
		
		return Spreadsheet(
			title=worksheets[0].name,
			worksheets=worksheets,
			url=url
		)
	
	def load_worksheet(self, url: str, worksheet_name: Optional[str] = None) -> Worksheet:
		"""Loads specific worksheet from Google Sheets.
		
		Args:
			url: Google Sheets table URL
			worksheet_name: Worksheet name (if None, loads first)
			
		Returns:
			Worksheet object
		"""
		spreadsheet = self.load_spreadsheet(url)
		
		if worksheet_name:
			worksheet = spreadsheet.get_worksheet(worksheet_name)
			if not worksheet:
				raise ValueError(f"Лист '{worksheet_name}' не найден")
			return worksheet
		else:
			first_worksheet = spreadsheet.get_first_worksheet()
			if not first_worksheet:
				raise ValueError("Таблица не содержит листов")
			return first_worksheet
	
	def load_from_csv_string(self, csv_string: str, worksheet_name: str = "Sheet1") -> Worksheet:
		"""Loads data from CSV string.
		
		Args:
			csv_string: CSV string
			worksheet_name: Worksheet name
			
		Returns:
			Worksheet object
		"""
		return self.parser.parse_from_string(csv_string, worksheet_name)
	
	def get_sheet_info(self, url: str) -> Dict[str, Any]:
		"""Gets information about the table.
		
		Args:
			url: Google Sheets table URL
			
		Returns:
			Dictionary with table information
		"""
		return self.downloader.get_sheet_info(url)
	
	def list_worksheets(self, url: str) -> Optional[Dict[str, str]]:
		"""Gets list of worksheets in the table.
		
		Args:
			url: Google Sheets table URL
			
		Returns:
			Dictionary {worksheet_name: gid} or None
		"""
		return self.downloader.list_worksheets(url)
	
	def export_to_dict(self, url: str, headers_row: int = 1) -> Dict[str, List[Dict[str, Any]]]:
		"""Exports table to dictionary.
		
		Args:
			url: Google Sheets table URL
			headers_row: Row number with headers
			
		Returns:
			Dictionary where keys are worksheet names, values are lists of dictionaries
		"""
		spreadsheet = self.load_spreadsheet(url)
		return spreadsheet.export_to_dict(headers_row)
	
	def find_data(self, url: str, value: Any) -> List[Any]:
		"""Finds all cells with specified value.
		
		Args:
			url: Google Sheets table URL
			value: Value to search for
			
		Returns:
			List of found cells
		"""
		spreadsheet = self.load_spreadsheet(url)
		return spreadsheet.find_cells_by_value(value)
	
	def find_by_pattern(self, url: str, pattern: str) -> List[Any]:
		"""Finds cells by regular expression.
		
		Args:
			url: Google Sheets table URL
			pattern: Regular expression
			
		Returns:
			List of found cells
		"""
		spreadsheet = self.load_spreadsheet(url)
		return spreadsheet.find_cells_by_pattern(pattern)
