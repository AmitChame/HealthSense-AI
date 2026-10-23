"""
Ingredient Concern & Additive Detector.
Flags added sugars, artificial sweeteners, preservatives, artificial colors, hydrogenated fats, and animal ingredients.
"""

from typing import Dict, List, Optional, Any
import re


class ConcernDetector:
    """
    Detector for ultra-processed additives, artificial chemicals, and dietary restrictions.
    """

    CONCERN_TAXONOMY: Dict[str, List[str]] = {
        'added_sugar': [
            'high fructose corn syrup', 'corn syrup', 'cane sugar', 'invert sugar',
            'corn syrup solids', 'maltodextrin', 'dextrose', 'fructose',
            'glucose', 'sucrose', 'maltose', 'molasses', 'agave nectar',
            'brown rice syrup', 'tapioca syrup', 'barley malt'
        ],
        'artificial_sweetener': [
            'aspartame', 'sucralose', 'acesulfame potassium', 'acesulfame-k',
            'ace-k', 'saccharin', 'neotame', 'advantame', 'splenda',
            'erythritol', 'xylitol', 'sorbitol', 'mannitol', 'maltitol'
        ],
        'preservative': [
            'sodium benzoate', 'potassium sorbate', 'sodium nitrite',
            'sodium nitrate', 'butylated hydroxyanisole', 'bha',
            'butylated hydroxytoluene', 'bht', 'tbhq', 'tertiary butylhydroquinone',
            'calcium propionate', 'potassium benzoate', 'sodium propionate'
        ],
        'artificial_color': [
            'red 40', 'red #40', 'yellow 5', 'yellow #5', 'yellow 6', 'yellow #6',
            'blue 1', 'blue #1', 'blue 2', 'blue #2', 'caramel color',
            'tartrazine', 'allura red', 'sunset yellow', 'brilliant blue',
            'artificial color', 'artificial colors'
        ],
        'hydrogenated_oil': [
            'partially hydrogenated', 'hydrogenated vegetable oil',
            'hydrogenated palm oil', 'hydrogenated soybean oil',
            'hydrogenated cottonseed oil', 'shortening', 'interesterified oil'
        ],
        'animal_derived': [
            'gelatin', 'carmine', 'cochineal', 'lard', 'tallow', 'collagen',
            'rennet', 'casein', 'whey', 'honey', 'beeswax', 'isinglass'
        ],
        'meat_or_gelatin': [
            'beef', 'pork', 'chicken', 'lamb', 'turkey', 'duck', 'meat',
            'bacon', 'ham', 'sausage', 'gelatin', 'lard', 'tallow',
            'veal', 'mutton', 'poultry'
        ]
    }

    def __init__(self):
        self.patterns: Dict[str, List[re.Pattern]] = {}
        for concern, keywords in self.CONCERN_TAXONOMY.items():
            self.patterns[concern] = [
                re.compile(r'\b' + re.escape(kw) + r'\b', re.IGNORECASE)
                for kw in keywords
            ]

    def detect_concerns(self, ingredients_text: str, additives_tags: Optional[List[str]] = None) -> Dict[str, any]:
        """
        Returns binary indicators, count metrics, and specific flagged items.
        Combines ingredient text regex with explicit additive tags.
        """
        results = {
            'added_sugar_indicator': 0,
            'artificial_sweetener_indicator': 0,
            'preservative_indicator': 0,
            'artificial_color_indicator': 0,
            'hydrogenated_oil_indicator': 0,
            'contains_animal_derived': False,
            'contains_meat_or_gelatin': False,
            'high_concern_ingredient_count': 0,
            'flagged_concerns_list': []
        }

        flagged_items = []

        # 1. Regex-based detection from ingredient text
        if ingredients_text and isinstance(ingredients_text, str):
            text_lower = ingredients_text.lower()
            for category, regex_list in self.patterns.items():
                matched_in_category = False
                for regex in regex_list:
                    match = regex.search(text_lower)
                    if match:
                        matched_in_category = True
                        flagged_items.append(f"{category.replace('_', ' ').title()}: {match.group(0)}")

                if matched_in_category:
                    self._update_results_by_category(results, category)

        # 2. Tag-based detection (Open Food Facts additives_tags)
        if additives_tags:
            for tag in additives_tags:
                category = self._map_additive_tag_to_category(tag)
                if category:
                    self._update_results_by_category(results, category)
                    desc = tag.replace('en:', '').upper()
                    item_str = f"{category.replace('_', ' ').title()}: Tag {desc}"
                    if item_str not in flagged_items:
                        flagged_items.append(item_str)

        results['high_concern_ingredient_count'] = (
            results['added_sugar_indicator'] +
            results['artificial_sweetener_indicator'] +
            results['preservative_indicator'] +
            results['artificial_color_indicator'] +
            results['hydrogenated_oil_indicator']
        )

        # De-duplicate flagged items (maintaining order)
        seen = set()
        results['flagged_concerns_list'] = [x for x in flagged_items if not (x.lower() in seen or seen.add(x.lower()))]

        return results

    def _update_results_by_category(self, results: Dict[str, Any], category: str):
        if category == 'added_sugar':
            results['added_sugar_indicator'] = 1
        elif category == 'artificial_sweetener':
            results['artificial_sweetener_indicator'] = 1
        elif category == 'preservative':
            results['preservative_indicator'] = 1
        elif category == 'artificial_color':
            results['artificial_color_indicator'] = 1
        elif category == 'hydrogenated_oil':
            results['hydrogenated_oil_indicator'] = 1
        elif category == 'animal_derived':
            results['contains_animal_derived'] = True
        elif category == 'meat_or_gelatin':
            results['contains_meat_or_gelatin'] = True

    def _map_additive_tag_to_category(self, tag: str) -> Optional[str]:
        """
        Maps E-numbers and additive names to internal concern categories.
        """
        tag = tag.lower().replace('en:', '').strip()

        # Simple E-number range mapping
        if tag.startswith('e'):
            try:
                num = int(re.sub(r'[^0-9]', '', tag))
                if 100 <= num <= 199: return 'artificial_color'
                if 200 <= num <= 299: return 'preservative'
                if 950 <= num <= 969: return 'artificial_sweetener'
                # Specific animals
                if num == 120: return 'animal_derived' # Carmine
                if num == 428: return 'meat_or_gelatin' # Gelatin
                if num == 901: return 'animal_derived' # Beeswax
            except ValueError:
                pass

        # Explicit name mapping for common tags
        if 'aspartame' in tag: return 'artificial_sweetener'
        if 'sucralose' in tag: return 'artificial_sweetener'
        if 'saccharin' in tag: return 'artificial_sweetener'
        if 'gelatin' in tag: return 'meat_or_gelatin'

        return None
