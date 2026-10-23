"""
Ingredient Normalizer.
Standardizes and cleans ingredient text from raw packaging data or OpenFoodFacts.
"""

import re
from typing import List, Set


class IngredientNormalizer:
    """
    NLP & Regex-based cleaner for packaged food ingredient text.
    """

    # Common noise phrases in packaging ingredients
    NOISE_PATTERNS = [
        r'contains\s+less\s+than\s+\d+(\.\d+)?%\s+of\s*:',
        r'less\s+than\s+\d+(\.\d+)?%\s+of\s*:',
        r'\b\d+(\.\d+)?%\b',  # Percentage values like 15% or 2.5%
        r'\[.*?\]',            # Bracketed annotations
        r'\*',                 # Asterisks for footnotes
    ]

    def __init__(self):
        self.noise_regexes = [re.compile(p, re.IGNORECASE) for p in self.NOISE_PATTERNS]

    def clean_text(self, text: str) -> str:
        """
        Cleans and canonicalizes raw ingredients text into a standardized string.
        """
        if not text or not isinstance(text, str):
            return ""

        cleaned = text.lower().strip()

        # Remove noise patterns
        for regex in self.noise_regexes:
            cleaned = regex.sub(' ', cleaned)

        # Remove HTML tags if present
        cleaned = re.sub(r'<[^>]+>', ' ', cleaned)

        # Replace underscores and formatting artifacts
        cleaned = cleaned.replace('_', ' ').replace('\n', ' ').replace('\r', ' ')

        # Normalize multiple spaces
        cleaned = re.sub(r'\s+', ' ', cleaned)

        return cleaned.strip()

    def extract_phrases(self, text: str) -> List[str]:
        """
        Splits ingredient text by commas, semicolons, and periods into individual ingredient phrases.
        """
        cleaned = self.clean_text(text)
        if not cleaned:
            return []

        # Split on commas, semicolons, and bullets
        raw_items = re.split(r'[,;•\.\n]', cleaned)

        phrases = []
        for item in raw_items:
            item = item.strip()
            # Remove leading/trailing numbers, bullets, brackets
            item = re.sub(r'^[\d\s\-\.\)]+', '', item)
            item = re.sub(r'[\[\]\(\)]', '', item).strip()

            if item and len(item) > 1:
                # Remove common prefixes like 'and', 'organic', 'certified'
                item = re.sub(r'^(and|contains|with|of)\s+', '', item).strip()
                if item:
                    phrases.append(item)

        return phrases

    def normalize(self, text: str) -> str:
        """
        Returns a canonical comma-separated normalized ingredient string.
        """
        phrases = self.extract_phrases(text)
        return ", ".join(phrases) if phrases else "no ingredients listed"
