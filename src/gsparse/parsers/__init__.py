"""Модули для парсинга скачанных данных."""

from .csv_parser import CSVParser
from .xlsx_parser import XLSXParser
from .base_parser import BaseParser

__all__ = ["CSVParser", "XLSXParser", "BaseParser"]
