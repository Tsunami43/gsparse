"""Extended tests for Worksheet."""

import pytest

from src.gsparse.core.worksheet import Worksheet


class TestWorksheetExtended:
	"""Extended tests for Worksheet class."""

	def test_worksheet_creation_empty(self):
		"""Test creating empty worksheet."""
		worksheet = Worksheet('Empty', [], 0, 0)
		assert worksheet.name == 'Empty'
		assert worksheet.row_count == 0
		assert worksheet.column_count == 0
		assert worksheet.data == []

	def test_worksheet_creation_single_cell(self):
		"""Test creating worksheet with single cell."""
		worksheet = Worksheet('Single', [['A']], 1, 1)
		assert worksheet.name == 'Single'
		assert worksheet.row_count == 1
		assert worksheet.column_count == 1
		assert worksheet.data == [['A']]

	def test_worksheet_creation_uneven_rows(self):
		"""Test creating worksheet with uneven rows."""
		data = [['A', 'B'], ['1'], ['X', 'Y', 'Z']]
		worksheet = Worksheet('Uneven', data, 3, 3)
		assert worksheet.name == 'Uneven'
		assert worksheet.row_count == 3
		assert worksheet.column_count == 3
		assert worksheet.data == data

	def test_worksheet_creation_with_none_values(self):
		"""Test creating worksheet with None values."""
		data = [['A', None, 'C'], [None, 'B', None], ['X', 'Y', 'Z']]
		worksheet = Worksheet('WithNone', data, 3, 3)
		assert worksheet.name == 'WithNone'
		assert worksheet.row_count == 3
		assert worksheet.column_count == 3
		assert worksheet.data == data

	def test_worksheet_creation_with_empty_strings(self):
		"""Test creating worksheet with empty strings."""
		data = [['A', '', 'C'], ['', 'B', ''], ['X', 'Y', 'Z']]
		worksheet = Worksheet('WithEmpty', data, 3, 3)
		assert worksheet.name == 'WithEmpty'
		assert worksheet.row_count == 3
		assert worksheet.column_count == 3
		assert worksheet.data == data

	def test_worksheet_creation_with_mixed_types(self):
		"""Test creating worksheet with mixed data types."""
		data = [['A', 1, True], [3.14, 'B', False], [None, 'Y', 'Z']]
		worksheet = Worksheet('Mixed', data, 3, 3)
		assert worksheet.name == 'Mixed'
		assert worksheet.row_count == 3
		assert worksheet.column_count == 3
		assert worksheet.data == data

	def test_worksheet_creation_with_unicode(self):
		"""Test creating worksheet with Unicode characters."""
		data = [['Hello', 'World'], ['Hello', 'World']]
		worksheet = Worksheet('Unicode', data, 2, 2)
		assert worksheet.name == 'Unicode'
		assert worksheet.row_count == 2
		assert worksheet.column_count == 2
		assert worksheet.data == data

	def test_get_cell_edge_cases(self):
		"""Test getting cells at edge cases."""
		data = [['A', 'B'], ['1', '2']]
		worksheet = Worksheet('Test', data, 2, 2)

		# First cell
		cell = worksheet.get_cell(1, 1)
		assert cell.value == 'A'
		assert cell.address == 'A1'

		# Last cell
		cell = worksheet.get_cell(2, 2)
		assert cell.value == '2'
		assert cell.address == 'B2'

		# Out of bounds
		cell = worksheet.get_cell(3, 1)
		assert cell is None

		cell = worksheet.get_cell(1, 3)
		assert cell is None

		cell = worksheet.get_cell(0, 1)
		assert cell is None

		cell = worksheet.get_cell(1, 0)
		assert cell is None

	def test_get_cell_large_worksheet(self):
		"""Test getting cells from large worksheet."""
		# Create large worksheet
		data = []
		for i in range(100):
			row = []
			for j in range(50):
				row.append(f'R{i + 1}C{j + 1}')
			data.append(row)

		worksheet = Worksheet('Large', data, 100, 50)

		# Test various cells
		cell = worksheet.get_cell(1, 1)
		assert cell.value == 'R1C1'
		assert cell.address == 'A1'

		cell = worksheet.get_cell(50, 25)
		assert cell.value == 'R50C25'
		assert cell.address == 'Y50'

		cell = worksheet.get_cell(100, 50)
		assert cell.value == 'R100C50'
		assert cell.address == 'AX100'

	def test_get_range_edge_cases(self):
		"""Test getting ranges at edge cases."""
		data = [['A', 'B', 'C'], ['1', '2', '3'], ['X', 'Y', 'Z']]
		worksheet = Worksheet('Test', data, 3, 3)

		# Single cell range
		range_obj = worksheet.get_range(1, 1, 1, 1)
		assert range_obj.start_row == 1
		assert range_obj.end_row == 1
		assert range_obj.start_column == 1
		assert range_obj.end_column == 1
		assert range_obj.worksheet_name == 'Test'
		assert range_obj.address == 'Test!A1:A1'

		# Full worksheet range
		range_obj = worksheet.get_range(1, 3, 1, 3)
		assert range_obj.start_row == 1
		assert range_obj.end_row == 3
		assert range_obj.start_column == 1
		assert range_obj.end_column == 3
		assert range_obj.address == 'Test!A1:C3'

		# Partial range
		range_obj = worksheet.get_range(2, 3, 2, 3)
		assert range_obj.start_row == 2
		assert range_obj.end_row == 3
		assert range_obj.start_column == 2
		assert range_obj.end_column == 3
		assert range_obj.address == 'Test!B2:C3'

	def test_get_range_invalid_coordinates(self):
		"""Test getting range with invalid coordinates."""
		data = [['A', 'B'], ['1', '2']]
		worksheet = Worksheet('Test', data, 2, 2)

		# Start greater than end should raise ValueError
		with pytest.raises(
			ValueError, match='Start row cannot be greater than end row'
		):
			worksheet.get_range(2, 1, 1, 1)

		with pytest.raises(
			ValueError, match='Start column cannot be greater than end column'
		):
			worksheet.get_range(1, 1, 2, 1)

		# Out of bounds should still create Range (no validation in get_range)
		range_obj = worksheet.get_range(1, 3, 1, 1)
		assert range_obj is not None
		assert range_obj.start_row == 1
		assert range_obj.end_row == 3
		assert range_obj.start_column == 1
		assert range_obj.end_column == 1

		range_obj = worksheet.get_range(1, 1, 1, 3)
		assert range_obj is not None
		assert range_obj.start_row == 1
		assert range_obj.end_row == 1
		assert range_obj.start_column == 1
		assert range_obj.end_column == 3

	def test_get_data_as_dict_empty_worksheet(self):
		"""Test getting data as dict from empty worksheet."""
		worksheet = Worksheet('Empty', [], 0, 0)
		result = worksheet.get_data_as_dict()
		assert result == []

	def test_get_data_as_dict_single_row(self):
		"""Test getting data as dict from single row worksheet."""
		worksheet = Worksheet('Single', [['Name', 'Age', 'City']], 1, 3)
		result = worksheet.get_data_as_dict()
		assert result == []

	def test_get_data_as_dict_with_none_values(self):
		"""Test getting data as dict with None values."""
		data = [['Name', 'Age', 'City'], ['John', None, 'Moscow'], [None, 30, None]]
		worksheet = Worksheet('WithNone', data, 3, 3)
		result = worksheet.get_data_as_dict()

		assert len(result) == 2
		assert result[0]['Name'] == 'John'
		assert result[0]['Age'] is None
		assert result[0]['City'] == 'Moscow'
		assert result[1]['Name'] is None
		assert result[1]['Age'] == 30
		assert result[1]['City'] is None

	def test_get_data_as_dict_with_empty_strings(self):
		"""Test getting data as dict with empty strings."""
		data = [['Name', 'Age', 'City'], ['John', '', 'Moscow'], ['', 30, '']]
		worksheet = Worksheet('WithEmpty', data, 3, 3)
		result = worksheet.get_data_as_dict()

		assert len(result) == 2
		assert result[0]['Name'] == 'John'
		assert result[0]['Age'] == ''
		assert result[0]['City'] == 'Moscow'
		assert result[1]['Name'] == ''
		assert result[1]['Age'] == 30
		assert result[1]['City'] == ''

	def test_get_data_as_dict_with_mixed_types(self):
		"""Test getting data as dict with mixed types."""
		data = [['Name', 'Age', 'Active'], ['John', 25, True], ['Mary', 30, False]]
		worksheet = Worksheet('Mixed', data, 3, 3)
		result = worksheet.get_data_as_dict()

		assert len(result) == 2
		assert result[0]['Name'] == 'John'
		assert result[0]['Age'] == 25
		assert result[0]['Active'] is True
		assert result[1]['Name'] == 'Mary'
		assert result[1]['Age'] == 30
		assert result[1]['Active'] is False

	def test_get_columns_empty_worksheet(self):
		"""Test getting columns from empty worksheet."""
		worksheet = Worksheet('Empty', [], 0, 0)
		columns = worksheet.get_columns()
		assert columns == []

	def test_get_columns_single_column(self):
		"""Test getting columns from single column worksheet."""
		worksheet = Worksheet('Single', [['A'], ['1'], ['X']], 3, 1)
		columns = worksheet.get_columns()
		assert columns == [['A', '1', 'X']]

	def test_get_columns_with_none_values(self):
		"""Test getting columns with None values."""
		data = [['A', 'B', 'C'], ['1', None, '3'], [None, 'Y', 'Z']]
		worksheet = Worksheet('WithNone', data, 3, 3)
		columns = worksheet.get_columns()

		assert len(columns) == 3
		assert columns[0] == ['A', '1', None]
		assert columns[1] == ['B', None, 'Y']
		assert columns[2] == ['C', '3', 'Z']

	def test_get_columns_uneven_rows(self):
		"""Test getting columns from worksheet with uneven rows."""
		data = [['A', 'B'], ['1'], ['X', 'Y', 'Z']]
		worksheet = Worksheet('Uneven', data, 3, 3)
		columns = worksheet.get_columns()

		assert len(columns) == 3
		assert columns[0] == ['A', '1', 'X']
		assert columns[1] == ['B', None, 'Y']
		assert columns[2] == [None, None, 'Z']

	def test_get_rows_empty_worksheet(self):
		"""Test getting rows from empty worksheet."""
		worksheet = Worksheet('Empty', [], 0, 0)
		rows = worksheet.get_rows()
		assert rows == []

	def test_get_rows_single_row(self):
		"""Test getting rows from single row worksheet."""
		worksheet = Worksheet('Single', [['A', 'B', 'C']], 1, 3)
		rows = worksheet.get_rows()
		assert rows == [['A', 'B', 'C']]

	def test_get_rows_with_none_values(self):
		"""Test getting rows with None values."""
		data = [['A', 'B', 'C'], ['1', None, '3'], [None, 'Y', 'Z']]
		worksheet = Worksheet('WithNone', data, 3, 3)
		rows = worksheet.get_rows()

		assert len(rows) == 3
		assert rows[0] == ['A', 'B', 'C']
		assert rows[1] == ['1', None, '3']
		assert rows[2] == [None, 'Y', 'Z']

	def test_get_rows_uneven_rows(self):
		"""Test getting rows from worksheet with uneven rows."""
		data = [['A', 'B'], ['1'], ['X', 'Y', 'Z']]
		worksheet = Worksheet('Uneven', data, 3, 3)
		rows = worksheet.get_rows()

		assert len(rows) == 3
		# Worksheet doesn't normalize rows, so we get original data
		assert rows[0] == ['A', 'B']
		assert rows[1] == ['1']
		assert rows[2] == ['X', 'Y', 'Z']

	def test_worksheet_equality(self):
		"""Test worksheet equality."""
		data1 = [['A', 'B'], ['1', '2']]
		data2 = [['A', 'B'], ['1', '2']]
		data3 = [['A', 'B'], ['1', '3']]

		worksheet1 = Worksheet('Test', data1, 2, 2)
		worksheet2 = Worksheet('Test', data2, 2, 2)
		worksheet3 = Worksheet('Test', data3, 2, 2)
		worksheet4 = Worksheet('Different', data1, 2, 2)

		# Same worksheet
		assert worksheet1 == worksheet1

		# Different objects with same values
		assert worksheet1 == worksheet2

		# Different data
		assert worksheet1 != worksheet3

		# Different name
		assert worksheet1 != worksheet4

	def test_worksheet_string_representation(self):
		"""Test worksheet string representation."""
		worksheet = Worksheet('Test', [['A', 'B'], ['1', '2']], 2, 2)
		worksheet_str = str(worksheet)
		assert 'Test' in worksheet_str
		assert '2' in worksheet_str  # row_count
		assert '2' in worksheet_str  # column_count

	def test_worksheet_repr(self):
		"""Test worksheet repr representation."""
		worksheet = Worksheet('Test', [['A', 'B'], ['1', '2']], 2, 2)
		worksheet_repr = repr(worksheet)
		assert 'Worksheet' in worksheet_repr
		assert 'Test' in worksheet_repr
		assert '2' in worksheet_repr

	def test_worksheet_large_data(self):
		"""Test worksheet with large amount of data."""
		# Create large worksheet
		data = []
		for i in range(1000):
			row = []
			for j in range(100):
				row.append(f'R{i + 1}C{j + 1}')
			data.append(row)

		worksheet = Worksheet('Large', data, 1000, 100)

		assert worksheet.name == 'Large'
		assert worksheet.row_count == 1000
		assert worksheet.column_count == 100
		assert len(worksheet.data) == 1000
		assert all(len(row) == 100 for row in worksheet.data)

	def test_worksheet_unicode_names(self):
		"""Test worksheet with Unicode names."""
		worksheet = Worksheet('Sheet1', [['A', 'B']], 1, 2)
		assert worksheet.name == 'Sheet1'

		worksheet = Worksheet('工作表1', [['A', 'B']], 1, 2)
		assert worksheet.name == '工作表1'

		worksheet = Worksheet('シート1', [['A', 'B']], 1, 2)
		assert worksheet.name == 'シート1'

	def test_worksheet_special_characters_in_data(self):
		"""Test worksheet with special characters in data."""
		data = [['!@#$%^&*()', '<>?:"{}|'], ["[]\\;',./", '`~-_=+'], [' \t\n\r ', '']]
		worksheet = Worksheet('Special', data, 3, 2)

		assert worksheet.get_cell(1, 1).value == '!@#$%^&*()'
		assert worksheet.get_cell(1, 2).value == '<>?:"{}|'
		assert worksheet.get_cell(2, 1).value == "[]\\;',./"
		assert worksheet.get_cell(2, 2).value == '`~-_=+'
		assert worksheet.get_cell(3, 1).value == ' \t\n\r '
		assert worksheet.get_cell(3, 2).value == ''
