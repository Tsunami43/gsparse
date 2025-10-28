"""Тесты для GSParseClient."""

import pytest
from src.gsparse import GSParseClient


class TestGSParseClient:
	"""Tests for GSParseClient."""
	
	def test_init(self):
		"""Test client initialization."""
		client = GSParseClient()
		assert client is not None
		assert client.downloader is not None
		assert client.parser is not None
	
	def test_load_from_csv_string(self):
		"""Test loading from CSV string."""
		client = GSParseClient()
		
		csv_data = """Name,Age,City
John,25,Moscow
Mary,30,St. Petersburg"""
		
		worksheet = client.load_from_csv_string(csv_data, "Test")
		
		assert worksheet.name == "Test"
		assert worksheet.row_count == 3  # 2 data rows + header
		assert worksheet.column_count == 3
		
		# Check first cell
		cell = worksheet.get_cell(1, 1)
		assert cell.value == "Name"
		assert cell.address == "A1"
		
		# Check data
		data_dict = worksheet.get_data_as_dict()
		assert len(data_dict) == 2
		assert data_dict[0]["Name"] == "John"
		assert data_dict[0]["Age"] == "25"
		assert data_dict[0]["City"] == "Moscow"
	
	def test_load_from_csv_string_empty(self):
		"""Test loading empty CSV data."""
		client = GSParseClient()
		
		worksheet = client.load_from_csv_string("", "Empty")
		
		assert worksheet.name == "Empty"
		assert worksheet.row_count == 0
		assert worksheet.column_count == 0
	
	def test_load_from_csv_string_single_cell(self):
		"""Test loading CSV with single cell."""
		client = GSParseClient()
		
		worksheet = client.load_from_csv_string("Test", "Single Cell")
		
		assert worksheet.name == "Single Cell"
		assert worksheet.row_count == 1
		assert worksheet.column_count == 1
		
		cell = worksheet.get_cell(1, 1)
		assert cell.value == "Test"
