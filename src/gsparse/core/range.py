"""Range class for representing a range of cells in Google Sheets."""

import logging
from dataclasses import dataclass
from typing import Any

from .cell import Cell

logger = logging.getLogger(__name__)


@dataclass
class Range:
	"""Represents a range of cells in Google Sheets.

	Attributes:
		start_row: Starting row (inclusive)
		end_row: Ending row (inclusive)
		start_column: Starting column (inclusive)
		end_column: Ending column (inclusive)
		worksheet_name: Worksheet name (optional)
	"""

	start_row: int
	end_row: int
	start_column: int
	end_column: int
	worksheet_name: str | None = None

	def __post_init__(self) -> None:
		"""Validate data after initialization."""
		if self.start_row < 1 or self.end_row < 1:
			logger.error(
				f'Invalid row numbers: start={self.start_row}, end={self.end_row}'
			)
			raise ValueError('Row numbers must be greater than 0')
		if self.start_column < 1 or self.end_column < 1:
			logger.error(
				f'Invalid column numbers: start={self.start_column}, end={self.end_column}'
			)
			raise ValueError('Column numbers must be greater than 0')
		if self.start_row > self.end_row:
			logger.error(
				f'Start row ({self.start_row}) cannot be greater than end row ({self.end_row})'
			)
			raise ValueError('Start row cannot be greater than end row')
		if self.start_column > self.end_column:
			logger.error(
				f'Start column ({self.start_column}) cannot be greater than end column ({self.end_column})'
			)
			raise ValueError('Start column cannot be greater than end column')

		logger.debug(f'Created range: {self.address}')

	@property
	def address(self) -> str:
		"""Returns range address in A1:B2 format."""
		start_cell = self._number_to_column_letter(self.start_column) + str(
			self.start_row
		)
		end_cell = self._number_to_column_letter(self.end_column) + str(self.end_row)

		if self.worksheet_name:
			return f'{self.worksheet_name}!{start_cell}:{end_cell}'
		return f'{start_cell}:{end_cell}'

	@property
	def row_count(self) -> int:
		"""Number of rows in the range."""
		return self.end_row - self.start_row + 1

	@property
	def column_count(self) -> int:
		"""Number of columns in the range."""
		return self.end_column - self.start_column + 1

	@property
	def cell_count(self) -> int:
		"""Total number of cells in the range."""
		return self.row_count * self.column_count

	def contains_cell(self, row: int, column: int) -> bool:
		"""Checks if the range contains the specified cell."""
		return (
			self.start_row <= row <= self.end_row
			and self.start_column <= column <= self.end_column
		)

	def get_cells(self, data: list[list[Any]]) -> list[Cell]:
		"""Returns list of cells from data in the specified range."""
		cells = []
		logger.debug(f'Extracting cells from range {self.address}')

		for row_idx, row_data in enumerate(data[self.start_row - 1 : self.end_row]):
			for col_idx, value in enumerate(
				row_data[self.start_column - 1 : self.end_column]
			):
				cell = Cell(
					row=self.start_row + row_idx,
					column=self.start_column + col_idx,
					value=value,
				)
				cells.append(cell)

		logger.debug(f'Extracted {len(cells)} cells from range')
		return cells

	def _number_to_column_letter(self, col_num: int) -> str:
		"""Converts column number to letter notation (A, B, C, ...)."""
		result = ''
		while col_num > 0:
			col_num -= 1
			result = chr(65 + col_num % 26) + result
			col_num //= 26
		return result

	@classmethod
	def from_address(cls, address: str) -> 'Range':
		"""Creates Range from string address (e.g., "A1:B2" or "Sheet1!A1:B2")."""
		logger.debug(f'Parsing range address: {address}')

		# Split worksheet name and range
		if '!' in address:
			worksheet_name, range_part = address.split('!', 1)
		else:
			worksheet_name = None
			range_part = address

		# Parse range
		if ':' in range_part:
			start_cell, end_cell = range_part.split(':', 1)
		else:
			start_cell = end_cell = range_part

		start_row, start_col = cls._parse_cell_address(start_cell)
		end_row, end_col = cls._parse_cell_address(end_cell)

		logger.debug(f'Parsed range: {start_cell} to {end_cell}')
		return cls(
			start_row=start_row,
			end_row=end_row,
			start_column=start_col,
			end_column=end_col,
			worksheet_name=worksheet_name,
		)

	@staticmethod
	def _parse_cell_address(cell_address: str) -> tuple[int, int]:
		"""Parses cell address (e.g., "A1") into (row, column)."""
		import re

		match = re.match(r'([A-Z]+)(\d+)', cell_address.upper())
		if not match:
			logger.error(f'Invalid cell address format: {cell_address}')
			raise ValueError(f'Invalid cell address format: {cell_address}')

		col_letters = match.group(1)
		row_num = int(match.group(2))

		# Convert column letters to number
		col_num = 0
		for char in col_letters:
			col_num = col_num * 26 + (ord(char) - ord('A') + 1)

		return row_num, col_num
