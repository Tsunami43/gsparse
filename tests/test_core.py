"""Тесты для основных сущностей."""

import pytest
from src.gsparse.core import Cell, Range, Worksheet, Spreadsheet


class TestCell:
	"""Tests for Cell class."""
	
	def test_cell_creation(self):
		"""Test cell creation."""
		cell = Cell(row=1, column=1, value="Test")
		
		assert cell.row == 1
		assert cell.column == 1
		assert cell.value == "Test"
		assert cell.address == "A1"
		assert not cell.is_empty
	
	def test_cell_address(self):
		"""Test cell address generation."""
		assert Cell(1, 1, "A").address == "A1"
		assert Cell(1, 2, "B").address == "B1"
		assert Cell(2, 1, "A").address == "A2"
		assert Cell(26, 26, "Z").address == "Z26"  # Row 26, Column 26 = Z26
		assert Cell(1, 27, "AA").address == "AA1"
	
	def test_cell_empty(self):
		"""Test cell emptiness check."""
		assert Cell(1, 1, None).is_empty
		assert Cell(1, 1, "").is_empty
		assert Cell(1, 1, "   ").is_empty
		assert not Cell(1, 1, "Тест").is_empty
	
	def test_cell_validation(self):
		"""Test cell validation."""
		with pytest.raises(ValueError):
			Cell(0, 1, "Тест")
		
		with pytest.raises(ValueError):
			Cell(1, 0, "Тест")


class TestRange:
	"""Tests for Range class."""
	
	def test_range_creation(self):
		"""Test range creation."""
		range_obj = Range(1, 3, 1, 2, "Sheet1")
		
		assert range_obj.start_row == 1
		assert range_obj.end_row == 3
		assert range_obj.start_column == 1
		assert range_obj.end_column == 2
		assert range_obj.worksheet_name == "Sheet1"
		assert range_obj.address == "Sheet1!A1:B3"
	
	def test_range_properties(self):
		"""Test range properties."""
		range_obj = Range(1, 3, 1, 2)
		
		assert range_obj.row_count == 3
		assert range_obj.column_count == 2
		assert range_obj.cell_count == 6
	
	def test_range_contains(self):
		"""Test cell containment in range."""
		range_obj = Range(1, 3, 1, 2)
		
		assert range_obj.contains_cell(1, 1)
		assert range_obj.contains_cell(3, 2)
		assert not range_obj.contains_cell(4, 1)
		assert not range_obj.contains_cell(1, 3)
	
	def test_range_from_address(self):
		"""Test range creation from address."""
		range_obj = Range.from_address("A1:B3")
		
		assert range_obj.start_row == 1
		assert range_obj.end_row == 3
		assert range_obj.start_column == 1
		assert range_obj.end_column == 2
		assert range_obj.address == "A1:B3"
	
	def test_range_validation(self):
		"""Test range validation."""
		with pytest.raises(ValueError):
			Range(0, 1, 1, 1)
		
		with pytest.raises(ValueError):
			Range(1, 0, 1, 1)
		
		with pytest.raises(ValueError):
			Range(2, 1, 1, 1)


