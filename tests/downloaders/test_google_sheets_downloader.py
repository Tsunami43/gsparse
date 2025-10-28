"""Tests for GoogleSheetsDownloader."""

from unittest.mock import Mock, patch

import pytest

from src.gsparse.downloaders.google_sheets_downloader import GoogleSheetsDownloader


class TestGoogleSheetsDownloader:
	"""Tests for GoogleSheetsDownloader class."""

	def test_downloader_creation_default(self):
		"""Test downloader creation with default parameters."""
		downloader = GoogleSheetsDownloader()
		assert downloader.timeout == 30
		assert downloader.session is not None

	def test_downloader_creation_custom(self):
		"""Test downloader creation with custom parameters."""
		downloader = GoogleSheetsDownloader(timeout=60, max_retries=5)
		assert downloader.timeout == 60
		assert downloader.session is not None

	def test_extract_sheet_id_standard_url(self):
		"""Test extracting sheet ID from standard Google Sheets URL."""
		downloader = GoogleSheetsDownloader()
		url = 'https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit'
		sheet_id = downloader.extract_sheet_id(url)
		assert sheet_id == '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'

	def test_extract_sheet_id_with_gid(self):
		"""Test extracting sheet ID from URL with GID parameter."""
		downloader = GoogleSheetsDownloader()
		url = 'https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit#gid=0'
		sheet_id = downloader.extract_sheet_id(url)
		assert sheet_id == '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'

	def test_extract_sheet_id_with_id_param(self):
		"""Test extracting sheet ID from URL with id parameter."""
		downloader = GoogleSheetsDownloader()
		url = 'https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit?id=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
		sheet_id = downloader.extract_sheet_id(url)
		assert sheet_id == '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'

	def test_extract_sheet_id_with_key_param(self):
		"""Test extracting sheet ID from URL with key parameter."""
		downloader = GoogleSheetsDownloader()
		url = 'https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit?key=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
		sheet_id = downloader.extract_sheet_id(url)
		assert sheet_id == '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'

	def test_extract_sheet_id_invalid_url(self):
		"""Test extracting sheet ID from invalid URL."""
		downloader = GoogleSheetsDownloader()
		url = 'https://example.com/not-a-sheet'
		sheet_id = downloader.extract_sheet_id(url)
		assert sheet_id is None

	def test_extract_sheet_id_empty_url(self):
		"""Test extracting sheet ID from empty URL."""
		downloader = GoogleSheetsDownloader()
		sheet_id = downloader.extract_sheet_id('')
		assert sheet_id is None

	def test_is_valid_google_sheets_url_valid(self):
		"""Test validation of valid Google Sheets URL."""
		downloader = GoogleSheetsDownloader()
		url = 'https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit'
		assert downloader.is_valid_google_sheets_url(url) is True

	def test_is_valid_google_sheets_url_drive_domain(self):
		"""Test validation of Google Drive URL."""
		downloader = GoogleSheetsDownloader()
		url = 'https://drive.google.com/file/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/view'
		# This URL doesn't match the patterns in extract_sheet_id, so it should be False
		assert downloader.is_valid_google_sheets_url(url) is False

	def test_is_valid_google_sheets_url_invalid_domain(self):
		"""Test validation of URL with invalid domain."""
		downloader = GoogleSheetsDownloader()
		url = 'https://example.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit'
		assert downloader.is_valid_google_sheets_url(url) is False

	def test_is_valid_google_sheets_url_no_sheet_id(self):
		"""Test validation of URL without sheet ID."""
		downloader = GoogleSheetsDownloader()
		url = 'https://docs.google.com/spreadsheets/'
		assert downloader.is_valid_google_sheets_url(url) is False

	def test_get_export_url_csv(self):
		"""Test getting export URL for CSV format."""
		downloader = GoogleSheetsDownloader()
		sheet_id = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
		url = downloader.get_export_url(sheet_id, 'csv')
		expected = (
			f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv'
		)
		assert url == expected

	def test_get_export_url_xlsx(self):
		"""Test getting export URL for XLSX format."""
		downloader = GoogleSheetsDownloader()
		sheet_id = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
		url = downloader.get_export_url(sheet_id, 'xlsx')
		expected = (
			f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx'
		)
		assert url == expected

	def test_get_export_url_with_gid(self):
		"""Test getting export URL with GID parameter."""
		downloader = GoogleSheetsDownloader()
		sheet_id = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
		url = downloader.get_export_url(sheet_id, 'csv', gid='123456')
		expected = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=123456'
		assert url == expected

	def test_get_export_url_invalid_format(self):
		"""Test getting export URL with invalid format."""
		downloader = GoogleSheetsDownloader()
		sheet_id = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'

		with pytest.raises(ValueError, match='Unsupported format'):
			downloader.get_export_url(sheet_id, 'invalid_format')

	@patch(
		'src.gsparse.downloaders.google_sheets_downloader.GoogleSheetsDownloader.is_valid_google_sheets_url'
	)
	@patch(
		'src.gsparse.downloaders.google_sheets_downloader.GoogleSheetsDownloader.extract_sheet_id'
	)
	@patch(
		'src.gsparse.downloaders.google_sheets_downloader.GoogleSheetsDownloader.get_export_url'
	)
	def test_download_sheet_success(
		self, mock_get_export_url, mock_extract_sheet_id, mock_is_valid
	):
		"""Test successful sheet download."""
		# Setup mocks
		mock_is_valid.return_value = True
		mock_extract_sheet_id.return_value = 'test_sheet_id'
		mock_get_export_url.return_value = 'https://example.com/export'

		# Mock session response
		mock_response = Mock()
		mock_response.content = b'test_csv_data'
		mock_response.raise_for_status.return_value = None

		downloader = GoogleSheetsDownloader()
		downloader.session.get = Mock(return_value=mock_response)

		# Test download
		url = 'https://docs.google.com/spreadsheets/d/test_sheet_id/edit'
		result = downloader.download_sheet(url, 'csv')

		assert result == b'test_csv_data'
		mock_is_valid.assert_called_once_with(url)
		mock_extract_sheet_id.assert_called_once_with(url)
		mock_get_export_url.assert_called_once_with('test_sheet_id', 'csv', None)
		downloader.session.get.assert_called_once_with(
			'https://example.com/export', timeout=30
		)

	def test_download_sheet_invalid_url(self):
		"""Test downloading sheet with invalid URL."""
		downloader = GoogleSheetsDownloader()
		url = 'https://example.com/not-a-sheet'

		with pytest.raises(ValueError, match='Invalid Google Sheets URL'):
			downloader.download_sheet(url, 'csv')

	def test_download_sheet_no_sheet_id(self):
		"""Test downloading sheet when sheet ID cannot be extracted."""
		downloader = GoogleSheetsDownloader()
		# Mock is_valid_google_sheets_url to return True but extract_sheet_id to return None
		with patch.object(downloader, 'is_valid_google_sheets_url', return_value=True):
			with patch.object(downloader, 'extract_sheet_id', return_value=None):
				url = 'https://docs.google.com/spreadsheets/d/invalid/edit'

				with pytest.raises(
					ValueError, match='Failed to extract sheet ID from URL'
				):
					downloader.download_sheet(url, 'csv')

	@patch(
		'src.gsparse.downloaders.google_sheets_downloader.GoogleSheetsDownloader.is_valid_google_sheets_url'
	)
	@patch(
		'src.gsparse.downloaders.google_sheets_downloader.GoogleSheetsDownloader.extract_sheet_id'
	)
	@patch(
		'src.gsparse.downloaders.google_sheets_downloader.GoogleSheetsDownloader.get_export_url'
	)
	def test_download_sheet_request_error(
		self, mock_get_export_url, mock_extract_sheet_id, mock_is_valid
	):
		"""Test sheet download with request error."""
		# Setup mocks
		mock_is_valid.return_value = True
		mock_extract_sheet_id.return_value = 'test_sheet_id'
		mock_get_export_url.return_value = 'https://example.com/export'

		# Mock session to raise exception
		downloader = GoogleSheetsDownloader()
		downloader.session.get = Mock(side_effect=Exception('Network error'))

		url = 'https://docs.google.com/spreadsheets/d/test_sheet_id/edit'

		with pytest.raises(Exception, match='Network error'):
			downloader.download_sheet(url, 'csv')

	def test_get_sheet_info_success(self):
		"""Test getting sheet information."""
		downloader = GoogleSheetsDownloader()
		url = 'https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit'

		with patch.object(downloader, 'is_valid_google_sheets_url', return_value=True):
			with patch.object(
				downloader,
				'extract_sheet_id',
				return_value='1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms',
			):
				info = downloader.get_sheet_info(url)

				assert (
					info['sheet_id'] == '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
				)
				assert info['url'] == url
				assert info['is_public'] is True

	def test_get_sheet_info_invalid_url(self):
		"""Test getting sheet information with invalid URL."""
		downloader = GoogleSheetsDownloader()
		url = 'https://example.com/not-a-sheet'

		with pytest.raises(ValueError, match='Invalid Google Sheets URL'):
			downloader.get_sheet_info(url)

	def test_list_worksheets_success(self):
		"""Test listing worksheets successfully."""
		downloader = GoogleSheetsDownloader()
		url = 'https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit'

		with patch.object(downloader, 'download_sheet', return_value=b'test_data'):
			worksheets = downloader.list_worksheets(url)
			assert worksheets == {'Sheet1': '0'}

	def test_list_worksheets_error(self):
		"""Test listing worksheets with error."""
		downloader = GoogleSheetsDownloader()
		url = 'https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit'

		with patch.object(
			downloader, 'download_sheet', side_effect=Exception('Download error')
		):
			worksheets = downloader.list_worksheets(url)
			assert worksheets is None

	def test_formats_constant(self):
		"""Test that FORMATS constant contains expected formats."""
		downloader = GoogleSheetsDownloader()
		expected_formats = ['csv', 'tsv', 'xlsx', 'ods', 'pdf']

		for format_type in expected_formats:
			assert format_type in downloader.FORMATS

	def test_export_base_url_constant(self):
		"""Test that EXPORT_BASE_URL constant is correct."""
		downloader = GoogleSheetsDownloader()
		expected_url = 'https://docs.google.com/spreadsheets/d/{sheet_id}/export'
		assert downloader.EXPORT_BASE_URL == expected_url

	def test_session_creation_with_retry_strategy(self):
		"""Test that session is created with proper retry strategy."""
		downloader = GoogleSheetsDownloader(max_retries=5)
		session = downloader.session

		# Check that session has adapters mounted
		assert 'http://' in session.adapters
		assert 'https://' in session.adapters

		# Check that adapters have retry strategy
		http_adapter = session.adapters['http://']
		https_adapter = session.adapters['https://']

		assert http_adapter.max_retries.total == 5
		assert https_adapter.max_retries.total == 5
