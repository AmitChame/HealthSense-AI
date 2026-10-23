"""
USDA FoodData Central Downloader and Ingestion Module.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional


class USDADownloader:
    """
    Downloader and schema reference for USDA FoodData Central Branded Foods dataset.
    """

    USDA_DOWNLOAD_BASE = "https://fdc.nal.usda.gov/fdc-datasets/"

    def __init__(self, output_dir: Optional[str] = None):
        if output_dir is None:
            base_dir = Path(__file__).resolve().parent.parent.parent
            self.output_dir = base_dir / "data" / "raw" / "usda"
        else:
            self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def check_disk_space(self, required_mb: float = 500.0) -> Dict[str, Any]:
        total, used, free = shutil.disk_usage(self.output_dir)
        free_mb = free / (1024 * 1024)
        return {
            'free_mb': round(free_mb, 2),
            'required_mb': required_mb,
            'is_sufficient': free_mb >= required_mb
        }

    def get_ingestion_guidelines(self) -> Dict[str, Any]:
        """
        Returns reference instructions for importing USDA Branded Foods CSV dumps.
        """
        return {
            'source': 'USDA FoodData Central',
            'recommended_dataset': 'FoodData_Central_branded_food_csv.zip',
            'approx_size_compressed_mb': 150.0,
            'approx_size_uncompressed_mb': 900.0,
            'target_dir': str(self.output_dir),
            'status': 'Ready for secondary reference ingestion'
        }
