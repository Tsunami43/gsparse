"""Base class for parsers."""

import logging
from abc import ABC, abstractmethod
from typing import Any

from ..core.spreadsheet import Spreadsheet
from ..core.worksheet import Worksheet

logger = logging.getLogger(__name__)


class BaseParser(ABC):
	"""Base class for all parsers."""

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
			return cleaned if cleaned else None

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
