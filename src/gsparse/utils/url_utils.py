"""Utilities for working with URLs."""

import logging
import re
from typing import Optional, Dict, Any
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)


class URLUtils:
	"""Utilities for working with Google Sheets URLs."""
	
	@staticmethod
	def extract_sheet_id(url: str) -> Optional[str]:
		"""Extracts sheet ID from URL.
		
		Args:
			url: Google Sheets URL
			
		Returns:
			Sheet ID or None
		"""
		patterns = [
			r"/spreadsheets/d/([a-zA-Z0-9-_]+)",
			r"id=([a-zA-Z0-9-_]+)",
			r"key=([a-zA-Z0-9-_]+)",
		]
		
		for pattern in patterns:
			match = re.search(pattern, url)
			if match:
				return match.group(1)
		
		return None
	
	@staticmethod
	def extract_gid(url: str) -> Optional[str]:
		"""Extracts worksheet GID from URL.
		
		Args:
			url: Google Sheets URL
			
		Returns:
			Worksheet GID or None
		"""
		parsed = urlparse(url)
		query_params = parse_qs(parsed.query)
		
		if 'gid' in query_params:
			return query_params['gid'][0]
		
		return None
	
	@staticmethod
	def is_google_sheets_url(url: str) -> bool:
		"""Checks if URL is a Google Sheets URL."""
		parsed = urlparse(url)
		return (
			parsed.netloc in ["docs.google.com", "drive.google.com"] and
			URLUtils.extract_sheet_id(url) is not None
		)
	
	@staticmethod
	def normalize_url(url: str) -> str:
		"""Normalizes Google Sheets URL.
		
		Args:
			url: Original URL
			
		Returns:
			Normalized URL
		"""
		sheet_id = URLUtils.extract_sheet_id(url)
		if not sheet_id:
			raise ValueError("Failed to extract sheet ID from URL")
		
		return f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"
	
	@staticmethod
	def get_public_url(url: str) -> str:
		"""Converts URL to public format.
		
		Args:
			url: Original URL
			
		Returns:
			Public URL
		"""
		sheet_id = URLUtils.extract_sheet_id(url)
		if not sheet_id:
			raise ValueError("Failed to extract sheet ID from URL")
		
		return f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit#gid=0"
