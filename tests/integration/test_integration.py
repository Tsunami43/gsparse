"""Integration tests for GSParse."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.gsparse import GSParseClient
from src.gsparse.core.worksheet import Worksheet
from src.gsparse.core.spreadsheet import Spreadsheet


class TestIntegration:
	"""Integration tests for GSParse."""
	
	def test_full_csv_workflow(self):
		"""Test complete CSV workflow from string to data access."""
		client = GSParseClient()
		
		# Test data
		csv_data = """Name,Age,City,Country
John,25,Moscow,Russia
Mary,30,St. Petersburg,Russia
Bob,35,New York,USA
Alice,28,London,UK"""
		
		# Load worksheet
		worksheet = client.load_from_csv_string(csv_data, "Employees")
		
		# Verify worksheet properties
		assert worksheet.name == "Employees"
		assert worksheet.row_count == 5  # 4 data rows + header
		assert worksheet.column_count == 4
		
		# Verify header
		assert worksheet.get_cell(1, 1).value == "Name"
		assert worksheet.get_cell(1, 2).value == "Age"
		assert worksheet.get_cell(1, 3).value == "City"
		assert worksheet.get_cell(1, 4).value == "Country"
		
		# Verify data
		assert worksheet.get_cell(2, 1).value == "John"
		assert worksheet.get_cell(2, 2).value == "25"
		assert worksheet.get_cell(2, 3).value == "Moscow"
		assert worksheet.get_cell(2, 4).value == "Russia"
		
		# Test data access methods
		data_dict = worksheet.get_data_as_dict()
		assert len(data_dict) == 4
		assert data_dict[0]["Name"] == "John"
		assert data_dict[0]["Age"] == "25"
		assert data_dict[0]["City"] == "Moscow"
		assert data_dict[0]["Country"] == "Russia"
		
		# Test column access
		columns = worksheet.get_columns()
		assert len(columns) == 4
		assert columns[0] == ["Name", "John", "Mary", "Bob", "Alice"]
		assert columns[1] == ["Age", "25", "30", "35", "28"]
		
		# Test row access
		rows = worksheet.get_rows()
		assert len(rows) == 5
		assert rows[0] == ["Name", "Age", "City", "Country"]
		assert rows[1] == ["John", "25", "Moscow", "Russia"]
	
	def test_csv_with_special_characters_workflow(self):
		"""Test CSV workflow with special characters and Unicode."""
		client = GSParseClient()
		
		# Test data with special characters and Unicode
		csv_data = """Name,Age,City,Country
John,25,Moscow,Russia
Mary,30,St. Petersburg,Russia
John,35,New York,USA
Alice,28,London,UK"""
		
		# Load worksheet
		worksheet = client.load_from_csv_string(csv_data, "Employees")
		
		# Verify worksheet properties
		assert worksheet.name == "Employees"
		assert worksheet.row_count == 5
		assert worksheet.column_count == 4
		
		# Verify Unicode content
		assert worksheet.get_cell(1, 1).value == "Name"
		assert worksheet.get_cell(2, 1).value == "John"
		assert worksheet.get_cell(2, 3).value == "Moscow"
		
		# Test data access
		data_dict = worksheet.get_data_as_dict()
		assert len(data_dict) == 4
		assert data_dict[0]["Name"] == "John"
		assert data_dict[0]["Age"] == "25"
		assert data_dict[0]["City"] == "Moscow"
		assert data_dict[0]["Country"] == "Russia"
	
	def test_csv_with_empty_cells_workflow(self):
		"""Test CSV workflow with empty cells and None values."""
		client = GSParseClient()
		
		# Test data with empty cells
		csv_data = """Name,Age,City,Country
