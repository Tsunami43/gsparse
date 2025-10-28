"""Utilities for working with data."""

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


class DataUtils:
	"""Utilities for processing data from Google Sheets."""

	@staticmethod
	def clean_value(value: Any) -> Any:
		"""Cleans value from extra characters.

		Args:
		    value: Original value

		Returns:
		    Cleaned value
		"""
		if value is None:
			return None

		if isinstance(value, str):
			# Decode Unicode escape sequences first
			decoded = DataUtils._decode_unicode_escapes(value)

			# Remove extra spaces and line breaks
			cleaned = decoded.strip().replace('\r\n', '\n').replace('\r', '\n')
			# If string is empty after cleaning, return None
			return cleaned if cleaned else None

		return value

	@staticmethod
	def _decode_unicode_escapes(text: str) -> str:
		"""Decodes Unicode escape sequences in text.

		Args:
		    text: Text that may contain Unicode escape sequences

		Returns:
		    Text with decoded Unicode characters
		"""
		if not isinstance(text, str):
			return text

		# Check if text contains Unicode escape sequences
		if '\\U' in text or '\\u' in text:
			import re

			# Use regex to find and replace Unicode escape sequences
			def replace_unicode_escape(match):
				escape_seq = match.group(0)
				try:
					# Decode only the escape sequence, not the whole string
					decoded_char = escape_seq.encode().decode('unicode_escape')
					return decoded_char
				except Exception:
					return escape_seq  # Return original if decoding fails

			# Pattern for Unicode escape sequences
			unicode_pattern = r'\\U[0-9a-fA-F]{8}|\\u[0-9a-fA-F]{4}'
			result = re.sub(unicode_pattern, replace_unicode_escape, text)

			logger.debug(f'Decoded Unicode escapes: {text[:50]}... -> {result[:50]}...')
			return result

		return text

	@staticmethod
	def convert_to_number(value: Any) -> int | float | None:
		"""Attempts to convert value to number.

		Args:
		    value: Value to convert

		Returns:
		    Number or None if conversion failed
		"""
		if value is None:
			return None

		if isinstance(value, (int, float)):
			return value

		if isinstance(value, str):
			# Remove spaces
			cleaned = value.strip()
			if not cleaned:
				return None

			# Try to convert to int
			try:
				return int(cleaned)
			except ValueError:
				pass

			# Try to convert to float
			try:
				return float(cleaned)
			except ValueError:
				pass

		return None

	@staticmethod
	def convert_to_boolean(value: Any) -> bool | None:
		"""Attempts to convert value to boolean.

		Args:
		    value: Value to convert

		Returns:
		    Boolean value or None if conversion failed
		"""
		if value is None:
			return None

		if isinstance(value, bool):
			return value

		if isinstance(value, str):
			cleaned = value.strip().lower()
			if cleaned in ['true', '1', 'yes']:
				return True
			elif cleaned in ['false', '0', 'no']:
				return False

		return None

	@staticmethod
	def detect_data_type(column_data: list[Any]) -> str:
		"""Detects data type in column.

		Args:
		    column_data: List of column values

		Returns:
		    Data type: 'number', 'boolean', 'date', 'text'
		"""
		if not column_data:
			return 'text'

		# Count types
		type_counts = {'number': 0, 'boolean': 0, 'date': 0, 'text': 0}

		for value in column_data:
			if value is None:
				continue

			if DataUtils.convert_to_number(value) is not None:
				type_counts['number'] += 1
			elif DataUtils.convert_to_boolean(value) is not None:
				type_counts['boolean'] += 1
			elif DataUtils._is_date_like(value):
				type_counts['date'] += 1
			else:
				type_counts['text'] += 1

		# Return the most frequent type
		return max(type_counts, key=lambda x: type_counts[x])

	@staticmethod
	def _is_date_like(value: Any) -> bool:
		"""Checks if value looks like a date.

		Args:
		    value: Value to check

		Returns:
		    True if value looks like a date
		"""
		if not isinstance(value, str):
			return False

		# Simple patterns for dates
		date_patterns = [
			r'\d{1,2}/\d{1,2}/\d{4}',  # MM/DD/YYYY
			r'\d{4}-\d{1,2}-\d{1,2}',  # YYYY-MM-DD
			r'\d{1,2}\.\d{1,2}\.\d{4}',  # DD.MM.YYYY
		]

		for pattern in date_patterns:
			if re.match(pattern, value.strip()):
				return True

		return False

	@staticmethod
	def find_empty_rows(data: list[list[Any]]) -> list[int]:
		"""Finds empty rows in data.

		Args:
		    data: Two-dimensional data array

		Returns:
		    List of empty row indices (starting from 0)
		"""
		empty_rows = []

		for i, row in enumerate(data):
			if not row or all(cell is None or str(cell).strip() == '' for cell in row):
				empty_rows.append(i)

		return empty_rows

	@staticmethod
	def find_empty_columns(data: list[list[Any]]) -> list[int]:
		"""Finds empty columns in data.

		Args:
		    data: Two-dimensional data array

		Returns:
		    List of empty column indices (starting from 0)
		"""
		if not data:
			return []

		empty_columns = []
		max_cols = max(len(row) for row in data) if data else 0

		for col in range(max_cols):
			is_empty = True
			for row in data:
				if col < len(row) and row[col] is not None and str(row[col]).strip():
					is_empty = False
					break

			if is_empty:
				empty_columns.append(col)

		return empty_columns

	@staticmethod
	def remove_empty_rows(data: list[list[Any]]) -> list[list[Any]]:
		"""Removes empty rows from data.

		Args:
		    data: Two-dimensional data array

		Returns:
		    Data without empty rows
		"""
		return [
			row
			for row in data
			if row and any(cell is not None and str(cell).strip() for cell in row)
		]

	@staticmethod
	def remove_empty_columns(data: list[list[Any]]) -> list[list[Any]]:
		"""Removes empty columns from data.

		Args:
		    data: Two-dimensional data array

		Returns:
		    Data without empty columns
		"""
		if not data:
			return data

		empty_columns = DataUtils.find_empty_columns(data)

		# Create new array without empty columns
		result = []
		for row in data:
			new_row = []
			for i, cell in enumerate(row):
				if i not in empty_columns:
					new_row.append(cell)
			result.append(new_row)

		return result
