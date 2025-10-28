"""Spreadsheet class for representing a Google Sheets table with multiple worksheets."""

import logging
from typing import List, Optional, Dict, Any, Iterator
from dataclasses import dataclass

from .worksheet import Worksheet

logger = logging.getLogger(__name__)


@dataclass
class Spreadsheet:
	"""Represents a Google Sheets table with multiple worksheets.
	
	Attributes:
		title: Table title
		worksheets: List of worksheets in the table
		url: Table URL (if known)
	"""
	
	title: str
	worksheets: List[Worksheet]
	url: Optional[str] = None
	
	def __post_init__(self) -> None:
		"""Validate data after initialization."""
		if not self.title.strip():
			logger.error(f"Empty spreadsheet title")
			raise ValueError("Spreadsheet title cannot be empty")
		if not self.worksheets:
			logger.error(f"No worksheets provided")
			raise ValueError("Spreadsheet must contain at least one worksheet")
		
		logger.debug(f"Created spreadsheet '{self.title}' with {len(self.worksheets)} worksheets")
	
	@property
	def worksheet_count(self) -> int:
		"""Number of worksheets in the spreadsheet."""
		return len(self.worksheets)
	
	@property
	def worksheet_names(self) -> List[str]:
		"""List of all worksheet names."""
		return [ws.name for ws in self.worksheets]
	
	def get_worksheet(self, name: str) -> Optional[Worksheet]:
		"""Gets worksheet by name.
		
		Args:
			name: Worksheet name
			
		Returns:
			Worksheet or None if not found
		"""
		for worksheet in self.worksheets:
			if worksheet.name == name:
				return worksheet
		return None
	
	def get_worksheet_by_index(self, index: int) -> Optional[Worksheet]:
		"""Gets worksheet by index.
		
		Args:
			index: Worksheet index (starting from 0)
			
		Returns:
			Worksheet or None if index is invalid
		"""
		if 0 <= index < len(self.worksheets):
			return self.worksheets[index]
		return None
	
	def get_first_worksheet(self) -> Optional[Worksheet]:
		"""Gets the first worksheet in the spreadsheet."""
		return self.worksheets[0] if self.worksheets else None
	
	def get_last_worksheet(self) -> Optional[Worksheet]:
		"""Gets the last worksheet in the spreadsheet."""
		return self.worksheets[-1] if self.worksheets else None
	
	def add_worksheet(self, worksheet: Worksheet) -> None:
		"""Adds a new worksheet to the spreadsheet.
		
		Args:
			worksheet: Worksheet to add
		"""
		# Проверяем, что лист с таким именем еще не существует
		if self.get_worksheet(worksheet.name):
			raise ValueError(f"Лист с именем '{worksheet.name}' уже существует")
		
		self.worksheets.append(worksheet)
	
	def remove_worksheet(self, name: str) -> bool:
		"""Removes worksheet by name.
		
		Args:
			name: Worksheet name to remove
			
		Returns:
			True if worksheet was removed, False if not found
		"""
		for i, worksheet in enumerate(self.worksheets):
			if worksheet.name == name:
				del self.worksheets[i]
				return True
		return False
	
	def get_all_cells(self) -> List[Any]:
		"""Returns all cells from all worksheets."""
		all_cells = []
		for worksheet in self.worksheets:
			all_cells.extend(worksheet.get_all_cells())
		return all_cells
	
	def get_data_summary(self) -> Dict[str, Any]:
		"""Returns spreadsheet data summary.
		
		Returns:
			Dictionary with spreadsheet information
		"""
		total_cells = sum(ws.row_count * ws.column_count for ws in self.worksheets)
		non_empty_cells = sum(
			len([cell for cell in ws.get_all_cells() if not cell.is_empty])
			for ws in self.worksheets
		)
		
		return {
			"title": self.title,
			"worksheet_count": self.worksheet_count,
			"worksheet_names": self.worksheet_names,
			"total_cells": total_cells,
			"non_empty_cells": non_empty_cells,
			"url": self.url,
		}
	
	def find_cells_by_value(self, value: Any) -> List[Any]:
		"""Finds all cells with the specified value in all worksheets."""
		cells = []
		for worksheet in self.worksheets:
			cells.extend(worksheet.find_cells_by_value(value))
		return cells
	
	def find_cells_by_pattern(self, pattern: str) -> List[Any]:
		"""Finds all cells whose values match the regular expression."""
		cells = []
		for worksheet in self.worksheets:
			cells.extend(worksheet.find_cells_by_pattern(pattern))
		return cells
	
	def export_to_dict(self, headers_row: int = 1) -> Dict[str, List[Dict[str, Any]]]:
		"""Exports all worksheets to dictionary.
		
		Args:
			headers_row: Row number with headers for each worksheet
			
		Returns:
			Dictionary where keys are worksheet names, values are lists of dictionaries
		"""
		result = {}
		for worksheet in self.worksheets:
			result[worksheet.name] = worksheet.get_data_as_dict(headers_row)
		return result
	
	def __iter__(self) -> Iterator[Worksheet]:
		"""Iterator over all worksheets in the spreadsheet."""
		return iter(self.worksheets)
	
	def __getitem__(self, name: str) -> Worksheet:
		"""Allows accessing worksheets like dictionary elements."""
		worksheet = self.get_worksheet(name)
		if worksheet is None:
			raise KeyError(f"Лист '{name}' не найден")
		return worksheet
	
	def __contains__(self, name: str) -> bool:
		"""Checks if worksheet with specified name exists."""
		return self.get_worksheet(name) is not None
