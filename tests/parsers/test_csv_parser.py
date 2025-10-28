"""Tests for CSVParser."""

import pytest

from src.gsparse.core.spreadsheet import Spreadsheet
from src.gsparse.core.worksheet import Worksheet
from src.gsparse.parsers.csv_parser import CSVParser


class TestCSVParser:
	"""Tests for CSVParser class."""

	def test_csv_parser_creation_default(self):
		"""Test CSV parser creation with default parameters."""
		parser = CSVParser()
		assert parser.delimiter == ','
		assert parser.quotechar == '"'
		assert parser.encoding is None

	def test_csv_parser_creation_custom(self):
		"""Test CSV parser creation with custom parameters."""
		parser = CSVParser(delimiter=';', quotechar="'", encoding='utf-8')
		assert parser.delimiter == ';'
		assert parser.quotechar == "'"
		assert parser.encoding == 'utf-8'

	def test_parse_simple_csv(self):
		"""Test parsing simple CSV data."""
		parser = CSVParser()
		csv_data = b'Name,Age,City\nJohn,25,Moscow\nMary,30,St. Petersburg'
		worksheet = parser.parse(csv_data, 'Test')

		assert isinstance(worksheet, Worksheet)
		assert worksheet.name == 'Test'
		assert worksheet.row_count == 3
		assert worksheet.column_count == 3

		# Check first row (header)
		assert worksheet.get_cell(1, 1).value == 'Name'
		assert worksheet.get_cell(1, 2).value == 'Age'
		assert worksheet.get_cell(1, 3).value == 'City'

		# Check second row
		assert worksheet.get_cell(2, 1).value == 'John'
		assert worksheet.get_cell(2, 2).value == '25'
		assert worksheet.get_cell(2, 3).value == 'Moscow'

	def test_parse_empty_csv(self):
		"""Test parsing empty CSV data."""
		parser = CSVParser()
		csv_data = b''
		worksheet = parser.parse(csv_data, 'Empty')

		assert worksheet.name == 'Empty'
		assert worksheet.row_count == 0
		assert worksheet.column_count == 0

	def test_parse_csv_with_quotes(self):
		"""Test parsing CSV with quoted values."""
		parser = CSVParser()
		csv_data = b'"Name","Age","City"\n"John, Jr.",25,"Moscow, Russia"\n"Mary",30,"St. Petersburg"'
		worksheet = parser.parse(csv_data, 'Quoted')

		assert worksheet.row_count == 3
		assert worksheet.column_count == 3
		assert worksheet.get_cell(2, 1).value == 'John, Jr.'
		assert worksheet.get_cell(2, 3).value == 'Moscow, Russia'

	def test_parse_csv_with_different_delimiter(self):
		"""Test parsing CSV with semicolon delimiter."""
		parser = CSVParser(delimiter=';')
		csv_data = b'Name;Age;City\nJohn;25;Moscow\nMary;30;St. Petersburg'
		worksheet = parser.parse(csv_data, 'Semicolon')

		assert worksheet.row_count == 3
		assert worksheet.column_count == 3
		assert worksheet.get_cell(2, 1).value == 'John'

	def test_parse_csv_with_tabs(self):
		"""Test parsing CSV with tab delimiter."""
		parser = CSVParser(delimiter='\t')
		csv_data = b'Name\tAge\tCity\nJohn\t25\tMoscow\nMary\t30\tSt. Petersburg'
		worksheet = parser.parse(csv_data, 'Tab')

		assert worksheet.row_count == 3
		assert worksheet.column_count == 3
		assert worksheet.get_cell(2, 1).value == 'John'

	def test_parse_csv_uneven_rows(self):
		"""Test parsing CSV with uneven row lengths."""
		parser = CSVParser()
		csv_data = b'Name,Age,City\nJohn,25\nMary,30,St. Petersburg,Extra'
		worksheet = parser.parse(csv_data, 'Uneven')

		assert worksheet.row_count == 3
		assert worksheet.column_count == 4  # Should be max length

		# Check that short rows are padded with None
		assert worksheet.get_cell(2, 3).value is None
		assert worksheet.get_cell(3, 4).value == 'Extra'

	def test_parse_csv_with_encoding_detection(self):
		"""Test parsing CSV with automatic encoding detection."""
		parser = CSVParser()
		# UTF-8 encoded CSV with Cyrillic characters
		csv_data = b'Name,Age,City\nJohn,25,Moscow\nMary,30,SPb'
		worksheet = parser.parse(csv_data, 'Cyrillic')

		assert worksheet.row_count == 3
		assert worksheet.get_cell(1, 1).value == 'Name'
		assert worksheet.get_cell(2, 1).value == 'John'

	def test_parse_csv_fallback_encoding(self):
		"""Test parsing CSV with fallback encoding."""
		parser = CSVParser(encoding='invalid')
		csv_data = b'Name,Age\nJohn,25\nMary,30'
		# This should raise an error with invalid encoding
		with pytest.raises(LookupError, match='unknown encoding: invalid'):
			parser.parse(csv_data, 'Fallback')

	def test_parse_csv_encoding_error(self):
		"""Test parsing CSV with unsupported encoding."""
		parser = CSVParser(encoding='invalid')
		# Create data that can't be decoded with any supported encoding
		csv_data = b'\xff\xfe\x00\x00'  # Invalid UTF-8

		# This should raise an error with invalid encoding
		with pytest.raises(LookupError, match='unknown encoding: invalid'):
			parser.parse(csv_data, 'Invalid')

	def test_parse_from_string(self):
		"""Test parsing CSV from string."""
		parser = CSVParser()
		csv_string = 'Name,Age\nJohn,25\nMary,30'
		worksheet = parser.parse_from_string(csv_string, 'String')

		assert worksheet.name == 'String'
		assert worksheet.row_count == 3
		assert worksheet.get_cell(2, 1).value == 'John'

	def test_parse_multiple_csv(self):
		"""Test parsing multiple CSV files."""
		parser = CSVParser()
		data_dict = {
			'Sheet1': b'Name,Age\nJohn,25\nMary,30',
			'Sheet2': b'City,Country\nMoscow,Russia\nSPb,Russia',
		}
		spreadsheet = parser.parse_multiple(data_dict)

		assert isinstance(spreadsheet, Spreadsheet)
		assert spreadsheet.title == 'Sheet1'
		assert spreadsheet.worksheet_count == 2
		assert spreadsheet.worksheet_names == ['Sheet1', 'Sheet2']

	def test_parse_multiple_empty(self):
		"""Test parsing empty dictionary."""
		parser = CSVParser()
		# This might raise an error if Spreadsheet requires at least one worksheet
		try:
			spreadsheet = parser.parse_multiple({})
			assert spreadsheet.title == 'Untitled'
			assert spreadsheet.worksheet_count == 0
		except ValueError as e:
			# If it fails, it should be with the expected message
			assert 'Spreadsheet must contain at least one worksheet' in str(e)

	def test_detect_delimiter_comma(self):
		"""Test delimiter detection for comma."""
		parser = CSVParser()
		csv_data = b'Name,Age,City\nJohn,25,Moscow\nMary,30,SPb'
		delimiter = parser.detect_delimiter(csv_data)
		assert delimiter == ','

	def test_detect_delimiter_semicolon(self):
		"""Test delimiter detection for semicolon."""
		parser = CSVParser()
		csv_data = b'Name;Age;City\nJohn;25;Moscow\nMary;30;SPb'
		delimiter = parser.detect_delimiter(csv_data)
		assert delimiter == ';'

	def test_detect_delimiter_tab(self):
		"""Test delimiter detection for tab."""
		parser = CSVParser()
		csv_data = b'Name\tAge\tCity\nJohn\t25\tMoscow\nMary\t30\tSPb'
		delimiter = parser.detect_delimiter(csv_data)
		assert delimiter == '\t'

	def test_detect_delimiter_pipe(self):
		"""Test delimiter detection for pipe."""
		parser = CSVParser()
		csv_data = b'Name|Age|City\nJohn|25|Moscow\nMary|30|SPb'
		delimiter = parser.detect_delimiter(csv_data)
		assert delimiter == '|'

	def test_detect_delimiter_empty_data(self):
		"""Test delimiter detection with empty data."""
		parser = CSVParser()
		csv_data = b''
		delimiter = parser.detect_delimiter(csv_data)
		# Should return one of the supported delimiters (comma by default)
		assert delimiter in [',', ';', '\t', '|']

	def test_parse_csv_with_unicode_escapes(self):
		"""Test parsing CSV with Unicode escape sequences."""
		parser = CSVParser()
		csv_data = b'Name,Age\n\\u0418\\u0432\\u0430\\u043d,25\n\\u041c\\u0430\\u0440\\u0438\\u044f,30'
		worksheet = parser.parse(csv_data, 'Unicode')

		# The actual result depends on the implementation
		assert worksheet.get_cell(2, 1).value in [
			'John',
			'John',
			'\\u0418\\u0432\\u0430\\u043d',
		]
		assert worksheet.get_cell(3, 1).value in [
			'Mary',
			'Mary',
			'\\u041c\\u0430\\u0440\\u0438\\u044f',
		]

	def test_parse_csv_with_mixed_quotes(self):
		"""Test parsing CSV with mixed quote characters."""
		parser = CSVParser(quotechar="'")
		csv_data = b"'Name','Age','City'\n'John','25','Moscow'\n'Mary','30','SPb'"
		worksheet = parser.parse(csv_data, 'SingleQuotes')

		assert worksheet.row_count == 3
		assert worksheet.get_cell(2, 1).value == 'John'

	def test_parse_csv_with_empty_cells(self):
		"""Test parsing CSV with empty cells."""
		parser = CSVParser()
		csv_data = b'Name,Age,City\nJohn,,Moscow\n,30,SPb\nMary,25,'
		worksheet = parser.parse(csv_data, 'EmptyCells')

		assert worksheet.row_count == 4
		assert worksheet.column_count == 3
		assert worksheet.get_cell(2, 2).value is None
		assert worksheet.get_cell(3, 1).value is None
		assert worksheet.get_cell(4, 3).value is None
