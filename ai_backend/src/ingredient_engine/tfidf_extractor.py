"""
TF-IDF Feature Extractor for Ingredient Text.
"""

from typing import List, Optional
import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer


class IngredientTfidfExtractor:
    """
    Extracts numerical TF-IDF feature vectors from normalized ingredient strings.
    """

    def __init__(self, max_features: int = 50, ngram_range: tuple = (1, 2)):
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            ngram_range=self.ngram_range,
            token_pattern=r'(?u)\b[a-zA-Z]{3,}\b',
            stop_words='english'
        )
        self.is_fitted = False

    def fit(self, texts: List[str]):
        """
        Fits the TF-IDF vectorizer on training ingredient texts.
        """
        clean_texts = [t if t and isinstance(t, str) else "" for t in texts]
        self.vectorizer.fit(clean_texts)
        self.is_fitted = True
        return self

    def transform(self, texts: List[str]):
        """
        Transforms texts into a dense or sparse TF-IDF array.
        """
        if not self.is_fitted:
            raise ValueError("IngredientTfidfExtractor must be fitted before transforming.")
        clean_texts = [t if t and isinstance(t, str) else "" for t in texts]
        return self.vectorizer.transform(clean_texts).toarray()

    def fit_transform(self, texts: List[str]):
        """
        Fits and transforms texts.
        """
        self.fit(texts)
        return self.transform(texts)

    def get_feature_names(self) -> List[str]:
        """
        Returns the vocabulary feature names.
        """
        if not self.is_fitted:
            return []
        return [f"tfidf_{name.replace(' ', '_')}" for name in self.vectorizer.get_feature_names_out()]

    def save(self, filepath: str):
        """
        Serializes the fitted vectorizer to disk.
        """
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump(self.vectorizer, filepath)

    def load(self, filepath: str):
        """
        Loads a serialized vectorizer from disk.
        """
        if os.path.exists(filepath):
            self.vectorizer = joblib.load(filepath)
            self.is_fitted = True
        else:
            raise FileNotFoundError(f"TF-IDF artifact not found at {filepath}")
        return self
