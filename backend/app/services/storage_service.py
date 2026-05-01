"""
Storage Service - local filesystem and Supabase storage support
"""
import mimetypes
import os
import tempfile
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import httpx

from app.config import (
	settings,
	AUDIO_DIR,
	AVATARS_DIR,
	UPLOADS_DIR,
)

try:
	from supabase import create_client
except Exception:  # pragma: no cover - fallback when dependency missing locally
	create_client = None


class StorageService:
	def __init__(self):
		self.backend = (settings.STORAGE_BACKEND or "local").lower()
		self._supabase = None

		if self.backend == "supabase" and create_client and settings.SUPABASE_URL and settings.SUPABASE_SERVICE_ROLE_KEY:
			self._supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)

		os.makedirs(AUDIO_DIR, exist_ok=True)
		os.makedirs(AVATARS_DIR, exist_ok=True)
		os.makedirs(UPLOADS_DIR, exist_ok=True)

	@property
	def is_supabase_enabled(self) -> bool:
		return self._supabase is not None

	def _bucket_for_category(self, category: str) -> str:
		category = (category or "").lower()
		if category == "avatars":
			return settings.SUPABASE_BUCKET_AVATARS
		if category == "audio":
			return settings.SUPABASE_BUCKET_AUDIO
		return settings.SUPABASE_BUCKET_UPLOADS

	def _local_dir_for_category(self, category: str) -> str:
		category = (category or "").lower()
		if category == "avatars":
			return AVATARS_DIR
		if category == "audio":
			return AUDIO_DIR
		return UPLOADS_DIR

	def _local_public_url(self, category: str, filename: str) -> str:
		return f"/static/{category}/{filename}"

	def save_bytes(self, data: bytes, filename: str, category: str, content_type: Optional[str] = None) -> str:
		"""
		Save bytes to storage.

		Returns a URL-like reference:
		- Supabase public URL when enabled
		- /static/... URL when using local storage
		"""
		if self.is_supabase_enabled:
			bucket = self._bucket_for_category(category)
			path = filename
			guessed_type = content_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"
			self._supabase.storage.from_(bucket).upload(
				file=data,
				path=path,
				file_options={"content-type": guessed_type, "upsert": "true"},
			)
			return self._supabase.storage.from_(bucket).get_public_url(path)

		target_dir = self._local_dir_for_category(category)
		os.makedirs(target_dir, exist_ok=True)
		target_path = os.path.join(target_dir, filename)
		with open(target_path, "wb") as f:
			f.write(data)
		return self._local_public_url(category, filename)

	def save_file(self, file_path: str, filename: Optional[str], category: str, content_type: Optional[str] = None) -> str:
		"""Save local file contents to storage and return URL reference."""
		file_name = filename or Path(file_path).name
		with open(file_path, "rb") as f:
			data = f.read()
		return self.save_bytes(data, file_name, category, content_type)

	def resolve_to_local_path(self, reference: Optional[str], expected_suffix: str = ".wav") -> Optional[str]:
		"""
		Resolve stored reference to local filesystem path.

		- Local absolute paths are returned directly
		- /static/... URLs map to local static directories
		- Remote URLs are downloaded to a temp file
		"""
		if not reference:
			return None

		# Absolute local path
		if os.path.isabs(reference) and os.path.exists(reference):
			return reference

		# Static URL format
		if reference.startswith("/static/"):
			relative = reference.lstrip("/")
			local_path = os.path.join(Path(__file__).resolve().parents[2], relative)
			if os.path.exists(local_path):
				return local_path

		# Remote URL
		if reference.startswith("http://") or reference.startswith("https://"):
			suffix = Path(urlparse(reference).path).suffix or expected_suffix
			with httpx.Client(timeout=30.0, follow_redirects=True) as client:
				resp = client.get(reference)
				resp.raise_for_status()
				with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
					temp.write(resp.content)
					return temp.name

		# Relative local path fallback
		if os.path.exists(reference):
			return reference

		return None

	def delete_reference(self, reference: Optional[str], category: Optional[str] = None) -> None:
		"""Delete an asset reference from whichever backend is used."""
		if not reference:
			return

		# Delete local absolute/relative path
		if os.path.exists(reference):
			os.remove(reference)
			return

		# Delete /static mapped file
		if reference.startswith("/static/"):
			relative = reference.lstrip("/")
			local_path = os.path.join(Path(__file__).resolve().parents[2], relative)
			if os.path.exists(local_path):
				os.remove(local_path)
			return

		# Delete Supabase object by URL
		if self.is_supabase_enabled and (reference.startswith("http://") or reference.startswith("https://")):
			path = Path(urlparse(reference).path).name
			bucket = self._bucket_for_category(category or "uploads")
			self._supabase.storage.from_(bucket).remove([path])


storage_service = StorageService()
