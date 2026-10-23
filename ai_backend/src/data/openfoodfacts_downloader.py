"""
Open Food Facts Dataset Downloader.
Handles disk space verification, targeted exploratory sample downloading, and streaming CSV ingestion.
"""

import os
import shutil
import requests
import json
from typing import Dict, Any, List, Optional
from pathlib import Path


class OpenFoodFactsDownloader:
    """
    Reproducible downloader for Open Food Facts dataset.
    """

    OFF_SEARCH_API = "https://world.openfoodfacts.org/cgi/search.pl"
    OFF_CSV_URL = "https://static.openfoodfacts.org/data/en.openfoodfacts.org.products.csv.gz"

    def __init__(self, output_dir: Optional[str] = None):
        if output_dir is None:
            base_dir = Path(__file__).resolve().parent.parent.parent
            self.output_dir = base_dir / "data" / "raw" / "openfoodfacts"
        else:
            self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def check_disk_space(self, required_mb: float = 100.0) -> Dict[str, Any]:
        """
        Verifies available disk space before initiating any download.
        """
        total, used, free = shutil.disk_usage(self.output_dir)
        free_mb = free / (1024 * 1024)
        free_gb = free / (1024 * 1024 * 1024)

        return {
            'free_gb': round(free_gb, 2),
            'free_mb': round(free_mb, 2),
            'required_mb': required_mb,
            'is_sufficient': free_mb >= required_mb
        }

    def fetch_exploratory_sample(self, page_size: int = 50, num_pages: int = 10) -> str:
        """
        Fetches an exploratory sample (e.g. 500 products across diverse categories)
        via the official OpenFoodFacts search API to explore data quality and fields.
        """
        disk = self.check_disk_space(required_mb=50.0)
        if not disk['is_sufficient']:
            raise OSError(f"Insufficient disk space. Free: {disk['free_mb']}MB, Required: 50MB")

        sample_file = self.output_dir / "off_exploratory_sample.json"
        all_products: List[Dict[str, Any]] = []

        categories = [
            "cereals", "beverages", "snacks", "dairy", "plant-based-foods",
            "sauces", "breads", "biscuits", "chocolates", "prepared-meals"
        ]

        print(f"[OFF Downloader] Fetching exploratory sample across {len(categories)} categories...")

        for i, category in enumerate(categories):
            try:
                params = {
                    'action': 'process',
                    'tagtype_0': 'categories',
                    'tag_contains_0': 'contains',
                    'tag_0': category,
                    'page_size': page_size,
                    'page': 1,
                    'json': 'true'
                }
                headers = {
                    'User-Agent': 'HealthSenseAI-AcademicProject/1.0 (contact@healthsenseai.edu)'
                }
                resp = requests.get(self.OFF_SEARCH_API, params=params, headers=headers, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    products = data.get('products', [])
                    all_products.extend(products)
                    print(f"  Category '{category}': fetched {len(products)} products")
            except Exception as e:
                print(f"  Warning: failed to fetch category '{category}': {e}")

        # Save to JSON
        with open(sample_file, 'w', encoding='utf-8') as f:
            json.dump(all_products, f, indent=2)

        file_size_kb = sample_file.stat().st_size / 1024
        print(f"[OFF Downloader] Saved {len(all_products)} products to {sample_file} ({file_size_kb:.1f} KB)")
        return str(sample_file)