class TestWorksheet:
	"""Tests for Worksheet class."""
	
	def test_worksheet_creation(self):
		"""Test worksheet creation."""
		data = [["A", "B"], ["1", "2"]]
		worksheet = Worksheet("Тест", data, 2, 2)
		
		assert worksheet.name == "Тест"
		assert worksheet.row_count == 2
		assert worksheet.column_count == 2
	
	def test_worksheet_get_cell(self):
		"""Test getting cell."""
		data = [["A", "B"], ["1", "2"]]
		worksheet = Worksheet("Тест", data, 2, 2)
		
		cell = worksheet.get_cell(1, 1)
		assert cell.value == "A"
		assert cell.address == "A1"
		
		cell = worksheet.get_cell(2, 2)
		assert cell.value == "2"
		assert cell.address == "B2"
	
	def test_worksheet_get_range(self):
		"""Test getting range."""
		data = [["A", "B"], ["1", "2"]]
		worksheet = Worksheet("Test", data, 2, 2)
		
		range_obj = worksheet.get_range(1, 2, 1, 2)
		assert range_obj.worksheet_name == "Test"
		assert range_obj.address == "Test!A1:B2"
	
	def test_worksheet_get_data_as_dict(self):
		"""Test data export to dictionary."""
		data = [["Name", "Age"], ["John", "25"], ["Mary", "30"]]
		worksheet = Worksheet("Test", data, 3, 2)
		
		result = worksheet.get_data_as_dict()
		assert len(result) == 2
		assert result[0]["Name"] == "John"
		assert result[0]["Age"] == "25"
		assert result[1]["Name"] == "Mary"
		assert result[1]["Age"] == "30"
	
	def test_worksheet_get_columns(self):
		"""Test getting all columns."""
		data = [["A", "B", "C"], ["1", "2", "3"], ["X", "Y", "Z"]]
		worksheet = Worksheet("Test", data, 3, 3)
		
		columns = worksheet.get_columns()
		assert len(columns) == 3
		assert columns[0] == ["A", "1", "X"]
		assert columns[1] == ["B", "2", "Y"]
		assert columns[2] == ["C", "3", "Z"]
	
	def test_worksheet_get_rows(self):
		"""Test getting all rows."""
		data = [["A", "B", "C"], ["1", "2", "3"], ["X", "Y", "Z"]]
		worksheet = Worksheet("Test", data, 3, 3)
		
		rows = worksheet.get_rows()
		assert len(rows) == 3
		assert rows[0] == ["A", "B", "C"]
		assert rows[1] == ["1", "2", "3"]
		assert rows[2] == ["X", "Y", "Z"]
	
	def test_worksheet_get_columns_empty(self):
		"""Test getting columns from empty worksheet."""
		worksheet = Worksheet("Empty", [], 0, 0)
		
		columns = worksheet.get_columns()
		assert columns == []
	
	def test_worksheet_get_rows_empty(self):
		"""Test getting rows from empty worksheet."""
		worksheet = Worksheet("Empty", [], 0, 0)
		
		rows = worksheet.get_rows()
		assert rows == []


class TestSpreadsheet:
	"""Tests for Spreadsheet class."""
	
	def test_spreadsheet_creation(self):
		"""Test spreadsheet creation."""
		worksheet1 = Worksheet("Sheet1", [["A"]], 1, 1)
		worksheet2 = Worksheet("Sheet2", [["B"]], 1, 1)
		
		spreadsheet = Spreadsheet("Test", [worksheet1, worksheet2])
		
		assert spreadsheet.title == "Test"
		assert spreadsheet.worksheet_count == 2
		assert spreadsheet.worksheet_names == ["Sheet1", "Sheet2"]
	
	def test_spreadsheet_get_worksheet(self):
		"""Test getting worksheet by name."""
		worksheet1 = Worksheet("Sheet1", [["A"]], 1, 1)
		worksheet2 = Worksheet("Sheet2", [["B"]], 1, 1)
		
		spreadsheet = Spreadsheet("Test", [worksheet1, worksheet2])
		
		assert spreadsheet.get_worksheet("Sheet1") == worksheet1
		assert spreadsheet.get_worksheet("Sheet2") == worksheet2
		assert spreadsheet.get_worksheet("NonExistent") is None
	
	def test_spreadsheet_get_worksheet_by_index(self):
		"""Test getting worksheet by index."""
		worksheet1 = Worksheet("Sheet1", [["A"]], 1, 1)
		worksheet2 = Worksheet("Sheet2", [["B"]], 1, 1)
		
		spreadsheet = Spreadsheet("Test", [worksheet1, worksheet2])
		
		assert spreadsheet.get_worksheet_by_index(0) == worksheet1
		assert spreadsheet.get_worksheet_by_index(1) == worksheet2
		assert spreadsheet.get_worksheet_by_index(2) is None
