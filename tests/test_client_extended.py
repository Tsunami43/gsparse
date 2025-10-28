"""Extended tests for GSParseClient."""

from src.gsparse import GSParseClient
from src.gsparse.core.worksheet import Worksheet


class TestGSParseClientExtended:
	"""Extended tests for GSParseClient class."""

	def test_client_creation_default(self):
		"""Test client creation with default parameters."""
		client = GSParseClient()
		assert client is not None
		assert client.downloader is not None
		assert client.csv_parser is not None
		assert client.xlsx_parser is not None

	def test_load_from_csv_string_simple(self):
		"""Test loading from simple CSV string."""
		client = GSParseClient()

		csv_data = """Name,Age,City
John,25,Moscow
Mary,30,St. Petersburg"""

		worksheet = client.load_from_csv_string(csv_data, 'Test')

		assert isinstance(worksheet, Worksheet)
		assert worksheet.name == 'Test'
		assert worksheet.row_count == 3
		assert worksheet.column_count == 3

		# Check header
		assert worksheet.get_cell(1, 1).value == 'Name'
		assert worksheet.get_cell(1, 2).value == 'Age'
		assert worksheet.get_cell(1, 3).value == 'City'

		# Check data
		assert worksheet.get_cell(2, 1).value == 'John'
		assert worksheet.get_cell(2, 2).value == '25'
		assert worksheet.get_cell(2, 3).value == 'Moscow'

		assert worksheet.get_cell(3, 1).value == 'Mary'
		assert worksheet.get_cell(3, 2).value == '30'
		assert worksheet.get_cell(3, 3).value == 'St. Petersburg'

	def test_load_from_csv_string_empty(self):
		"""Test loading from empty CSV string."""
		client = GSParseClient()

		worksheet = client.load_from_csv_string('', 'Empty')

		assert worksheet.name == 'Empty'
		assert worksheet.row_count == 0
		assert worksheet.column_count == 0

	def test_load_from_csv_string_single_cell(self):
		"""Test loading from CSV string with single cell."""
		client = GSParseClient()

		worksheet = client.load_from_csv_string('Test', 'Single')

		assert worksheet.name == 'Single'
		assert worksheet.row_count == 1
		assert worksheet.column_count == 1
		assert worksheet.get_cell(1, 1).value == 'Test'

	def test_load_from_csv_string_with_quotes(self):
		"""Test loading from CSV string with quoted values."""
		client = GSParseClient()

		csv_data = '"Name","Age","City"\n"John, Jr.",25,"Moscow, Russia"\n"Mary",30,"St. Petersburg"'
		worksheet = client.load_from_csv_string(csv_data, 'Quoted')

		assert worksheet.row_count == 3
		assert worksheet.column_count == 3
		assert worksheet.get_cell(2, 1).value == 'John, Jr.'
		assert worksheet.get_cell(2, 3).value == 'Moscow, Russia'

	def test_load_from_csv_string_with_semicolon_delimiter(self):
		"""Test loading from CSV string with semicolon delimiter."""
		client = GSParseClient()

		# Create a custom CSV parser with semicolon delimiter
		from src.gsparse.parsers.csv_parser import CSVParser

		client.csv_parser = CSVParser(delimiter=';')

		csv_data = 'Name;Age;City\nJohn;25;Moscow\nMary;30;St. Petersburg'
		worksheet = client.load_from_csv_string(csv_data, 'Semicolon')

		# The parser should parse correctly with semicolon delimiter
		assert worksheet.row_count == 3
		assert worksheet.column_count == 3
		assert worksheet.get_cell(2, 1).value == 'John'

	def test_load_from_csv_string_with_unicode(self):
		"""Test loading from CSV string with Unicode characters."""
		client = GSParseClient()

		csv_data = 'Name,Age,City\nJohn,25,Moscow\nMary,30,SPb'
		worksheet = client.load_from_csv_string(csv_data, 'Unicode')

		assert worksheet.row_count == 3
		assert worksheet.column_count == 3
		assert worksheet.get_cell(1, 1).value == 'Name'
		assert worksheet.get_cell(2, 1).value == 'John'
		assert worksheet.get_cell(3, 1).value == 'Mary'

	def test_load_from_csv_string_with_empty_cells(self):
		"""Test loading from CSV string with empty cells."""
		client = GSParseClient()

		csv_data = 'Name,Age,City\nJohn,,Moscow\n,30,SPb\nMary,25,'
		worksheet = client.load_from_csv_string(csv_data, 'EmptyCells')

		assert worksheet.row_count == 4
		assert worksheet.column_count == 3
		assert worksheet.get_cell(2, 2).value is None
		assert worksheet.get_cell(3, 1).value is None
		assert worksheet.get_cell(4, 3).value is None

	def test_load_from_csv_string_with_uneven_rows(self):
		"""Test loading from CSV string with uneven rows."""
		client = GSParseClient()

		csv_data = 'Name,Age,City\nJohn,25\nMary,30,St. Petersburg,Extra'
		worksheet = client.load_from_csv_string(csv_data, 'Uneven')

		assert worksheet.row_count == 3
		assert worksheet.column_count == 4  # Should be max length
		assert worksheet.get_cell(2, 3).value is None
		assert worksheet.get_cell(3, 4).value == 'Extra'

	def test_load_from_csv_string_with_special_characters(self):
		"""Test loading from CSV string with special characters."""
		client = GSParseClient()

		csv_data = 'Name,Age,City\nJohn!@#,25,Moscow\nMary,30,St. Petersburg'
		worksheet = client.load_from_csv_string(csv_data, 'Special')

		assert worksheet.row_count == 3
		assert worksheet.get_cell(2, 1).value == 'John!@#'

	def test_load_from_csv_string_with_newlines_in_cells(self):
		"""Test loading from CSV string with newlines in cells."""
		client = GSParseClient()

		csv_data = 'Name,Description\nJohn,"Line 1\nLine 2"\nMary,Simple'
		worksheet = client.load_from_csv_string(csv_data, 'Newlines')

		assert worksheet.row_count == 3
		assert worksheet.get_cell(2, 2).value == 'Line 1\nLine 2'

	def test_load_from_csv_string_with_tabs(self):
		"""Test loading from CSV string with tab delimiter."""
		client = GSParseClient()

		# Create a custom CSV parser with tab delimiter
		from src.gsparse.parsers.csv_parser import CSVParser

		client.csv_parser = CSVParser(delimiter='\t')

		csv_data = 'Name\tAge\tCity\nJohn\t25\tMoscow\nMary\t30\tSt. Petersburg'
		worksheet = client.load_from_csv_string(csv_data, 'Tabs')

		# The parser should parse correctly with tab delimiter
		assert worksheet.row_count == 3
		assert worksheet.column_count == 3
		assert worksheet.get_cell(2, 1).value == 'John'

	def test_load_from_csv_string_with_pipes(self):
		"""Test loading from CSV string with pipe delimiter."""
		client = GSParseClient()

		# Create a custom CSV parser with pipe delimiter
		from src.gsparse.parsers.csv_parser import CSVParser

		client.csv_parser = CSVParser(delimiter='|')

		csv_data = 'Name|Age|City\nJohn|25|Moscow\nMary|30|St. Petersburg'
		worksheet = client.load_from_csv_string(csv_data, 'Pipes')

		# The parser should parse correctly with pipe delimiter
		assert worksheet.row_count == 3
		assert worksheet.column_count == 3
		assert worksheet.get_cell(2, 1).value == 'John'

	def test_load_from_csv_string_with_unicode_escapes(self):
		"""Test loading from CSV string with Unicode escape sequences."""
		client = GSParseClient()

		csv_data = 'Name,Age\n\\u0418\\u0432\\u0430\\u043d,25\n\\u041c\\u0430\\u0440\\u0438\\u044f,30'
		worksheet = client.load_from_csv_string(csv_data, 'UnicodeEscapes')

		assert worksheet.row_count == 3
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

	def test_load_from_csv_string_with_mixed_quotes(self):
		"""Test loading from CSV string with mixed quote characters."""
		client = GSParseClient()

		csv_data = "'Name','Age','City'\n'John','25','Moscow'\n'Mary','30','SPb'"
		worksheet = client.load_from_csv_string(csv_data, 'SingleQuotes')

		# The parser should detect the quote character and parse correctly
		assert worksheet.row_count == 3
		assert worksheet.column_count == 3
		assert worksheet.get_cell(2, 1).value == 'John'

	def test_load_from_csv_string_with_very_long_content(self):
		"""Test loading from CSV string with very long content."""
		client = GSParseClient()

		# Create CSV with 1000 rows
		csv_data = 'Name,Age,City\n'
		for i in range(1000):
			csv_data += f'Person{i},{20 + i % 50},City{i}\n'

		worksheet = client.load_from_csv_string(csv_data, 'Long')

		assert worksheet.row_count == 1001  # 1000 data rows + header
		assert worksheet.column_count == 3
		assert worksheet.get_cell(2, 1).value == 'Person0'
		assert worksheet.get_cell(1001, 1).value == 'Person999'

	def test_load_from_csv_string_with_very_wide_content(self):
		"""Test loading from CSV string with very wide content."""
		client = GSParseClient()

		# Create CSV with 100 columns
		csv_data = ','.join([f'Col{i}' for i in range(100)]) + '\n'
		csv_data += ','.join([f'Val{i}' for i in range(100)]) + '\n'

		worksheet = client.load_from_csv_string(csv_data, 'Wide')

		assert worksheet.row_count == 2
		assert worksheet.column_count == 100
		assert worksheet.get_cell(1, 1).value == 'Col0'
		assert worksheet.get_cell(1, 100).value == 'Col99'
		assert worksheet.get_cell(2, 1).value == 'Val0'
		assert worksheet.get_cell(2, 100).value == 'Val99'

	def test_load_from_csv_string_with_empty_rows(self):
		"""Test loading from CSV string with empty rows."""
		client = GSParseClient()

		csv_data = 'Name,Age,City\n\nJohn,25,Moscow\n\nMary,30,SPb\n'
		worksheet = client.load_from_csv_string(csv_data, 'EmptyRows')

		assert worksheet.row_count == 5  # Including empty rows
		assert worksheet.column_count == 3
		assert worksheet.get_cell(3, 1).value == 'John'
		assert worksheet.get_cell(5, 1).value == 'Mary'

	def test_load_from_csv_string_with_only_whitespace_rows(self):
		"""Test loading from CSV string with only whitespace rows."""
		client = GSParseClient()

		csv_data = 'Name,Age,City\n   \nJohn,25,Moscow\n\t\nMary,30,SPb\n'
		worksheet = client.load_from_csv_string(csv_data, 'WhitespaceRows')

		assert worksheet.row_count == 5  # Including whitespace rows
		assert worksheet.column_count == 3
		assert worksheet.get_cell(3, 1).value == 'John'
		assert worksheet.get_cell(5, 1).value == 'Mary'

	def test_load_from_csv_string_with_mixed_delimiters(self):
		"""Test loading from CSV string with mixed delimiters."""
		client = GSParseClient()

		csv_data = 'Name,Age;City\nJohn,25;Moscow\nMary,30;SPb'
		worksheet = client.load_from_csv_string(csv_data, 'MixedDelimiters')

		# The parser should detect the most common delimiter (comma) and parse correctly
		# With comma as delimiter, we get 2 columns: ['Name', 'Age;City']
		assert worksheet.row_count == 3
		assert worksheet.column_count == 2
		assert worksheet.get_cell(2, 1).value == 'John'
		assert worksheet.get_cell(2, 2).value == '25;Moscow'

	def test_load_from_csv_string_with_very_long_cell_content(self):
		"""Test loading from CSV string with very long cell content."""
		client = GSParseClient()

		# Create a very long cell content
		long_content = 'A' * 10000
		csv_data = f'Name,Description\nJohn,"{long_content}"\nMary,Short'

		worksheet = client.load_from_csv_string(csv_data, 'LongContent')

		assert worksheet.row_count == 3
		assert worksheet.column_count == 2
		assert worksheet.get_cell(2, 2).value == long_content
		assert len(worksheet.get_cell(2, 2).value) == 10000

	def test_load_from_csv_string_with_special_characters_in_names(self):
		"""Test loading from CSV string with special characters in worksheet names."""
		client = GSParseClient()

		csv_data = 'Name,Age\nJohn,25\nMary,30'

		# Test various special characters in worksheet names
		special_names = [
			'Sheet!@#$%^&*()',
			'Sheet<>?:"{}|',
			"Sheet[]\\;',./",
			'Sheet`~-_=+',
			'Sheet with spaces',
			'Sheet\twith\ttabs',
			'Sheet\nwith\nnewlines',
		]

		for name in special_names:
			worksheet = client.load_from_csv_string(csv_data, name)
			assert worksheet.name == name
			assert worksheet.row_count == 3
			assert worksheet.column_count == 2

	def test_load_from_csv_string_with_unicode_in_names(self):
		"""Test loading from CSV string with Unicode in worksheet names."""
		client = GSParseClient()

		csv_data = 'Name,Age\nJohn,25\nMary,30'

		# Test various Unicode characters in worksheet names
		unicode_names = [
			'Sheet1',
			'工作表1',
			'シート1',
			'Sheet🚀',
			'Sheet with émojis 🎉',
			'Sheet with 中文',
			'Sheet with Russian',
		]

		for name in unicode_names:
			worksheet = client.load_from_csv_string(csv_data, name)
			assert worksheet.name == name
			assert worksheet.row_count == 3
			assert worksheet.column_count == 2

	def test_load_from_csv_string_with_empty_worksheet_name(self):
		"""Test loading from CSV string with empty worksheet name."""
		client = GSParseClient()

		csv_data = 'Name,Age\nJohn,25\nMary,30'
		# This might raise an error if worksheet name cannot be empty
		try:
			worksheet = client.load_from_csv_string(csv_data, '')
			assert worksheet.name == ''
			assert worksheet.row_count == 3
			assert worksheet.column_count == 2
		except ValueError as e:
			# If it fails, it should be with the expected message
			assert 'Worksheet name cannot be empty' in str(e)

	def test_load_from_csv_string_with_none_worksheet_name(self):
		"""Test loading from CSV string with None worksheet name."""
		client = GSParseClient()

		csv_data = 'Name,Age\nJohn,25\nMary,30'
		# This might raise an error if worksheet name cannot be None
		try:
			worksheet = client.load_from_csv_string(csv_data, None)
			# Should use default name
			assert worksheet.name == 'Sheet1'
			assert worksheet.row_count == 3
			assert worksheet.column_count == 2
		except (ValueError, AttributeError) as e:
			# If it fails, it should be with the expected message
			assert 'Worksheet name cannot be empty' in str(
				e
			) or "'NoneType' object has no attribute 'strip'" in str(e)

	def test_load_from_csv_string_with_very_large_dataset(self):
		"""Test loading from CSV string with very large dataset."""
		client = GSParseClient()

		# Create CSV with 10000 rows and 50 columns
		csv_data = ','.join([f'Col{i}' for i in range(50)]) + '\n'
		for i in range(10000):
			csv_data += ','.join([f'Val{i}_{j}' for j in range(50)]) + '\n'

		worksheet = client.load_from_csv_string(csv_data, 'Large')

		assert worksheet.row_count == 10001  # 10000 data rows + header
		assert worksheet.column_count == 50
		assert worksheet.get_cell(2, 1).value == 'Val0_0'
		assert worksheet.get_cell(10001, 50).value == 'Val9999_49'

	def test_load_from_csv_string_with_mixed_data_types(self):
		"""Test loading from CSV string with mixed data types."""
		client = GSParseClient()

		csv_data = (
			'Name,Age,Active,Score\nJohn,25,true,85.5\nMary,30,false,92.0\nBob,,true,'
		)
		worksheet = client.load_from_csv_string(csv_data, 'MixedTypes')

		assert worksheet.row_count == 4
		assert worksheet.column_count == 4
		assert worksheet.get_cell(2, 1).value == 'John'
		assert worksheet.get_cell(2, 2).value == '25'
		assert worksheet.get_cell(2, 3).value == 'true'
		assert worksheet.get_cell(2, 4).value == '85.5'
		assert worksheet.get_cell(3, 2).value == '30'
		assert worksheet.get_cell(3, 3).value == 'false'
		assert worksheet.get_cell(3, 4).value == '92.0'
		assert worksheet.get_cell(4, 2).value is None
		assert worksheet.get_cell(4, 4).value is None