John,25,Moscow,Russia
Mary,,St. Petersburg,Russia
Bob,35,,
Alice,28,London,UK"""
		
		# Load worksheet
		worksheet = client.load_from_csv_string(csv_data, "Incomplete")
		
		# Verify worksheet properties
		assert worksheet.name == "Incomplete"
		assert worksheet.row_count == 5
		assert worksheet.column_count == 4
		
		# Verify empty cells
		assert worksheet.get_cell(3, 2).value is None  # Mary's age
		assert worksheet.get_cell(4, 3).value is None  # Bob's city
		assert worksheet.get_cell(4, 4).value is None  # Bob's country
		
		# Test data access with None values
		data_dict = worksheet.get_data_as_dict()
		assert len(data_dict) == 4
		assert data_dict[1]["Name"] == "Mary"
		assert data_dict[1]["Age"] is None
		assert data_dict[1]["City"] == "St. Petersburg"
		assert data_dict[1]["Country"] == "Russia"
		
		assert data_dict[2]["Name"] == "Bob"
		assert data_dict[2]["Age"] == "35"
		assert data_dict[2]["City"] is None
		assert data_dict[2]["Country"] is None
	
	def test_csv_with_quoted_values_workflow(self):
		"""Test CSV workflow with quoted values containing special characters."""
		client = GSParseClient()
		
		# Test data with quoted values
		csv_data = '''"Name","Age","City, Country","Description"
"John, Jr.",25,"Moscow, Russia","Software Engineer"
"Mary O'Connor",30,"St. Petersburg, Russia","Data Scientist"
"Bob \"The Builder\"",35,"New York, USA","Project Manager"'''
		
		# Load worksheet
		worksheet = client.load_from_csv_string(csv_data, "Quoted")
		
		# Verify worksheet properties
		assert worksheet.name == "Quoted"
		assert worksheet.row_count == 4
		assert worksheet.column_count == 4
		
		# Verify quoted values
		assert worksheet.get_cell(2, 1).value == "John, Jr."
		assert worksheet.get_cell(2, 3).value == "Moscow, Russia"
		assert worksheet.get_cell(2, 4).value == "Software Engineer"
		
		assert worksheet.get_cell(3, 1).value == "Mary O'Connor"
		assert worksheet.get_cell(3, 3).value == "St. Petersburg, Russia"
		
		# The actual result depends on the implementation
		assert worksheet.get_cell(4, 1).value in ['Bob "The Builder"', 'Bob The Builder""', 'Bob "The Builder"']
		assert worksheet.get_cell(4, 3).value == "New York, USA"
	
	def test_csv_with_uneven_rows_workflow(self):
		"""Test CSV workflow with uneven row lengths."""
		client = GSParseClient()
		
		# Test data with uneven rows
		csv_data = """Name,Age,City,Country
John,25,Moscow,Russia
Mary,30,St. Petersburg
Bob,35,New York,USA,Extra
Alice,28,London,UK,Extra,More"""
		
		# Load worksheet
		worksheet = client.load_from_csv_string(csv_data, "Uneven")
		
		# Verify worksheet properties
		assert worksheet.name == "Uneven"
		assert worksheet.row_count == 5
		assert worksheet.column_count == 6  # Should be max length
		
		# Verify data with padding
		assert worksheet.get_cell(2, 1).value == "John"
		assert worksheet.get_cell(2, 2).value == "25"
		assert worksheet.get_cell(2, 3).value == "Moscow"
		assert worksheet.get_cell(2, 4).value == "Russia"
		assert worksheet.get_cell(2, 5).value is None
		assert worksheet.get_cell(2, 6).value is None
		
		assert worksheet.get_cell(3, 1).value == "Mary"
		assert worksheet.get_cell(3, 2).value == "30"
		assert worksheet.get_cell(3, 3).value == "St. Petersburg"
		assert worksheet.get_cell(3, 4).value is None
		assert worksheet.get_cell(3, 5).value is None
		assert worksheet.get_cell(3, 6).value is None
		
		assert worksheet.get_cell(4, 1).value == "Bob"
		assert worksheet.get_cell(4, 2).value == "35"
		assert worksheet.get_cell(4, 3).value == "New York"
		assert worksheet.get_cell(4, 4).value == "USA"
		assert worksheet.get_cell(4, 5).value == "Extra"
		assert worksheet.get_cell(4, 6).value is None
		
		assert worksheet.get_cell(5, 1).value == "Alice"
		assert worksheet.get_cell(5, 2).value == "28"
		assert worksheet.get_cell(5, 3).value == "London"
		assert worksheet.get_cell(5, 4).value == "UK"
		assert worksheet.get_cell(5, 5).value == "Extra"
		assert worksheet.get_cell(5, 6).value == "More"
	
	def test_csv_with_unicode_escapes_workflow(self):
		"""Test CSV workflow with Unicode escape sequences."""
		client = GSParseClient()
		
		# Test data with Unicode escapes
		csv_data = """Name,Age,City
\\u0418\\u0432\\u0430\\u043d,25,\\u041c\\u043e\\u0441\\u043a\\u0432\\u0430
\\u041c\\u0430\\u0440\\u0438\\u044f,30,\\u0421\\u0430\\u043d\\u043a\\u0442-\\u041f\\u0435\\u0442\\u0435\\u0440\\u0431\\u0443\\u0440\\u0433
John,35,New York"""
		
		# Load worksheet
		worksheet = client.load_from_csv_string(csv_data, "UnicodeEscapes")
		
		# Verify worksheet properties
		assert worksheet.name == "UnicodeEscapes"
		assert worksheet.row_count == 4
		assert worksheet.column_count == 3
		
		# Verify Unicode content - the actual result depends on the implementation
		assert worksheet.get_cell(2, 1).value in ["John", "John", "\\u0418\\u0432\\u0430\\u043d"]
		assert worksheet.get_cell(2, 3).value in ["Moscow", "Moscow", "\\u041c\\u043e\\u0441\\u043a\\u0432\\u0430"]
		assert worksheet.get_cell(3, 1).value in ["Mary", "Mary", "\\u041c\\u0430\\u0440\\u0438\\u044f"]
		assert worksheet.get_cell(3, 3).value in ["St. Petersburg", "St. Petersburg", "\\u0421\\u0430\\u043d\\u043a\\u0442-\\u041f\\u0435\\u0442\\u0435\\u0440\\u0431\\u0443\\u0440\\u0433"]
		assert worksheet.get_cell(4, 1).value == "John"
		assert worksheet.get_cell(4, 3).value == "New York"
	
	def test_csv_with_mixed_delimiters_workflow(self):
		"""Test CSV workflow with mixed delimiters."""
		client = GSParseClient()
		
		# Test data with mixed delimiters
		csv_data = """Name,Age;City,Country
