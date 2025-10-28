"""Downloader for downloading Google Sheets by URL."""

import logging
import re
from typing import Any
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class GoogleSheetsDownloader:
	"""Downloader for downloading Google Sheets in various formats."""

	# Base URLs for Google Sheets export
	EXPORT_BASE_URL = 'https://docs.google.com/spreadsheets/d/{sheet_id}/export'

	# Supported export formats
	FORMATS = {
		'csv': 'csv',
		'tsv': 'tsv',
		'xlsx': 'xlsx',
		'ods': 'ods',
		'pdf': 'pdf',
	}

	def __init__(self, timeout: int = 30, max_retries: int = 3):
		"""Initialize downloader.

		Args:
		    timeout: Request timeout in seconds
		    max_retries: Maximum number of retry attempts
		"""
		self.timeout = timeout
		self.session = self._create_session(max_retries)

	def _create_session(self, max_retries: int) -> requests.Session:
		"""Creates HTTP session with retry settings."""
		session = requests.Session()

		retry_strategy = Retry(
			total=max_retries,
			backoff_factor=1,
			status_forcelist=[429, 500, 502, 503, 504],
		)

		adapter = HTTPAdapter(max_retries=retry_strategy)
		session.mount('http://', adapter)
		session.mount('https://', adapter)

		return session

	def extract_sheet_id(self, url: str) -> str | None:
		"""Extracts sheet ID from Google Sheets URL.

		Args:
		    url: Google Sheets URL

		Returns:
		    Sheet ID or None if extraction failed
		"""
		# Patterns for various Google Sheets URL formats
		patterns = [
			r'/spreadsheets/d/([a-zA-Z0-9-_]+)',
			r'id=([a-zA-Z0-9-_]+)',
			r'key=([a-zA-Z0-9-_]+)',
		]

		for pattern in patterns:
			match = re.search(pattern, url)
			if match:
				return match.group(1)

		return None

	def is_valid_google_sheets_url(self, url: str) -> bool:
		"""Checks if URL is a valid Google Sheets URL."""
		parsed = urlparse(url)
		return (
			parsed.netloc in ['docs.google.com', 'drive.google.com']
			and self.extract_sheet_id(url) is not None
		)

	def get_export_url(
		self, sheet_id: str, format_type: str = 'csv', gid: str | None = None
	) -> str:
		"""Creates URL for sheet export.

		Args:
		    sheet_id: Sheet ID
		    format_type: Export format type
		    gid: Sheet ID (optional)

		Returns:
		    Export URL
		"""
		if format_type not in self.FORMATS:
			raise ValueError(f'Unsupported format: {format_type}')

		url = self.EXPORT_BASE_URL.format(sheet_id=sheet_id)
		params = {'format': self.FORMATS[format_type]}

		if gid:
			params['gid'] = gid

		# Add parameters to URL
		param_string = '&'.join([f'{k}={v}' for k, v in params.items()])
		return f'{url}?{param_string}'

	def download_sheet(
		self, url: str, format_type: str = 'csv', gid: str | None = None
	) -> bytes:
		"""Downloads sheet in specified format.

		Args:
		    url: Google Sheets URL
		    format_type: Export format type
		    gid: Sheet ID (optional)

		Returns:
		    Bytes of downloaded file

		Raises:
		    ValueError: If URL is invalid
		    requests.RequestException: If download error occurred
		"""
		if not self.is_valid_google_sheets_url(url):
			raise ValueError(f'Invalid Google Sheets URL: {url}')

		sheet_id = self.extract_sheet_id(url)
		if not sheet_id:
			raise ValueError('Failed to extract sheet ID from URL')

		export_url = self.get_export_url(sheet_id, format_type, gid)

		try:
			response = self.session.get(export_url, timeout=self.timeout)
			response.raise_for_status()
			return response.content
		except requests.RequestException as e:
			raise requests.RequestException(
				f'Error downloading spreadsheet: {e}'
			) from e

	def get_sheet_info(self, url: str) -> dict[str, Any]:
		"""Gets information about the sheet.

		Args:
		    url: Google Sheets URL

		Returns:
		    Dictionary with sheet information
		"""
		if not self.is_valid_google_sheets_url(url):
			raise ValueError(f'Invalid Google Sheets URL: {url}')

		sheet_id = self.extract_sheet_id(url)
		if not sheet_id:
			raise ValueError('Failed to extract sheet ID from URL')

		# Try to get information via API (if available)
		# For now, return basic information
		return {
			'sheet_id': sheet_id,
			'url': url,
			'is_public': True,  # Assume the sheet is public
		}

	def list_worksheets(self, url: str) -> dict[str, str] | None:
		"""Gets list of worksheets in the sheet.

		Args:
		    url: Google Sheets URL

		Returns:
		    Dictionary {worksheet_name: gid} or None if failed to get
		"""
		# This is a simplified implementation
		# In a real version, need to use Google Sheets API
		# or parse the table's HTML page
		try:
			# Try to download CSV of the first sheet
			self.download_sheet(url, 'csv')
			return {'Sheet1': '0'}  # Assume there's a sheet with gid=0
		except Exception:
			return None
