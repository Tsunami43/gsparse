"""Worksheet class for representing a sheet in Google Sheets."""

import logging
from typing import List, Optional, Any, Dict, Iterator
from dataclasses import dataclass

from .cell import Cell
from .range import Range

logger = logging.getLogger(__name__)


@dataclass
class Worksheet:
	"""Represents a worksheet in Google Sheets.
	
	Attributes:
		name: Worksheet name
		data: Two-dimensional array of worksheet data
		row_count: Number of rows
		column_count: Number of columns
	"""
	
	name: str
	data: List[List[Any]]
	row_count: int
	column_count: int
	
	def __post_init__(self) -> None:
		"""Validate data after initialization."""
		if not self.name.strip():
			logger.error(f"Empty worksheet name")
			raise ValueError("Worksheet name cannot be empty")
		if self.row_count < 0 or self.column_count < 0:
			logger.error(f"Invalid dimensions: rows={self.row_count}, columns={self.column_count}")
			raise ValueError("Row and column counts must be non-negative")
		
		logger.debug(f"Created worksheet '{self.name}' with {self.row_count}x{self.column_count} dimensions")
	
	def get_cell(self, row: int, column: int) -> Optional[Cell]:
		"""Gets cell by coordinates (starting from 1).
		
		Args:
			row: Row number (starting from 1)
			column: Column number (starting from 1)
			
		Returns:
			Cell or None if cell doesn't exist
		"""
		if not self._is_valid_coordinates(row, column):
			return None
		
		value = self.data[row - 1][column - 1] if self.data else None
		return Cell(row=row, column=column, value=value)
	
	def get_range(self, start_row: int, end_row: int, start_column: int, end_column: int) -> Range:
		"""Gets range of cells.
		
		Args:
			start_row: Starting row (inclusive)
			end_row: Ending row (inclusive)
			start_column: Starting column (inclusive)
			end_column: Ending column (inclusive)
			
		Returns:
			Range object
		"""
		return Range(
			start_row=start_row,
			end_row=end_row,
			start_column=start_column,
			end_column=end_column,
			worksheet_name=self.name
		)
	
	def get_range_by_address(self, address: str) -> Range:
		"""Gets range by address (e.g., "A1:B2").
		
		Args:
			address: Range address
			
		Returns:
			Range object
		"""
		range_obj = Range.from_address(address)
		range_obj.worksheet_name = self.name
		return range_obj
	
	def get_all_cells(self) -> List[Cell]:
		"""Returns all cells in the worksheet."""
		cells = []
		for row_idx, row_data in enumerate(self.data):
			for col_idx, value in enumerate(row_data):
				cell = Cell(
					row=row_idx + 1,
					column=col_idx + 1,
					value=value
				)
				cells.append(cell)
		return cells
	
	def get_cells_in_range(self, range_obj: Range) -> List[Cell]:
		"""Gets cells in the specified range."""
		if range_obj.worksheet_name and range_obj.worksheet_name != self.name:
			return []
		
		cells = []
		for row in range(range_obj.start_row, range_obj.end_row + 1):
			for col in range(range_obj.start_column, range_obj.end_column + 1):
				cell = self.get_cell(row, col)
				if cell:
					cells.append(cell)
		return cells
	
	def get_row(self, row_number: int) -> List[Cell]:
		"""Gets all cells in the specified row."""
		if not self._is_valid_row(row_number):
			return []
		
		cells = []
		for col in range(1, self.column_count + 1):
			cell = self.get_cell(row_number, col)
			if cell:
				cells.append(cell)
		return cells
	
	def get_column(self, column_number: int) -> List[Cell]:
		"""Gets all cells in the specified column."""
		if not self._is_valid_column(column_number):
			return []
		
		cells = []
		for row in range(1, self.row_count + 1):
			cell = self.get_cell(row, column_number)
			if cell:
				cells.append(cell)
		return cells
	
	def get_columns(self) -> List[List[Any]]:
		"""Gets all columns as a list of lists.
		
		Returns:
			List where each element is a column (list of values)
		"""
		if not self.data or not self.column_count:
			return []
		
		columns = []
		for col_idx in range(self.column_count):
			column = []
			for row in self.data:
				if col_idx < len(row):
					column.append(row[col_idx])
				else:
					column.append(None)
			columns.append(column)
		
		return columns
	
	def get_rows(self) -> List[List[Any]]:
		"""Gets all rows as a list of lists.
		
		Returns:
			List where each element is a row (list of values)
		"""
		if not self.data:
			return []
		
		# Return a copy of the data to avoid external modifications
		return [row.copy() for row in self.data]
	
	def get_data_as_dict(self, headers_row: int = 1) -> List[Dict[str, Any]]:
		"""Converts data to list of dictionaries using specified row as headers.
		
		Args:
			headers_row: Row number with headers (default 1)
			
		Returns:
			List of dictionaries where keys are column headers
		"""
		if not self.data or headers_row > self.row_count:
			return []
		
		# Get headers
		header_cells = self.get_row(headers_row)
		headers = [cell.value for cell in header_cells if cell and not cell.is_empty]
		
		if not headers:
			return []
		
		# Get data
		result = []
		for row_num in range(headers_row + 1, self.row_count + 1):
			row_cells = self.get_row(row_num)
			row_data = {}
			
			for i, cell in enumerate(row_cells):
				if i < len(headers):
					row_data[headers[i]] = cell.value if cell else None
			
			result.append(row_data)
		
		return result
	
	def find_cells_by_value(self, value: Any) -> List[Cell]:
		"""Finds all cells with the specified value."""
		cells = []
		for cell in self.get_all_cells():
			if cell.value == value:
				cells.append(cell)
		return cells
	
	def find_cells_by_pattern(self, pattern: str) -> List[Cell]:
		"""Finds all cells whose values match the regular expression."""
		import re
		compiled_pattern = re.compile(pattern)
		cells = []
		
		for cell in self.get_all_cells():
			if cell.value and compiled_pattern.search(str(cell.value)):
				cells.append(cell)
		return cells
	
	def remove_empty_rows(self) -> 'Worksheet':
		"""Removes empty rows from the worksheet.
		
		Returns:
			New Worksheet instance without empty rows
		"""
		if not self.data:
			return self
		
		# Filter out empty rows
		non_empty_rows = []
		for row in self.data:
			# Check if row has any non-empty values
			if any(cell is not None and str(cell).strip() for cell in row):
				non_empty_rows.append(row)
		
		# Calculate new dimensions
		new_row_count = len(non_empty_rows)
		new_column_count = max(len(row) for row in non_empty_rows) if non_empty_rows else 0
		
		# Normalize rows to have same length
		normalized_rows = []
		for row in non_empty_rows:
			normalized_row = row + [None] * (new_column_count - len(row))
			normalized_rows.append(normalized_row)
		
		return Worksheet(
			name=self.name,
			data=normalized_rows,
			row_count=new_row_count,
			column_count=new_column_count
		)
	
	def remove_empty_columns(self) -> 'Worksheet':
		"""Removes empty columns from the worksheet.
		
		Returns:
			New Worksheet instance without empty columns
		"""
		if not self.data or not self.column_count:
			return self
		
		# Find empty columns
		empty_columns = set()
		for col_idx in range(self.column_count):
			is_empty = True
			for row in self.data:
				if col_idx < len(row) and row[col_idx] is not None and str(row[col_idx]).strip():
					is_empty = False
					break
			if is_empty:
				empty_columns.add(col_idx)
		
		# Create new data without empty columns
		new_data = []
		for row in self.data:
			new_row = []
			for col_idx, cell in enumerate(row):
				if col_idx not in empty_columns:
					new_row.append(cell)
			new_data.append(new_row)
		
		# Calculate new dimensions
		new_row_count = len(new_data)
		new_column_count = max(len(row) for row in new_data) if new_data else 0
		
		return Worksheet(
			name=self.name,
			data=new_data,
			row_count=new_row_count,
			column_count=new_column_count
		)
	
	def clean_data(self) -> 'Worksheet':
		"""Removes both empty rows and empty columns from the worksheet.
		
		Returns:
			New Worksheet instance with cleaned data
		"""
		# First remove empty rows, then empty columns
		cleaned_worksheet = self.remove_empty_rows()
		return cleaned_worksheet.remove_empty_columns()
	
	def remove_empty_rows_inplace(self) -> None:
		"""Removes empty rows from the worksheet in place.
		
		Modifies the current worksheet object.
		"""
		if not self.data:
			return
		
		# Filter out empty rows
		non_empty_rows = []
		for row in self.data:
			# Check if row has any non-empty values
			if any(cell is not None and str(cell).strip() for cell in row):
				non_empty_rows.append(row)
		
		# Update data
		self.data = non_empty_rows
		
		# Update dimensions
		self.row_count = len(non_empty_rows)
		self.column_count = max(len(row) for row in non_empty_rows) if non_empty_rows else 0
		
		# Normalize rows to have same length
		normalized_rows = []
		for row in self.data:
			normalized_row = row + [None] * (self.column_count - len(row))
			normalized_rows.append(normalized_row)
		
		self.data = normalized_rows
	
	def remove_empty_columns_inplace(self) -> None:
		"""Removes empty columns from the worksheet in place.
		
		Modifies the current worksheet object.
		"""
		if not self.data or not self.column_count:
			return
		
		# Find empty columns
		empty_columns = set()
		for col_idx in range(self.column_count):
			is_empty = True
			for row in self.data:
				if col_idx < len(row) and row[col_idx] is not None and str(row[col_idx]).strip():
					is_empty = False
					break
			if is_empty:
				empty_columns.add(col_idx)
		
		# Create new data without empty columns
		new_data = []
		for row in self.data:
			new_row = []
			for col_idx, cell in enumerate(row):
				if col_idx not in empty_columns:
					new_row.append(cell)
			new_data.append(new_row)
		
		# Update data and dimensions
		self.data = new_data
		self.row_count = len(new_data)
		self.column_count = max(len(row) for row in new_data) if new_data else 0
	
	def clean_data_inplace(self) -> None:
		"""Removes both empty rows and empty columns from the worksheet in place.
		
		Modifies the current worksheet object.
		"""
		# First remove empty rows, then empty columns
		self.remove_empty_rows_inplace()
		self.remove_empty_columns_inplace()
	
	def __iter__(self) -> Iterator[Cell]:
		"""Iterator over all cells in the worksheet."""
		return iter(self.get_all_cells())
	
	def _is_valid_coordinates(self, row: int, column: int) -> bool:
		"""Checks if coordinates are valid."""
		return self._is_valid_row(row) and self._is_valid_column(column)
	
	def _is_valid_row(self, row: int) -> bool:
		"""Checks if row number is valid."""
		return 1 <= row <= self.row_count
	
	def _is_valid_column(self, column: int) -> bool:
		"""Checks if column number is valid."""
		return 1 <= column <= self.column_count