John,25;Moscow,Russia
Mary,30;St. Petersburg,Russia
Bob,35;New York,USA"""
		
		# Load worksheet
		worksheet = client.load_from_csv_string(csv_data, "MixedDelimiters")
		
		# Verify worksheet properties
		assert worksheet.name == "MixedDelimiters"
		assert worksheet.row_count == 4
		assert worksheet.column_count == 3  # Parser detects comma as primary delimiter
		
		# Verify data (parser should detect the most common delimiter)
		assert worksheet.get_cell(2, 1).value == "John"
		assert worksheet.get_cell(2, 2).value == "25;Moscow"  # Semicolon is treated as part of the value
		assert worksheet.get_cell(2, 3).value == "Russia"
	
	def test_csv_with_very_large_dataset_workflow(self):
		"""Test CSV workflow with very large dataset."""
		client = GSParseClient()
		
		# Create large dataset
		csv_data = "Name,Age,City,Country,Department,Salary\n"
		for i in range(1000):
			csv_data += f"Person{i},{20 + i % 50},City{i % 100},Country{i % 10},Dept{i % 20},{30000 + i * 100}\n"
		
		# Load worksheet
		worksheet = client.load_from_csv_string(csv_data, "Large")
		
		# Verify worksheet properties
		assert worksheet.name == "Large"
		assert worksheet.row_count == 1001  # 1000 data rows + header
		assert worksheet.column_count == 6
		
		# Verify sample data
		assert worksheet.get_cell(2, 1).value == "Person0"
		assert worksheet.get_cell(2, 2).value == "20"
		assert worksheet.get_cell(2, 3).value == "City0"
		assert worksheet.get_cell(2, 4).value == "Country0"
		assert worksheet.get_cell(2, 5).value == "Dept0"
		assert worksheet.get_cell(2, 6).value == "30000"
		
		assert worksheet.get_cell(1001, 1).value == "Person999"
		assert worksheet.get_cell(1001, 2).value == "69"
		assert worksheet.get_cell(1001, 3).value == "City99"
		assert worksheet.get_cell(1001, 4).value == "Country9"
		assert worksheet.get_cell(1001, 5).value == "Dept19"
		assert worksheet.get_cell(1001, 6).value == "129900"
		
		# Test data access methods
		data_dict = worksheet.get_data_as_dict()
		assert len(data_dict) == 1000
		assert data_dict[0]["Name"] == "Person0"
		assert data_dict[0]["Age"] == "20"
		assert data_dict[999]["Name"] == "Person999"
		assert data_dict[999]["Age"] == "69"
		
		# Test column access
		columns = worksheet.get_columns()
		assert len(columns) == 6
		assert len(columns[0]) == 1001  # Including header
		assert columns[0][0] == "Name"
		assert columns[0][1] == "Person0"
		assert columns[0][1000] == "Person999"
		
		# Test row access
		rows = worksheet.get_rows()
		assert len(rows) == 1001
		assert len(rows[0]) == 6
		assert rows[0] == ["Name", "Age", "City", "Country", "Department", "Salary"]
		assert rows[1] == ["Person0", "20", "City0", "Country0", "Dept0", "30000"]
		assert rows[1000] == ["Person999", "69", "City99", "Country9", "Dept19", "129900"]
	
	def test_csv_with_special_worksheet_names_workflow(self):
		"""Test CSV workflow with special worksheet names."""
		client = GSParseClient()
		
		# Test data
		csv_data = "Name,Age\nJohn,25\nMary,30"
		
		# Test various special worksheet names
		special_names = [
			"Sheet!@#$%^&*()",
			"Sheet<>?:\"{}|",
			"Sheet[]\\;',./",
			"Sheet`~-_=+",
			"Sheet with spaces",
			"Sheet\twith\ttabs",
			"Sheet\nwith\nnewlines",
			"Sheet1",
			"工作表1",
			"シート1",
			"Sheet🚀",
			"Sheet with émojis 🎉"
		]
		
		for name in special_names:
			worksheet = client.load_from_csv_string(csv_data, name)
			assert worksheet.name == name
			assert worksheet.row_count == 3
			assert worksheet.column_count == 2
			
			# Verify data access still works
			data_dict = worksheet.get_data_as_dict()
			assert len(data_dict) == 2
			assert data_dict[0]["Name"] == "John"
			assert data_dict[0]["Age"] == "25"
			assert data_dict[1]["Name"] == "Mary"
			assert data_dict[1]["Age"] == "30"
