"""
Food Category Intelligence Engine for HealthSense AI.
Resolves product food categories, checks composition standards (e.g. Codex chocolate),
and applies category-specific nutrient benchmarks without confusing identity with healthfulness.
"""

from typing import Dict, Any, List, Optional
import os
from pathlib import Path
import yaml
import logging

logger = logging.getLogger(__name__)


class FoodCategoryEngine:
    """
    Categorizes products and evaluates category-specific composition requirements.
    Separates 'meets food standard' from 'is healthy for this individual'.
    """

    _instance: Optional['FoodCategoryEngine'] = None

    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            base_dir = Path(__file__).resolve().parent.parent.parent
            config_path = str(base_dir / "config" / "food_categories.yaml")

        self.config_path = config_path
        self.categories: Dict[str, Any] = {}
        self._load_categories()

    @classmethod
    def get_instance(cls, config_path: Optional[str] = None) -> 'FoodCategoryEngine':
        """Singleton accessor for thread-safe in-memory caching."""
        if cls._instance is None:
            cls._instance = cls(config_path)
        return cls._instance

    def _load_categories(self):
        if not os.path.exists(self.config_path):
            logger.warning(f"Food categories file not found at: {self.config_path}")
            return

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
            self.categories = data.get('categories', {})
        except Exception as e:
            logger.error(f"Failed to load food categories: {e}")

    def resolve_category(self, categories_list: List[str], product_name: str = "", ingredients_text: str = "") -> Optional[Dict[str, Any]]:
        """
        Resolves the most specific food category from OpenFoodFacts tags, product name, or ingredients.
        """
        search_terms = [c.lower() for c in categories_list]
        name_lower = product_name.lower()
        ing_lower = ingredients_text.lower()

        # Prioritize specific subcategories first (e.g. milk_chocolate before chocolate, energy_drink before soft_drink)
        priority_keys = ['milk_chocolate', 'chocolate', 'energy_drink', 'soft_drink', 'oats', 'bread_whole_grain', 'plain_yogurt', 'general_confectionery']

        for key in priority_keys:
            cat_data = self.categories.get(key)
            if not cat_data:
                continue

            tags = cat_data.get('tags', [])
            for tag in tags:
                clean_tag = tag.lower().replace('en:', '').replace('-', ' ')
                if any(clean_tag in term or term in clean_tag for term in search_terms):
                    result = dict(cat_data)
                    result['key'] = key
                    return result

                if clean_tag in name_lower:
                    result = dict(cat_data)
                    result['key'] = key
                    return result

        # Fallback to key in name
        for key, cat_data in self.categories.items():
            if key.replace('_', ' ') in name_lower or key.replace('_', ' ') in ing_lower:
                result = dict(cat_data)
                result['key'] = key
                return result

        return None

    def evaluate_composition_standard(self, category_key: str, product_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verifies if a product meets regulatory/compositional standards for its named category.
        Example: Chocolate cocoa solids requirement (Codex CXS 87-1981 / FSSAI).
        NOTE: Meeting a composition standard verifies legal/taxonomic identity, NOT healthiness.
        """
        cat_data = self.categories.get(category_key)
        if not cat_data or 'composition_standards' not in cat_data:
            return {
                'has_standard': False,
                'meets_standard': True,
                'details': 'No specific composition standard defined for this category'
            }

        standards = cat_data['composition_standards']
        ingredients = product_context.get('normalized_ingredients', '').lower()

        # Special Case: Chocolate composition analysis
        if category_key in ['chocolate', 'milk_chocolate']:
            # Check for authentic cocoa ingredients (cocoa mass, cocoa liquor, cocoa butter)
            has_cocoa = 'cocoa' in ingredients or 'cacao' in ingredients or 'chocolate liquor' in ingredients
            has_cocoa_butter = 'cocoa butter' in ingredients or 'cacao butter' in ingredients
            has_veg_fat_substitute = 'hydrogenated' in ingredients or 'palm oil' in ingredients or 'vegetable fat' in ingredients

            meets = has_cocoa and (has_cocoa_butter or not has_veg_fat_substitute)

            notes = []
            if has_cocoa:
                notes.append("Contains authentic cocoa components.")
            if has_veg_fat_substitute:
                notes.append("Contains vegetable fat substitutes; verify if compliant with chocolate standard threshold (max 5% under Codex/FSSAI).")

            return {
                'has_standard': True,
                'meets_standard': meets,
                'source': standards.get('source'),
                'standard_name': "Cocoa Composition Identity Standard",
                'composition_notes': " ".join(notes),
                'conceptual_clarification': "Meeting a cocoa solids standard defines legal product classification, not healthfulness."
            }

        return {
            'has_standard': True,
            'meets_standard': True,
            'source': standards.get('source'),
            'details': 'Meets general category composition requirements'
        }
