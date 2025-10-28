"""Base class for parsers."""

import logging
from abc import ABC, abstractmethod
from typing import Any

from ..core.spreadsheet import Spreadsheet
from ..core.worksheet import Worksheet

logger = logging.getLogger(__name__)


class BaseParser(ABC):
	"""Base class for all parsers."""

	def __init__(self, preserve_strings: bool = False):
		"""Initialize parser.

		Args:
			preserve_strings: If True, all values will be kept as strings without type conversion
		"""
		self.preserve_strings = preserve_strings

	@abstractmethod
	def parse(self, data: bytes, worksheet_name: str = 'Sheet1') -> Worksheet:
		"""Parses data and returns Worksheet.

		Args:
			data: Data bytes to parse
			worksheet_name: Worksheet name

		Returns:
			Worksheet object
		"""
		pass

	@abstractmethod
	def parse_multiple(self, data_dict: dict[str, bytes]) -> Spreadsheet:
		"""Parses multiple data sets and returns Spreadsheet.

		Args:
			data_dict: Dictionary {worksheet_name: data}

		Returns:
			Spreadsheet object
		"""
		pass

	def _clean_cell_value(self, value: Any) -> Any:
		"""Cleans cell value from extra characters.

		Args:
			value: Original value

		Returns:
			Cleaned value
		"""
		if value is None:
			return None

		if isinstance(value, str):
			# Remove extra spaces and line breaks
			cleaned = value.strip().replace('\r\n', '\n').replace('\r', '\n')
			# If string is empty after cleaning, return None
			if not cleaned:
				return None

			# Check if this looks like a date string (DD,MM or DD.MM format)
			if self._is_potential_date_string(cleaned):
				return self._format_date_string(cleaned)

			return cleaned

		# Handle potential date values that come as floats
		if isinstance(value, (int, float)):
			# Check if this looks like a date (e.g., 28.1, 1.1, 31.12)
			if self._is_potential_date_float(value):
				return self._format_date_float(value)

		# If preserve_strings is True, convert all values to strings
		if self.preserve_strings:
			return str(value) if value is not None else None

		return value

	def _detect_encoding(self, data: bytes) -> str:
		"""Detects data encoding.

		Args:
			data: Data bytes

		Returns:
			Encoding name
		"""
		import chardet

		# Try to detect encoding
		result = chardet.detect(data)
		encoding = result.get('encoding', 'utf-8')
		confidence = result.get('confidence', 0)

		# If confidence is low, use utf-8 by default
		if confidence < 0.7:
			encoding = 'utf-8'

		return encoding

	def _is_potential_date_float(self, value: float) -> bool:
		"""Check if float value looks like a date in DD.MM format.

		Args:
			value: Float value to check

		Returns:
			True if value looks like a date
		"""
		if not isinstance(value, (int, float)):
			return False

		# Convert to string to check format
		str_value = str(value)

		# Check if it has decimal point and looks like DD.M or DD.MM
		if '.' in str_value:
			parts = str_value.split('.')
			if len(parts) == 2:
				day_part = parts[0]
				month_part = parts[1]

				# Check if day is 1-31 and month is 1-12
				try:
					day = int(day_part)
					month = int(month_part)
					return 1 <= day <= 31 and 1 <= month <= 12
				except ValueError:
					return False

		return False

	def _format_date_float(self, value: float) -> str:
		"""Format float value as date string preserving original format.

		Args:
			value: Float value representing date

		Returns:
			Formatted date string
		"""
		str_value = str(value)

		if '.' in str_value:
			parts = str_value.split('.')
			if len(parts) == 2:
				day_part = parts[0]
				month_part = parts[1]

				# Special handling for dates that might have lost trailing zeros
				# If month is single digit and day is 28-31, it might be 28.10 -> 28.1
				day = int(day_part)
				month = int(month_part)

				# Check if this could be a date that lost trailing zero
				# Common patterns: 28.1 could be 28.10, 29.1 could be 29.10, etc.
				if day >= 28 and month == 1:
					# This is likely 28.10, 29.10, 30.10, or 31.10 that became 28.1, 29.1, 30.1, 31.1
					return f'{day_part}.10'
				elif day >= 1 and day <= 9 and month == 1:
					# This could be 1.10, 2.10, etc. that became 1.1, 2.1, etc.
					return f'{day_part}.10'
				else:
					# Keep as is
					return f'{day_part}.{month_part}'

		return str_value

	def _is_potential_date_string(self, value: str) -> bool:
		"""Check if string value looks like a date in DD,MM or DD.MM format.

		Args:
			value: String value to check

		Returns:
			True if value looks like a date
		"""
		if not isinstance(value, str):
			return False

		# Check for DD,MM or DD.MM format
		if ',' in value or '.' in value:
			separator = ',' if ',' in value else '.'
			parts = value.split(separator)
			if len(parts) == 2:
				day_part = parts[0].strip()
				month_part = parts[1].strip()

				# Check if day is 1-31 and month is 1-12
				try:
					day = int(day_part)
					month = int(month_part)
					return 1 <= day <= 31 and 1 <= month <= 12
				except ValueError:
					return False

		return False

	def _format_date_string(self, value: str) -> str:
		"""Format string value as date string preserving original format.

		Args:
			value: String value representing date

		Returns:
			Formatted date string
		"""
		if ',' in value:
			# Convert DD,MM to DD.MM format
			return value.replace(',', '.')
		return value
