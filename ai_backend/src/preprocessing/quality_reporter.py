"""
Data Quality and Coverage Reporter for HealthSense AI Datasets.
"""

import pandas as pd
from typing import Dict, Any


class DataQualityReporter:
    """
    Generates structured reports on missingness, coverage, and data health.
    """

    def generate_report(self, df: pd.DataFrame) -> Dict[str, Any]:
        total_rows = len(df)
        if total_rows == 0:
            return {'total_rows': 0, 'status': 'EMPTY_DATASET'}

        # Missingness percentages
        missing_counts = df.isnull().sum()
        missing_pcts = (missing_counts / total_rows * 100.0).round(2).to_dict()

        # Core nutrients coverage
        core_nutrients = ['energy_kcal_100g', 'sugars_100g', 'sodium_100g', 'fat_100g', 'saturated_fat_100g', 'protein_100g', 'carbohydrates_100g', 'fiber_100g']
        complete_nutrition_count = int(df[core_nutrients].dropna().shape[0]) if all(c in df.columns for c in core_nutrients) else 0

        # Ingredients coverage
        has_ingredients = int((df['ingredients_text'].fillna('').str.strip().str.len() > 0).sum()) if 'ingredients_text' in df.columns else 0

        # Allergen flags distribution
        allergen_cols = [c for c in df.columns if c.startswith('contains_')]
        allergen_counts = {col: int(df[col].sum()) for col in allergen_cols if col in df.columns}

        report = {
            'total_products': total_rows,
            'complete_nutrition_count': complete_nutrition_count,
            'complete_nutrition_pct': round(complete_nutrition_count / total_rows * 100.0, 2),
            'ingredients_text_coverage_count': has_ingredients,
            'ingredients_text_coverage_pct': round(has_ingredients / total_rows * 100.0, 2),
            'missingness_percentages': missing_pcts,
            'allergen_positives': allergen_counts,
            'food_grade_distribution': df['healthsense_grade'].value_counts().to_dict() if 'healthsense_grade' in df.columns else {}
        }
        return report

    def format_markdown_report(self, report: Dict[str, Any]) -> str:
        md = []
        md.append(f"# HealthSense AI Data Quality Audit Report\n")
        md.append(f"- **Total Products Analyzed**: {report.get('total_products', 0)}")
        md.append(f"- **Complete Nutrition Profile**: {report.get('complete_nutrition_count', 0)} ({report.get('complete_nutrition_pct', 0)}%)")
        md.append(f"- **Ingredients Text Coverage**: {report.get('ingredients_text_coverage_count', 0)} ({report.get('ingredients_text_coverage_pct', 0)}%)\n")

        md.append("## Nutritional Missingness")
        md.append("| Field | Missing Count | Missing % |")
        md.append("|---|---|---|")
        for k, v in report.get('missingness_percentages', {}).items():
            if '100g' in k or 'ingredient' in k:
                md.append(f"| `{k}` | {int(v * report['total_products'] / 100)} | {v}% |")

        md.append("\n## HealthSense Food Grade Distribution")
        for g, count in report.get('food_grade_distribution', {}).items():
            md.append(f"- **Grade {g}**: {count} products")

        return "\n".join(md)
