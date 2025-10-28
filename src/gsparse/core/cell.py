"""Cell class for representing a cell in Google Sheets."""

import logging
from typing import Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Cell:
	"""Represents a cell in Google Sheets.
	
	Attributes:
		row: Row number (starting from 1)
		column: Column number (starting from 1)
		value: Cell value
		formatted_value: Formatted cell value
		formula: Cell formula (if any)
	"""
	
	row: int
	column: int
	value: Any
	formatted_value: Optional[str] = None
	formula: Optional[str] = None
	
	def __post_init__(self) -> None:
		"""Validate data after initialization."""
		if self.row < 1:
			logger.error(f"Invalid row number: {self.row}. Must be greater than 0")
			raise ValueError("Row number must be greater than 0")
		if self.column < 1:
			logger.error(f"Invalid column number: {self.column}. Must be greater than 0")
			raise ValueError("Column number must be greater than 0")
		
		logger.debug(f"Created cell {self.address} with value: {self.value}")
	
	@property
	def address(self) -> str:
		"""Returns cell address in A1 format."""
		return self._number_to_column_letter(self.column) + str(self.row)
	
	@property
	def is_empty(self) -> bool:
		"""Checks if the cell is empty."""
		return self.value is None or str(self.value).strip() == ""
	
	def _number_to_column_letter(self, col_num: int) -> str:
		"""Converts column number to letter notation (A, B, C, ...)."""
		result = ""
		while col_num > 0:
			col_num -= 1
			result = chr(65 + col_num % 26) + result
			col_num //= 26
		return result
