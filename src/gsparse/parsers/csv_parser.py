"""Parser for CSV data."""

import csv
import io
import logging

from ..core.spreadsheet import Spreadsheet
from ..core.worksheet import Worksheet
from .base_parser import BaseParser

logger = logging.getLogger(__name__)


class CSVParser(BaseParser):
	"""Parser for CSV data from Google Sheets."""

	def __init__(
		self, delimiter: str = ',', quotechar: str = '"', encoding: str | None = None
	):
		"""Initialize parser.

		Args:
			delimiter: Field delimiter
			quotechar: Quote character
			encoding: Encoding (if None, auto-detected)
		"""
		self.delimiter = delimiter
		self.quotechar = quotechar
		self.encoding = encoding

	def parse(self, data: bytes, worksheet_name: str = 'Sheet1') -> Worksheet:
		"""Parses CSV data and returns Worksheet.

		Args:
			data: CSV data bytes
			worksheet_name: Worksheet name

		Returns:
			Worksheet object
		"""
		# Detect encoding if not specified
		encoding = self.encoding or self._detect_encoding(data)

		try:
			# Decode data
			text_data = data.decode(encoding)
		except UnicodeDecodeError:
			# If decoding failed, try other encodings
			for fallback_encoding in ['utf-8', 'cp1251', 'latin-1', 'utf-16']:
				try:
					text_data = data.decode(fallback_encoding)
					logger.debug(f'Successfully decoded with {fallback_encoding}')
					break
				except UnicodeDecodeError:
					continue
			else:
				raise ValueError('Failed to decode data with any supported encoding')

		# Auto-detect quote character if not explicitly set
		quotechar = self.quotechar
		if quotechar == '"':  # Only auto-detect if using default
			quotechar = self._detect_quote_char(text_data)

		# Parse CSV
		csv_reader = csv.reader(
			io.StringIO(text_data), delimiter=self.delimiter, quotechar=quotechar
		)

		# Read all rows
		rows = list(csv_reader)

		if not rows:
			# If no data, create empty worksheet
			return Worksheet(name=worksheet_name, data=[], row_count=0, column_count=0)

		# Clean data
		cleaned_rows = []
		for row in rows:
			cleaned_row = [self._clean_cell_value(cell) for cell in row]
			cleaned_rows.append(cleaned_row)

		# Determine dimensions
		row_count = len(cleaned_rows)
		column_count = max(len(row) for row in cleaned_rows) if cleaned_rows else 0

		# Normalize rows (pad with empty values to same length)
		normalized_rows = []
		for row in cleaned_rows:
			normalized_row = row + [None] * (column_count - len(row))
			normalized_rows.append(normalized_row)

		return Worksheet(
			name=worksheet_name,
			data=normalized_rows,
			row_count=row_count,
			column_count=column_count,
		)

	def parse_multiple(self, data_dict: dict[str, bytes]) -> Spreadsheet:
		"""Parses multiple CSV files and returns Spreadsheet.

		Args:
			data_dict: Dictionary {worksheet_name: CSV_data}

		Returns:
			Spreadsheet object
		"""
		worksheets = []

		for worksheet_name, data in data_dict.items():
			worksheet = self.parse(data, worksheet_name)
			worksheets.append(worksheet)

		# Use first worksheet name as spreadsheet title
		title = list(data_dict.keys())[0] if data_dict else 'Untitled'

		return Spreadsheet(title=title, worksheets=worksheets)

	def parse_from_string(
		self, csv_string: str, worksheet_name: str = 'Sheet1'
	) -> Worksheet:
		"""Parses CSV data from string.

		Args:
			csv_string: CSV string
			worksheet_name: Worksheet name

		Returns:
			Worksheet object
		"""
		return self.parse(csv_string.encode('utf-8'), worksheet_name)

	def _detect_quote_char(self, text_data: str) -> str:
		"""Automatically detects quote character in CSV data.

		Args:
			text_data: CSV text data

		Returns:
			Detected quote character
		"""
		# Read first few lines for analysis
		lines = text_data.split('\n')[:5]

		# Count frequency of different quote characters
		quote_chars = ['"', "'", '`']
		quote_counts = {}

		for quote_char in quote_chars:
			count = 0
			for line in lines:
				if line.strip():
					# Count occurrences where quote appears at start/end of fields
					# Look for patterns like 'value' or "value"
					import re

					pattern = f'^{re.escape(quote_char)}.*{re.escape(quote_char)}$'
					fields = line.split(self.delimiter)
					for field in fields:
						field = field.strip()
						if re.match(pattern, field):
							count += 1
			quote_counts[quote_char] = count

		# Return quote character with highest frequency, default to double quotes
		return (
			max(quote_counts, key=lambda x: quote_counts[x])
			if any(quote_counts.values())
			else '"'
		)

	def detect_delimiter(self, data: bytes) -> str:
		"""Automatically detects delimiter in CSV data.

		Args:
			data: CSV data bytes

		Returns:
			Found delimiter
		"""
		encoding = self.encoding or self._detect_encoding(data)
		text_data = data.decode(encoding)

		# Read first few lines for analysis
		lines = text_data.split('\n')[:5]

		# Count frequency of different delimiters
		delimiters = [',', ';', '\t', '|']
		delimiter_counts = {}

		for delimiter in delimiters:
			count = 0
			for line in lines:
				if line.strip():
					count += line.count(delimiter)
			delimiter_counts[delimiter] = count

		# Return delimiter with highest frequency
		return max(delimiter_counts, key=lambda x: delimiter_counts[x])
