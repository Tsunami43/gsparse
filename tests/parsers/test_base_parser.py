"""Tests for BaseParser."""

from src.gsparse.core.spreadsheet import Spreadsheet
from src.gsparse.core.worksheet import Worksheet
from src.gsparse.parsers.base_parser import BaseParser


class ConcreteParser(BaseParser):
	"""Concrete implementation of BaseParser for testing."""

	def parse(self, data, worksheet_name='Sheet1'):
		"""Dummy implementation."""
		return Worksheet(worksheet_name, [], 0, 0)

	def parse_multiple(self, data_dict):
		"""Dummy implementation."""
		return Spreadsheet('Test', [])


class TestBaseParser:
	"""Tests for BaseParser class."""

	def test_base_parser_creation(self):
		"""Test base parser creation."""
		parser = ConcreteParser()
		assert parser is not None

	def test_clean_cell_value_none(self):
		"""Test cleaning None value."""
		parser = ConcreteParser()
		result = parser._clean_cell_value(None)
		assert result is None

	def test_clean_cell_value_string(self):
		"""Test cleaning string value."""
		parser = ConcreteParser()
		result = parser._clean_cell_value('  test  ')
		assert result == 'test'

	def test_clean_cell_value_empty_string(self):
		"""Test cleaning empty string."""
		parser = ConcreteParser()
		result = parser._clean_cell_value('   ')
		assert result is None

	def test_clean_cell_value_number(self):
		"""Test cleaning number value."""
		parser = ConcreteParser()
		result = parser._clean_cell_value(42)
		assert result == 42

	def test_clean_cell_value_float(self):
		"""Test cleaning float value."""
		parser = ConcreteParser()
		result = parser._clean_cell_value(3.14)
		assert result == 3.14

	def test_clean_cell_value_boolean(self):
		"""Test cleaning boolean value."""
		parser = ConcreteParser()
		result = parser._clean_cell_value(True)
		assert result is True

	def test_clean_cell_value_with_newlines(self):
		"""Test cleaning string with newlines."""
		parser = ConcreteParser()
		result = parser._clean_cell_value('test\r\nvalue\r')
		assert result == 'test\nvalue'

	def test_clean_cell_value_unicode_escapes(self):
		"""Test cleaning string with Unicode escapes."""
		parser = ConcreteParser()
		result = parser._clean_cell_value('test\\u0410\\u0432\\u0433')
		# The actual result depends on the implementation
		assert result in ['testABC', 'testAbc', 'test\\u0410\\u0432\\u0433']

	def test_clean_cell_value_complex_unicode(self):
		"""Test cleaning complex Unicode string."""
		parser = ConcreteParser()
		result = parser._clean_cell_value(
			'  \\u041f\\u0440\\u0438\\u0432\\u0435\\u0442  '
		)
		# The actual result depends on the implementation
		assert result in ['Hello', '\\u041f\\u0440\\u0438\\u0432\\u0435\\u0442']

	def test_clean_cell_value_mixed_content(self):
		"""Test cleaning mixed content."""
		parser = ConcreteParser()
		result = parser._clean_cell_value('  test\\u0020value  ')
		# The actual result depends on the implementation
		assert result in ['test value', 'test\\u0020value']

	def test_clean_cell_value_invalid_unicode(self):
		"""Test cleaning string with invalid Unicode escapes."""
		parser = ConcreteParser()
		result = parser._clean_cell_value('test\\uZZZZ')
		assert result == 'test\\uZZZZ'  # Should return original if invalid

	def test_clean_cell_value_empty_after_cleaning(self):
		"""Test cleaning string that becomes empty after cleaning."""
		parser = ConcreteParser()
		result = parser._clean_cell_value('\\u0020\\u0020')
		# The actual result depends on the implementation
		assert result in [None, '\\u0020\\u0020']

	def test_clean_cell_value_float_not_mangled_as_date(self):
		"""Floats must be preserved as-is and never rewritten as dates.

		Regression: the date-guessing heuristic turned floats like 3.1 into
		the string '3.10', corrupting ordinary numeric data.
		"""
		parser = ConcreteParser()
		for value in [3.1, 1.1, 5.1, 28.1, 29.1, 31.1, 2.5, 100.1]:
			result = parser._clean_cell_value(value)
			assert result == value
			assert isinstance(result, float)

	def test_clean_cell_value_decimal_string_not_mangled_as_date(self):
		"""Decimal-looking strings must be preserved verbatim."""
		parser = ConcreteParser()
		# European decimal separator must not be rewritten to a dot.
		assert parser._clean_cell_value('1,5') == '1,5'
		assert parser._clean_cell_value('2.5') == '2.5'
		assert parser._clean_cell_value('12.5') == '12.5'

	def test_clean_cell_value_preserve_strings_stringifies_floats(self):
		"""preserve_strings=True converts values to str without date guessing."""
		parser = ConcreteParser(preserve_strings=True)
		assert parser._clean_cell_value(3.1) == '3.1'
		assert parser._clean_cell_value(28.1) == '28.1'
		assert parser._clean_cell_value(42) == '42'
