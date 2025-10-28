"""Extended tests for Spreadsheet."""

import pytest

from src.gsparse.core.spreadsheet import Spreadsheet
from src.gsparse.core.worksheet import Worksheet


class TestSpreadsheetExtended:
	"""Extended tests for Spreadsheet class."""

	def test_spreadsheet_creation_empty(self):
		"""Test creating empty spreadsheet."""
		with pytest.raises(
			ValueError, match='Spreadsheet must contain at least one worksheet'
		):
			Spreadsheet('Empty', [])

	def test_spreadsheet_creation_single_worksheet(self):
		"""Test creating spreadsheet with single worksheet."""
		worksheet = Worksheet('Sheet1', [['A', 'B'], ['1', '2']], 2, 2)
		spreadsheet = Spreadsheet('Single', [worksheet])

		assert spreadsheet.title == 'Single'
		assert spreadsheet.worksheet_count == 1
		assert spreadsheet.worksheet_names == ['Sheet1']

	def test_spreadsheet_creation_multiple_worksheets(self):
		"""Test creating spreadsheet with multiple worksheets."""
		worksheet1 = Worksheet('Sheet1', [['A', 'B']], 1, 2)
		worksheet2 = Worksheet('Sheet2', [['1', '2']], 1, 2)
		worksheet3 = Worksheet('Sheet3', [['X', 'Y']], 1, 2)

		spreadsheet = Spreadsheet('Multiple', [worksheet1, worksheet2, worksheet3])

		assert spreadsheet.title == 'Multiple'
		assert spreadsheet.worksheet_count == 3
		assert spreadsheet.worksheet_names == ['Sheet1', 'Sheet2', 'Sheet3']

	def test_spreadsheet_creation_with_empty_worksheets(self):
		"""Test creating spreadsheet with empty worksheets."""
		worksheet1 = Worksheet('Empty1', [], 0, 0)
		worksheet2 = Worksheet('Empty2', [], 0, 0)

		spreadsheet = Spreadsheet('EmptySheets', [worksheet1, worksheet2])

		assert spreadsheet.title == 'EmptySheets'
		assert spreadsheet.worksheet_count == 2
		assert spreadsheet.worksheet_names == ['Empty1', 'Empty2']

	def test_spreadsheet_creation_with_mixed_worksheets(self):
		"""Test creating spreadsheet with mixed worksheet types."""
		worksheet1 = Worksheet('Data', [['A', 'B'], ['1', '2']], 2, 2)
		worksheet2 = Worksheet('Empty', [], 0, 0)
		worksheet3 = Worksheet('Single', [['X']], 1, 1)

		spreadsheet = Spreadsheet('Mixed', [worksheet1, worksheet2, worksheet3])

		assert spreadsheet.title == 'Mixed'
		assert spreadsheet.worksheet_count == 3
		assert spreadsheet.worksheet_names == ['Data', 'Empty', 'Single']

	def test_get_worksheet_by_name_existing(self):
		"""Test getting existing worksheet by name."""
		worksheet1 = Worksheet('Sheet1', [['A', 'B']], 1, 2)
		worksheet2 = Worksheet('Sheet2', [['1', '2']], 1, 2)
		worksheet3 = Worksheet('Sheet3', [['X', 'Y']], 1, 2)

		spreadsheet = Spreadsheet('Test', [worksheet1, worksheet2, worksheet3])

		assert spreadsheet.get_worksheet('Sheet1') == worksheet1
		assert spreadsheet.get_worksheet('Sheet2') == worksheet2
		assert spreadsheet.get_worksheet('Sheet3') == worksheet3

	def test_get_worksheet_by_name_non_existing(self):
		"""Test getting non-existing worksheet by name."""
		worksheet1 = Worksheet('Sheet1', [['A', 'B']], 1, 2)
		worksheet2 = Worksheet('Sheet2', [['1', '2']], 1, 2)

		spreadsheet = Spreadsheet('Test', [worksheet1, worksheet2])

		assert spreadsheet.get_worksheet('NonExistent') is None
		assert spreadsheet.get_worksheet('') is None
		assert spreadsheet.get_worksheet('Sheet3') is None

	def test_get_worksheet_by_name_case_sensitive(self):
		"""Test getting worksheet by name with case sensitivity."""
		worksheet1 = Worksheet('Sheet1', [['A', 'B']], 1, 2)
		worksheet2 = Worksheet('sheet1', [['1', '2']], 1, 2)

		spreadsheet = Spreadsheet('Test', [worksheet1, worksheet2])

		assert spreadsheet.get_worksheet('Sheet1') == worksheet1
		assert spreadsheet.get_worksheet('sheet1') == worksheet2
		assert spreadsheet.get_worksheet('SHEET1') is None

	def test_get_worksheet_by_index_existing(self):
		"""Test getting existing worksheet by index."""
		worksheet1 = Worksheet('Sheet1', [['A', 'B']], 1, 2)
		worksheet2 = Worksheet('Sheet2', [['1', '2']], 1, 2)
		worksheet3 = Worksheet('Sheet3', [['X', 'Y']], 1, 2)

		spreadsheet = Spreadsheet('Test', [worksheet1, worksheet2, worksheet3])

		assert spreadsheet.get_worksheet_by_index(0) == worksheet1
		assert spreadsheet.get_worksheet_by_index(1) == worksheet2
		assert spreadsheet.get_worksheet_by_index(2) == worksheet3

	def test_get_worksheet_by_index_non_existing(self):
		"""Test getting non-existing worksheet by index."""
		worksheet1 = Worksheet('Sheet1', [['A', 'B']], 1, 2)
		worksheet2 = Worksheet('Sheet2', [['1', '2']], 1, 2)

		spreadsheet = Spreadsheet('Test', [worksheet1, worksheet2])

		assert spreadsheet.get_worksheet_by_index(2) is None
		assert spreadsheet.get_worksheet_by_index(-1) is None
		assert spreadsheet.get_worksheet_by_index(100) is None

	def test_get_worksheet_by_index_float(self):
		"""Test getting worksheet by index with float value."""
		worksheet1 = Worksheet('Sheet1', [['A', 'B']], 1, 2)
		worksheet2 = Worksheet('Sheet2', [['1', '2']], 1, 2)

		spreadsheet = Spreadsheet('Test', [worksheet1, worksheet2])

		# Float indexing should raise TypeError
		with pytest.raises(
			TypeError, match='list indices must be integers or slices, not float'
		):
			spreadsheet.get_worksheet_by_index(0.0)

		with pytest.raises(
			TypeError, match='list indices must be integers or slices, not float'
		):
			spreadsheet.get_worksheet_by_index(1.0)

	def test_spreadsheet_equality(self):
		"""Test spreadsheet equality."""
		worksheet1 = Worksheet('Sheet1', [['A', 'B']], 1, 2)
		worksheet2 = Worksheet('Sheet2', [['1', '2']], 1, 2)

		spreadsheet1 = Spreadsheet('Test', [worksheet1, worksheet2])
		spreadsheet2 = Spreadsheet('Test', [worksheet1, worksheet2])
		spreadsheet3 = Spreadsheet('Different', [worksheet1, worksheet2])
		spreadsheet4 = Spreadsheet('Test', [worksheet1])

		# Same spreadsheet
		assert spreadsheet1 == spreadsheet1

		# Different objects with same values
		assert spreadsheet1 == spreadsheet2

		# Different title
		assert spreadsheet1 != spreadsheet3

		# Different worksheets
		assert spreadsheet1 != spreadsheet4

	def test_spreadsheet_string_representation(self):
		"""Test spreadsheet string representation."""
		worksheet1 = Worksheet('Sheet1', [['A', 'B']], 1, 2)
		worksheet2 = Worksheet('Sheet2', [['1', '2']], 1, 2)

		spreadsheet = Spreadsheet('Test', [worksheet1, worksheet2])
		spreadsheet_str = str(spreadsheet)

		assert 'Test' in spreadsheet_str
		assert '2' in spreadsheet_str  # worksheet_count

	def test_spreadsheet_repr(self):
		"""Test spreadsheet repr representation."""
		worksheet1 = Worksheet('Sheet1', [['A', 'B']], 1, 2)
		worksheet2 = Worksheet('Sheet2', [['1', '2']], 1, 2)

		spreadsheet = Spreadsheet('Test', [worksheet1, worksheet2])
		spreadsheet_repr = repr(spreadsheet)

		assert 'Spreadsheet' in spreadsheet_repr
		assert 'Test' in spreadsheet_repr
		assert '2' in spreadsheet_repr

	def test_spreadsheet_large_number_of_worksheets(self):
		"""Test spreadsheet with large number of worksheets."""
		worksheets = []
		for i in range(100):
			worksheet = Worksheet(f'Sheet{i + 1}', [['A', 'B']], 1, 2)
			worksheets.append(worksheet)

		spreadsheet = Spreadsheet('Large', worksheets)

		assert spreadsheet.title == 'Large'
		assert spreadsheet.worksheet_count == 100
		assert len(spreadsheet.worksheet_names) == 100
		assert spreadsheet.worksheet_names[0] == 'Sheet1'
		assert spreadsheet.worksheet_names[99] == 'Sheet100'

	def test_spreadsheet_unicode_titles(self):
		"""Test spreadsheet with Unicode titles."""
		worksheet = Worksheet('Sheet1', [['A', 'B']], 1, 2)
		spreadsheet = Spreadsheet('Table', [worksheet])

		assert spreadsheet.title == 'Table'
		assert spreadsheet.worksheet_names == ['Sheet1']

		worksheet = Worksheet('工作表1', [['A', 'B']], 1, 2)
		spreadsheet = Spreadsheet('工作簿', [worksheet])

		assert spreadsheet.title == '工作簿'
		assert spreadsheet.worksheet_names == ['工作表1']

		worksheet = Worksheet('シート1', [['A', 'B']], 1, 2)
		spreadsheet = Spreadsheet('スプレッドシート', [worksheet])

		assert spreadsheet.title == 'スプレッドシート'
		assert spreadsheet.worksheet_names == ['シート1']

	def test_spreadsheet_special_characters_in_titles(self):
		"""Test spreadsheet with special characters in titles."""
		worksheet = Worksheet('Sheet!@#$%^&*()', [['A', 'B']], 1, 2)
		spreadsheet = Spreadsheet('Test<>?:"{}|', [worksheet])

		assert spreadsheet.title == 'Test<>?:"{}|'
		assert spreadsheet.worksheet_names == ['Sheet!@#$%^&*()']

		# Test getting worksheet with special characters
		assert spreadsheet.get_worksheet('Sheet!@#$%^&*()') == worksheet

	def test_spreadsheet_empty_worksheet_names(self):
		"""Test spreadsheet with empty worksheet names."""
		# Empty worksheet names are not allowed
		with pytest.raises(ValueError, match='Worksheet name cannot be empty'):
			Worksheet('', [['A', 'B']], 1, 2)

		# Whitespace-only names are also not allowed
		with pytest.raises(ValueError, match='Worksheet name cannot be empty'):
			Worksheet('   ', [['1', '2']], 1, 2)

		# Only valid names are allowed
		worksheet3 = Worksheet('Sheet3', [['X', 'Y']], 1, 2)
		spreadsheet = Spreadsheet('Test', [worksheet3])

		assert spreadsheet.worksheet_count == 1
		assert spreadsheet.worksheet_names == ['Sheet3']
		assert spreadsheet.get_worksheet('Sheet3') == worksheet3

	def test_spreadsheet_duplicate_worksheet_names(self):
		"""Test spreadsheet with duplicate worksheet names."""
		worksheet1 = Worksheet('Sheet1', [['A', 'B']], 1, 2)
		worksheet2 = Worksheet('Sheet1', [['1', '2']], 1, 2)
		worksheet3 = Worksheet('Sheet2', [['X', 'Y']], 1, 2)

		spreadsheet = Spreadsheet('Test', [worksheet1, worksheet2, worksheet3])

		assert spreadsheet.worksheet_count == 3
		assert spreadsheet.worksheet_names == ['Sheet1', 'Sheet1', 'Sheet2']

		# Test getting worksheet with duplicate name (should return first match)
		assert spreadsheet.get_worksheet('Sheet1') == worksheet1
		assert spreadsheet.get_worksheet('Sheet2') == worksheet3

	def test_spreadsheet_worksheet_order(self):
		"""Test that worksheet order is preserved."""
		worksheets = []
		for i in range(10):
			worksheet = Worksheet(f'Sheet{i + 1}', [['A', 'B']], 1, 2)
			worksheets.append(worksheet)

		spreadsheet = Spreadsheet('OrderTest', worksheets)

		assert spreadsheet.worksheet_count == 10
		for i in range(10):
			assert spreadsheet.worksheet_names[i] == f'Sheet{i + 1}'
			assert spreadsheet.get_worksheet_by_index(i) == worksheets[i]

	def test_spreadsheet_worksheet_modification(self):
		"""Test that modifying worksheets doesn't affect spreadsheet."""
		worksheet = Worksheet('Sheet1', [['A', 'B']], 1, 2)
		spreadsheet = Spreadsheet('Test', [worksheet])

		# Modify the original worksheet
		worksheet.data[0][0] = 'Modified'

		# Get worksheet from spreadsheet
		retrieved_worksheet = spreadsheet.get_worksheet('Sheet1')

		# The retrieved worksheet should be the same object
		assert retrieved_worksheet is worksheet
		assert retrieved_worksheet.data[0][0] == 'Modified'

	def test_spreadsheet_worksheet_replacement(self):
		"""Test replacing worksheets in spreadsheet."""
		worksheet1 = Worksheet('Sheet1', [['A', 'B']], 1, 2)
		worksheet2 = Worksheet('Sheet2', [['1', '2']], 1, 2)
		worksheet3 = Worksheet('Sheet3', [['X', 'Y']], 1, 2)

		spreadsheet = Spreadsheet('Test', [worksheet1, worksheet2])

		# Replace worksheet at index 1
		spreadsheet.worksheets[1] = worksheet3

		assert spreadsheet.worksheet_count == 2
		assert spreadsheet.worksheet_names == ['Sheet1', 'Sheet3']
		assert spreadsheet.get_worksheet('Sheet1') == worksheet1
		assert spreadsheet.get_worksheet('Sheet3') == worksheet3
		assert spreadsheet.get_worksheet('Sheet2') is None
