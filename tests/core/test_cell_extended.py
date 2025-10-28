"""Extended tests for Cell."""

import pytest

from src.gsparse.core.cell import Cell


class TestCellExtended:
	"""Extended tests for Cell class."""

	def test_cell_address_edge_cases(self):
		"""Test cell address generation for edge cases."""
		# Test single letter columns
		assert Cell(1, 1, 'A').address == 'A1'
		assert Cell(1, 26, 'Z').address == 'Z1'

		# Test double letter columns
		assert Cell(1, 27, 'AA').address == 'AA1'
		assert Cell(1, 28, 'AB').address == 'AB1'
		assert Cell(1, 52, 'AZ').address == 'AZ1'
		assert Cell(1, 53, 'BA').address == 'BA1'
		assert Cell(1, 702, 'ZZ').address == 'ZZ1'

		# Test triple letter columns
		assert Cell(1, 703, 'AAA').address == 'AAA1'
		assert Cell(1, 704, 'AAB').address == 'AAB1'

	def test_cell_address_large_numbers(self):
		"""Test cell address generation with large row numbers."""
		assert Cell(1000, 1, 'A').address == 'A1000'
		assert Cell(9999, 26, 'Z').address == 'Z9999'
		assert Cell(10000, 27, 'AA').address == 'AA10000'

	def test_cell_validation_negative_values(self):
		"""Test cell validation with negative values."""
		with pytest.raises(ValueError):
			Cell(-1, 1, 'Test')

		with pytest.raises(ValueError):
			Cell(1, -1, 'Test')

		with pytest.raises(ValueError):
			Cell(-1, -1, 'Test')

	def test_cell_validation_zero_values(self):
		"""Test cell validation with zero values."""
		with pytest.raises(ValueError):
			Cell(0, 1, 'Test')

		with pytest.raises(ValueError):
			Cell(1, 0, 'Test')

		with pytest.raises(ValueError):
			Cell(0, 0, 'Test')

	def test_cell_validation_float_values(self):
		"""Test cell validation with float values."""
		# Dataclass accepts float values without type checking
		# This results in invalid addresses
		cell1 = Cell(1.5, 1, 'Test')
		assert cell1.row == 1.5
		assert cell1.column == 1
		assert cell1.address == 'A1.5'  # Invalid but computed

		# This should raise an error in __post_init__ when converting column to letter
		with pytest.raises(
			TypeError, match="'float' object cannot be interpreted as an integer"
		):
			Cell(1, 1.5, 'Test')

	def test_cell_validation_string_values(self):
		"""Test cell validation with string values."""
		with pytest.raises(
			TypeError, match="'<' not supported between instances of 'str' and 'int'"
		):
			Cell('1', 1, 'Test')

		with pytest.raises(
			TypeError, match="'<' not supported between instances of 'str' and 'int'"
		):
			Cell(1, '1', 'Test')

	def test_cell_empty_various_types(self):
		"""Test cell emptiness with various data types."""
		# None
		assert Cell(1, 1, None).is_empty is True

		# Empty string
		assert Cell(1, 1, '').is_empty is True

		# Whitespace only
		assert Cell(1, 1, '   ').is_empty is True
		assert Cell(1, 1, '\t').is_empty is True
		assert Cell(1, 1, '\n').is_empty is True
		assert Cell(1, 1, '\r\n').is_empty is True

		# Mixed whitespace
		assert Cell(1, 1, ' \t\n ').is_empty is True

		# Non-empty values
		assert Cell(1, 1, '0').is_empty is False
		assert Cell(1, 1, 'false').is_empty is False
		assert Cell(1, 1, 0).is_empty is False
		assert Cell(1, 1, False).is_empty is False
		assert Cell(1, 1, []).is_empty is False
		assert Cell(1, 1, {}).is_empty is False

	def test_cell_value_types(self):
		"""Test cell with different value types."""
		# String
		cell = Cell(1, 1, 'Hello')
		assert cell.value == 'Hello'
		assert not cell.is_empty

		# Integer
		cell = Cell(1, 1, 42)
		assert cell.value == 42
		assert not cell.is_empty

		# Float
		cell = Cell(1, 1, 3.14)
		assert cell.value == 3.14
		assert not cell.is_empty

		# Boolean
		cell = Cell(1, 1, True)
		assert cell.value is True
		assert not cell.is_empty

		# List
		cell = Cell(1, 1, [1, 2, 3])
		assert cell.value == [1, 2, 3]
		assert not cell.is_empty

		# Dict
		cell = Cell(1, 1, {'key': 'value'})
		assert cell.value == {'key': 'value'}
		assert not cell.is_empty

	def test_cell_unicode_values(self):
		"""Test cell with Unicode values."""
		cell = Cell(1, 1, 'Hello')
		assert cell.value == 'Hello'
		assert not cell.is_empty

		cell = Cell(1, 1, 'Hello 世界')
		assert cell.value == 'Hello 世界'
		assert not cell.is_empty

		cell = Cell(1, 1, '🚀')
		assert cell.value == '🚀'
		assert not cell.is_empty

	def test_cell_special_characters(self):
		"""Test cell with special characters."""
		special_values = [
			'!@#$%^&*()',
			'<>?:"{}|',
			"[]\\;',./",
			'`~-_=+',
			' \t\n\r ',
			'',
			'   ',
		]

		for value in special_values:
			cell = Cell(1, 1, value)
			assert cell.value == value
			if value.strip():
				assert not cell.is_empty
			else:
				assert cell.is_empty

	def test_cell_large_values(self):
		"""Test cell with large values."""
		# Large integer
		cell = Cell(1, 1, 999999999999999999)
		assert cell.value == 999999999999999999
		assert not cell.is_empty

		# Large float
		cell = Cell(1, 1, 3.14159265358979323846264338327950288419716939937510)
		assert cell.value == 3.14159265358979323846264338327950288419716939937510
		assert not cell.is_empty

		# Very long string
		long_string = 'A' * 10000
		cell = Cell(1, 1, long_string)
		assert cell.value == long_string
		assert not cell.is_empty

	def test_cell_equality(self):
		"""Test cell equality."""
		cell1 = Cell(1, 1, 'Test')
		cell2 = Cell(1, 1, 'Test')
		cell3 = Cell(1, 1, 'Different')
		cell4 = Cell(2, 1, 'Test')
		cell5 = Cell(1, 2, 'Test')

		# Same cell
		assert cell1 == cell1

		# Different objects with same values
		assert cell1 == cell2

		# Different values
		assert cell1 != cell3

		# Different positions
		assert cell1 != cell4
		assert cell1 != cell5

	def test_cell_string_representation(self):
		"""Test cell string representation."""
		cell = Cell(1, 1, 'Test')
		cell_str = str(cell)
		assert 'Test' in cell_str
		assert '1' in cell_str  # Row number should be in string representation

	def test_cell_repr(self):
		"""Test cell repr representation."""
		cell = Cell(1, 1, 'Test')
		cell_repr = repr(cell)
		assert 'Cell' in cell_repr
		assert '1' in cell_repr
		assert 'Test' in cell_repr
		# repr shows the dataclass representation, not the address
		assert 'row=1' in cell_repr
		assert 'column=1' in cell_repr
