"""
Allergen Taxonomy and Detection Engine.
Detects major food allergens from OpenFoodFacts tags and ingredients text.
"""

from typing import Dict, List, Set
import re


class AllergenDetector:
    """
    Multi-allergen taxonomy matching engine covering the top 9+ FDA/EU/WHO food allergens.
    """

    ALLERGEN_TAXONOMY: Dict[str, List[str]] = {
        'peanut': [
            'peanut', 'peanuts', 'arachis', 'groundnut', 'groundnuts',
            'monkey nut', 'peanut butter', 'peanut oil', 'peanut flour'
        ],
        'tree_nuts': [
            'almond', 'almonds', 'cashew', 'cashews', 'walnut', 'walnuts',
            'pecan', 'pecans', 'pistachio', 'pistachios', 'macadamia',
            'brazil nut', 'brazil nuts', 'hazelnut', 'hazelnuts', 'filbert',
            'filberts', 'chestnut', 'chestnuts', 'pine nut', 'pine nuts',
            'praline', 'marzipan', 'tree nut', 'tree nuts'
        ],
        'milk': [
            'milk', 'dairy', 'butter', 'cheese', 'whey', 'casein', 'caseinate',
            'cream', 'lactose', 'ghee', 'curd', 'yogurt', 'yoghurt',
            'buttermilk', 'milk powder', 'skim milk', 'whole milk',
            'sour cream', 'custard', 'nonfat milk', 'milk solids'
        ],
        'egg': [
            'egg', 'eggs', 'egg white', 'egg whites', 'egg yolk', 'egg yolks',
            'albumin', 'ovalbumin', 'lysozyme', 'mayonnaise', 'meringue',
            'ovomucoid', 'ovoglobulin', 'livetin', 'egg powder'
        ],
        'gluten': [
            'wheat', 'barley', 'rye', 'spelt', 'kamut', 'triticale', 'gluten',
            'vital wheat gluten', 'semolina', 'durum', 'farina', 'graham flour',
            'malt', 'malt extract', 'malt syrup', 'wheat flour', 'enriched flour',
            'bleached flour', 'unbleached flour', 'all-purpose flour'
        ],
        'soy': [
            'soy', 'soya', 'soybean', 'soybeans', 'tofu', 'tempeh', 'edamame',
            'soy lecithin', 'soya lecithin', 'soy sauce', 'hydrolyzed soy',
            'soy protein', 'soy isolate', 'soy flour', 'soymilk'
        ],
        'fish': [
            'fish', 'cod', 'salmon', 'tuna', 'anchovy', 'anchovies', 'bass',
            'trout', 'tilapia', 'halibut', 'sardine', 'sardines', 'haddock',
            'mackerel', 'flounder', 'snapper', 'fish sauce', 'fish oil'
        ],
        'shellfish': [
            'shellfish', 'shrimp', 'shrimps', 'prawn', 'prawns', 'crab',
            'crabs', 'lobster', 'lobsters', 'crawfish', 'crayfish', 'mussel',
            'mussels', 'oyster', 'oysters', 'clam', 'clams', 'scallop',
            'scallops', 'squid', 'calamari', 'octopus', 'crustacean', 'mollusc'
        ],
        'sesame': [
            'sesame', 'sesame seeds', 'sesame seed', 'tahini', 'tahina',
            'gingelly', 'sesamum', 'sesame oil', 'sesame paste'
        ],
        'mustard': [
            'mustard', 'mustard seed', 'mustard seeds', 'mustard powder',
            'mustard flour', 'sinapis'
        ],
        'sulfites': [
            'sulfite', 'sulfites', 'sulphite', 'sulphites', 'sulfur dioxide',
            'sulphur dioxide', 'sodium bisulfite', 'potassium metabisulfite',
            'sodium metabisulfite'
        ]
    }

    def __init__(self):
        # Precompile word-boundary regex patterns for accurate matching
        self.patterns: Dict[str, List[re.Pattern]] = {}
        for allergen, keywords in self.ALLERGEN_TAXONOMY.items():
            self.patterns[allergen] = [
                re.compile(r'\b' + re.escape(kw) + r'\b', re.IGNORECASE)
                for kw in keywords
            ]

    def detect_allergens(self, ingredients_text: str, tags: List[str] = None) -> Dict[str, bool]:
        """
        Returns a dictionary of boolean flags for each allergen category.
        """
        results = {
            f'contains_{allergen}': False
            for allergen in self.ALLERGEN_TAXONOMY.keys()
        }

        # 1. Check explicit OpenFoodFacts tags
        if tags:
            for tag in tags:
                clean_tag = tag.lower().replace('en:', '').replace('-', ' ').strip()
                for allergen in self.ALLERGEN_TAXONOMY.keys():
                    if allergen in clean_tag or clean_tag in allergen:
                        results[f'contains_{allergen}'] = True

        # 2. Check ingredients text
        if ingredients_text and isinstance(ingredients_text, str):
            text_lower = ingredients_text.lower()
            for allergen, regex_list in self.patterns.items():
                if results[f'contains_{allergen}']:
                    continue
                for regex in regex_list:
                    if regex.search(text_lower):
                        results[f'contains_{allergen}'] = True
                        break

        return results

    def get_detected_allergen_list(self, ingredients_text: str, tags: List[str] = None) -> List[str]:
        """
        Returns a human-readable list of detected allergens (e.g. ['Peanut', 'Gluten']).
        """
        flags = self.detect_allergens(ingredients_text, tags)
        detected = []
        for key, present in flags.items():
            if present:
                allergen_name = key.replace('contains_', '').replace('_', ' ').title()
                detected.append(allergen_name)
        return detected
