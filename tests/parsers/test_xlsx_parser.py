"""Tests for XLSXParser."""

import io
from unittest.mock import Mock, patch

import pytest

from src.gsparse.core.spreadsheet import Spreadsheet
from src.gsparse.core.worksheet import Worksheet
from src.gsparse.parsers.xlsx_parser import XLSXParser


class TestXLSXParser:
	"""Tests for XLSXParser class."""

	def test_xlsx_parser_creation_default(self):
		"""Test XLSX parser creation with default parameters."""
		parser = XLSXParser()
		assert parser.data_only is True

	def test_xlsx_parser_creation_custom(self):
		"""Test XLSX parser creation with custom parameters."""
		parser = XLSXParser(data_only=False)
		assert parser.data_only is False

	@patch('src.gsparse.parsers.xlsx_parser.load_workbook')
	def test_parse_simple_xlsx(self, mock_load_workbook):
		"""Test parsing simple XLSX data."""
		# Mock workbook and worksheet
		mock_worksheet = Mock()
		mock_worksheet.iter_rows.return_value = iter(
			[
				('Name', 'Age', 'City'),
				('John', 25, 'Moscow'),
				('Mary', 30, 'St. Petersburg'),
			]
		)
		mock_worksheet.title = 'Test'

		mock_workbook = Mock()
		mock_workbook.__getitem__ = Mock(return_value=mock_worksheet)
		mock_workbook.sheetnames = ['Test']
		mock_load_workbook.return_value = mock_workbook

		parser = XLSXParser()
		xlsx_data = b'fake_xlsx_data'
		worksheet = parser.parse(xlsx_data, 'Test')

		assert isinstance(worksheet, Worksheet)
		assert worksheet.name == 'Test'
		assert worksheet.row_count == 3
		assert worksheet.column_count == 3

		# Verify workbook was loaded correctly
		mock_load_workbook.assert_called_once()
		call_args = mock_load_workbook.call_args
		assert isinstance(call_args[0][0], io.BytesIO)
		assert call_args[1]['data_only'] is True
		assert call_args[1]['read_only'] is True

		# Verify workbook was closed
		mock_workbook.close.assert_called_once()

	@patch('src.gsparse.parsers.xlsx_parser.load_workbook')
	def test_parse_xlsx_worksheet_not_found(self, mock_load_workbook):
		"""Test parsing XLSX when specified worksheet not found."""
		# Mock workbook with different worksheet name
		mock_worksheet = Mock()
		mock_worksheet.iter_rows.return_value = [('Name', 'Age'), ('John', 25)]
		mock_worksheet.title = 'DefaultSheet'

		mock_workbook = Mock()
		mock_workbook.__getitem__ = Mock(side_effect=KeyError('Sheet not found'))
		mock_workbook.active = mock_worksheet
		mock_workbook.sheetnames = ['DefaultSheet']
		mock_load_workbook.return_value = mock_workbook

		parser = XLSXParser()
		xlsx_data = b'fake_xlsx_data'
		worksheet = parser.parse(xlsx_data, 'NonExistentSheet')

		assert worksheet.name == 'DefaultSheet'
		assert worksheet.row_count == 2
		assert worksheet.column_count == 2

	@patch('src.gsparse.parsers.xlsx_parser.load_workbook')
	def test_parse_xlsx_empty_data(self, mock_load_workbook):
		"""Test parsing XLSX with empty data."""
		mock_worksheet = Mock()
		mock_worksheet.iter_rows.return_value = iter([])
		mock_worksheet.title = 'Empty'

		mock_workbook = Mock()
		mock_workbook.__getitem__ = Mock(return_value=mock_worksheet)
		mock_workbook.sheetnames = ['Empty']
		mock_load_workbook.return_value = mock_workbook

		parser = XLSXParser()
		xlsx_data = b'fake_xlsx_data'
		worksheet = parser.parse(xlsx_data, 'Empty')

		assert worksheet.name == 'Empty'
		assert worksheet.row_count == 0
		assert worksheet.column_count == 0

	@patch('src.gsparse.parsers.xlsx_parser.load_workbook')
	def test_parse_xlsx_uneven_rows(self, mock_load_workbook):
		"""Test parsing XLSX with uneven row lengths."""
		mock_worksheet = Mock()
		mock_worksheet.iter_rows.return_value = iter(
			[
				('Name', 'Age', 'City'),
				('John', 25),  # Missing third column
				('Mary', 30, 'St. Petersburg', 'Extra'),  # Extra column
			]
		)
		mock_worksheet.title = 'Uneven'

		mock_workbook = Mock()
		mock_workbook.__getitem__ = Mock(return_value=mock_worksheet)
		mock_workbook.sheetnames = ['Uneven']
		mock_load_workbook.return_value = mock_workbook

		parser = XLSXParser()
		xlsx_data = b'fake_xlsx_data'
		worksheet = parser.parse(xlsx_data, 'Uneven')

		assert worksheet.row_count == 3
		assert worksheet.column_count == 4  # Should be max length

		# Check that short rows are padded with None
		assert worksheet.get_cell(2, 3).value is None
		assert worksheet.get_cell(3, 4).value == 'Extra'

	@patch('src.gsparse.parsers.xlsx_parser.load_workbook')
	def test_parse_xlsx_error_handling(self, mock_load_workbook):
		"""Test XLSX parsing error handling."""
		mock_load_workbook.side_effect = Exception('Invalid XLSX file')

		parser = XLSXParser()
		xlsx_data = b'invalid_xlsx_data'

		with pytest.raises(ValueError, match='Failed to parse XLSX data'):
			parser.parse(xlsx_data, 'Error')

	@patch('src.gsparse.parsers.xlsx_parser.load_workbook')
	def test_parse_multiple_xlsx(self, mock_load_workbook):
		"""Test parsing multiple XLSX files."""
		# Mock for first worksheet
		mock_worksheet1 = Mock()
		mock_worksheet1.iter_rows.return_value = iter([('Name', 'Age'), ('John', 25)])
		mock_worksheet1.title = 'Sheet1'

		# Mock for second worksheet
		mock_worksheet2 = Mock()
		mock_worksheet2.iter_rows.return_value = iter(
			[('City', 'Country'), ('Moscow', 'Russia')]
		)
		mock_worksheet2.title = 'Sheet2'

		mock_workbook = Mock()
		mock_workbook.__getitem__ = Mock(side_effect=[mock_worksheet1, mock_worksheet2])
		mock_workbook.sheetnames = ['Sheet1', 'Sheet2']
		mock_load_workbook.return_value = mock_workbook

		parser = XLSXParser()
		data_dict = {'Sheet1': b'fake_xlsx_data1', 'Sheet2': b'fake_xlsx_data2'}
		spreadsheet = parser.parse_multiple(data_dict)

		assert isinstance(spreadsheet, Spreadsheet)
		assert spreadsheet.title == 'Sheet1'
		assert spreadsheet.worksheet_count == 2
		assert spreadsheet.worksheet_names == ['Sheet1', 'Sheet2']

	@patch('src.gsparse.parsers.xlsx_parser.load_workbook')
	def test_parse_workbook(self, mock_load_workbook):
		"""Test parsing entire XLSX workbook."""
		# Mock for first worksheet
		mock_worksheet1 = Mock()
		mock_worksheet1.iter_rows.return_value = iter([('Name', 'Age'), ('John', 25)])
		mock_worksheet1.title = 'Sheet1'

		# Mock for second worksheet
		mock_worksheet2 = Mock()
		mock_worksheet2.iter_rows.return_value = iter(
			[('City', 'Country'), ('Moscow', 'Russia')]
		)
		mock_worksheet2.title = 'Sheet2'

		mock_workbook = Mock()
		mock_workbook.__getitem__ = Mock(side_effect=[mock_worksheet1, mock_worksheet2])
		mock_workbook.sheetnames = ['Sheet1', 'Sheet2']
		mock_load_workbook.return_value = mock_workbook

		parser = XLSXParser()
		xlsx_data = b'fake_xlsx_data'
		spreadsheet = parser.parse_workbook(xlsx_data)

		assert isinstance(spreadsheet, Spreadsheet)
		assert spreadsheet.title == 'Sheet1'
		assert spreadsheet.worksheet_count == 2
		assert spreadsheet.worksheet_names == ['Sheet1', 'Sheet2']

		# Verify workbook was closed
		mock_workbook.close.assert_called_once()

	@patch('src.gsparse.parsers.xlsx_parser.load_workbook')
	def test_parse_workbook_empty(self, mock_load_workbook):
		"""Test parsing empty workbook."""
		mock_workbook = Mock()
		mock_workbook.sheetnames = []
		mock_load_workbook.return_value = mock_workbook

		parser = XLSXParser()
		xlsx_data = b'fake_xlsx_data'
		# This might raise an error if Spreadsheet requires at least one worksheet
		try:
			spreadsheet = parser.parse_workbook(xlsx_data)
			assert spreadsheet.title == 'Untitled'
			assert spreadsheet.worksheet_count == 0
		except ValueError as e:
			# If it fails, it should be with the expected message
			assert 'Spreadsheet must contain at least one worksheet' in str(e)

	@patch('src.gsparse.parsers.xlsx_parser.load_workbook')
	def test_parse_workbook_error_handling(self, mock_load_workbook):
		"""Test workbook parsing error handling."""
		mock_load_workbook.side_effect = Exception('Invalid workbook')

		parser = XLSXParser()
		xlsx_data = b'invalid_xlsx_data'

		with pytest.raises(ValueError, match='Failed to parse XLSX workbook'):
			parser.parse_workbook(xlsx_data)

	@patch('src.gsparse.parsers.xlsx_parser.load_workbook')
	def test_get_worksheet_names(self, mock_load_workbook):
		"""Test getting worksheet names from XLSX file."""
		mock_workbook = Mock()
		mock_workbook.sheetnames = ['Sheet1', 'Sheet2', 'Sheet3']
		mock_load_workbook.return_value = mock_workbook

		parser = XLSXParser()
		xlsx_data = b'fake_xlsx_data'
		names = parser.get_worksheet_names(xlsx_data)

		assert names == ['Sheet1', 'Sheet2', 'Sheet3']
		mock_workbook.close.assert_called_once()

	@patch('src.gsparse.parsers.xlsx_parser.load_workbook')
	def test_get_worksheet_names_error(self, mock_load_workbook):
		"""Test getting worksheet names with error."""
		mock_load_workbook.side_effect = Exception('Invalid file')

		parser = XLSXParser()
		xlsx_data = b'invalid_xlsx_data'
		names = parser.get_worksheet_names(xlsx_data)

		assert names == []

	@patch('src.gsparse.parsers.xlsx_parser.load_workbook')
	def test_parse_xlsx_with_formulas(self, mock_load_workbook):
		"""Test parsing XLSX with formulas when data_only=False."""
		mock_worksheet = Mock()
		mock_worksheet.iter_rows.return_value = iter(
			[('Name', 'Age', 'Formula'), ('John', 25, '=A2*2'), ('Mary', 30, '=B3+5')]
		)
		mock_worksheet.title = 'Formulas'

		mock_workbook = Mock()
		mock_workbook.__getitem__ = Mock(return_value=mock_worksheet)
		mock_workbook.sheetnames = ['Formulas']
		mock_load_workbook.return_value = mock_workbook

		parser = XLSXParser(data_only=False)
		xlsx_data = b'fake_xlsx_data'
		worksheet = parser.parse(xlsx_data, 'Formulas')

		# Verify data_only=False was passed
		call_args = mock_load_workbook.call_args
		assert call_args[1]['data_only'] is False

		assert worksheet.get_cell(2, 3).value == '=A2*2'
		assert worksheet.get_cell(3, 3).value == '=B3+5'

	@patch('src.gsparse.parsers.xlsx_parser.load_workbook')
	def test_parse_xlsx_with_none_values(self, mock_load_workbook):
		"""Test parsing XLSX with None values."""
		mock_worksheet = Mock()
		mock_worksheet.iter_rows.return_value = iter(
			[('Name', 'Age', 'City'), ('John', None, 'Moscow'), (None, 30, None)]
		)
		mock_worksheet.title = 'NoneValues'

		mock_workbook = Mock()
		mock_workbook.__getitem__ = Mock(return_value=mock_worksheet)
		mock_workbook.sheetnames = ['NoneValues']
		mock_load_workbook.return_value = mock_workbook

		parser = XLSXParser()
		xlsx_data = b'fake_xlsx_data'
		worksheet = parser.parse(xlsx_data, 'NoneValues')

		assert worksheet.get_cell(2, 2).value is None
		assert worksheet.get_cell(3, 1).value is None
		assert worksheet.get_cell(3, 3).value is None
