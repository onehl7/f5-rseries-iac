"""
UCS Archive Extractor for F5 iSeries migration assessment.
Extracts TMOS UCS (User Configuration Set) archives and retrieves core configuration files:
- config/bigip.conf
- config/bigip_base.conf
- config/bigip_gtm.conf
- ssl certificates and keys
"""

import os
import tarfile
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Optional, List


class UCSExtractor:
    """Extracts and catalogs configuration files from an F5 BIG-IP UCS archive."""

    CORE_CONFIG_FILES = [
        "config/bigip.conf",
        "config/bigip_base.conf",
        "config/bigip_gtm.conf",
        "config/bigip_user.conf",
    ]

    def __init__(self, ucs_path: str):
        self.ucs_path = Path(ucs_path)
        if not self.ucs_path.is_file():
            raise FileNotFoundError(f"UCS archive not found at: {ucs_path}")
        self._temp_dir: Optional[str] = None

    def extract(self, destination_dir: Optional[str] = None) -> Dict[str, Path]:
        """
        Extracts configuration files from UCS archive.
        Returns a dictionary mapping relative config paths to their extracted local filesystem paths.
        """
        extract_root = Path(destination_dir) if destination_dir else Path(tempfile.mkdtemp(prefix="f5_ucs_"))
        extract_root.mkdir(parents=True, exist_ok=True)
        self._temp_dir = str(extract_root) if not destination_dir else None

        extracted_files: Dict[str, Path] = {}

        with tarfile.open(self.ucs_path, "r:*") as tar:
            members = tar.getmembers()
            for member in members:
                # Strip leading slash or ./
                normalized_name = member.name.lstrip("./")
                for target_file in self.CORE_CONFIG_FILES:
                    if normalized_name.endswith(target_file):
                        tar.extract(member, path=extract_root)
                        local_path = extract_root / member.name
                        extracted_files[target_file] = local_path
                        break

                # Also extract SSL certs metadata if present
                if "config/ssl/" in normalized_name and not member.isdir():
                    tar.extract(member, path=extract_root)
                    extracted_files[normalized_name] = extract_root / member.name

        return extracted_files

    def cleanup(self):
        """Removes temporary extracted directories if created."""
        if self._temp_dir and os.path.exists(self._temp_dir):
            shutil.rmtree(self._temp_dir, ignore_errors=True)
            self._temp_dir = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
