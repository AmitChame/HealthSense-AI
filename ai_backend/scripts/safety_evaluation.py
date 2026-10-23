import os
import sys
import json
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report, roc_auc_score, accuracy_score
from sklearn.preprocessing import label_binarize

# Add ai_backend to PYTHONPATH
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.evaluation.trainer import ModelTrainingPipeline
from src.models.model_registry import ModelRegistry

def main():
    print("=" * 80)
    print("HealthSense AI — Safety-Focused Model Evaluation")
    print("=" * 80)

    # 1. Load Data
    dataset_path = project_root / "data" / "processed" / "unified_food_dataset.csv"
    df = pd.read_csv(dataset_path)

    # 2. Replicate Split (Product-level, random_state=42)
    barcodes = df['barcode'].unique()
    train_bc, test_barcodes = train_test_split(barcodes, test_size=0.20, random_state=42)
    df_test = df[df['barcode'].isin(test_barcodes)]

    print(f"Test Products: {len(test_barcodes)}")

    # 3. Prepare Test Features using trainer's logic but SAVED artifacts
    trainer = ModelTrainingPipeline(project_root=str(project_root))

    # Load artifacts into trainer's components
    trainer.tfidf_extractor.load(str(project_root / "artifacts" / "encoders" / "ingredient_tfidf.joblib"))
    trainer.scaler = joblib.load(str(project_root / "artifacts" / "scalers" / "nutrition_scaler.joblib"))
    with open(project_root / "artifacts" / "encoders" / "features_list.json", 'r') as f:
        trainer.feature_names = json.load(f)

    X_test, y_test = trainer.prepare_data(df_test, is_training=False)
    print(f"Test Observations: {len(X_test)}")

    # 4. Load Models
    models_to_evaluate = ['lightgbm', 'xgboost']
    results = {}

    for mname in models_to_evaluate:
        print(f"\nEvaluating: {mname}...")
        model_cls = ModelRegistry.get(mname)
        model = model_cls()
        model.load(str(project_root / "artifacts" / "models" / f"{mname}.joblib"))

        probas = model.predict_proba(X_test)
        preds = np.argmax(probas, axis=1)
        max_probas = np.max(probas, axis=1)

        # --- Confusion Matrix ---
        cm = confusion_matrix(y_test, preds, labels=[0, 1, 2])

        # --- Metrics ---
        # Classes: 0=RECOMMENDED, 1=CAUTION, 2=AVOID
        label_names = ["RECOMMENDED", "CAUTION", "AVOID"]

        # Per-class metrics
        from sklearn.metrics import precision_recall_fscore_support
        precision, recall, f1, support = precision_recall_fscore_support(y_test, preds, labels=[0, 1, 2])

        # Specificity calculation
        def get_specificity(y_true, y_pred, label):
            y_true_neg = (y_true != label)
            y_pred_neg = (y_pred != label)
            return np.sum(y_true_neg & y_pred_neg) / np.sum(y_true_neg) if np.sum(y_true_neg) > 0 else 0

        specificities = [get_specificity(y_test, preds, i) for i in range(3)]

        # AVOID specific
        avoid_recall = recall[2]
        avoid_precision = precision[2]
        avoid_f1 = f1[2]
        avoid_fnr = 1.0 - avoid_recall

        # False Safety: Actual AVOID (2) predicted as RECOMMENDED (0)
        false_safety_count = np.sum((y_test == 2) & (preds == 0))
        total_avoid = np.sum(y_test == 2)
        false_safety_rate = false_safety_count / total_avoid if total_avoid > 0 else 0

        # Macro/Weighted
        acc = accuracy_score(y_test, preds)
        macro_f1 = np.mean(f1)

        # ROC AUC
        y_test_bin = label_binarize(y_test, classes=[0, 1, 2])
        try:
            auc = roc_auc_score(y_test_bin, probas, multi_class='ovr')
        except:
            auc = 0.0

        # --- Confidence Analysis ---
        conf_bands = [
            (0.95, 1.0, ">= 95%"),
            (0.90, 0.95, "90-95%"),
            (0.80, 0.90, "80-90%"),
            (0.70, 0.80, "70-80%"),
            (0.0, 0.70, "< 70%")
        ]

        band_results = []
        for low, high, name in conf_bands:
            mask = (max_probas >= low) & (max_probas < high)
            band_X = X_test[mask]
            band_y = y_test[mask]
            band_preds = preds[mask]

            count = len(band_y)
            if count > 0:
                band_acc = accuracy_score(band_y, band_preds)
                band_fs = np.sum((band_y == 2) & (band_preds == 0))
                band_results.append({
                    'band': name,
                    'count': count,
                    'accuracy': band_acc,
                    'false_safety': int(band_fs)
                })
            else:
                band_results.append({'band': name, 'count': 0, 'accuracy': 0.0, 'false_safety': 0})

        # --- Error Extraction ---
        # Prioritize Actual AVOID -> Predicted RECOMMENDED
        errors = []
        error_mask = (y_test != preds)
        df_errors = df_test.iloc[np.repeat(np.arange(len(df_test)), 8)].iloc[error_mask].copy()
        # Add labels and probs to df_errors
        df_errors['actual'] = y_test[error_mask]
        df_errors['predicted'] = preds[error_mask]
        df_errors['max_prob'] = max_probas[error_mask]

        # We need to map health profile to the error observation
        # prepare_data stacks 8 scenarios per product in order.
        scenarios = [s['name'] for s in trainer.PROFILE_SCENARIOS]
        error_indices = np.where(error_mask)[0]
        df_errors['profile'] = [scenarios[idx % 8] for idx in error_indices]

        dangerous_errors = df_errors[(df_errors['actual'] == 2) & (df_errors['predicted'] == 0)].head(5)

        results[mname] = {
            'cm': cm,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'support': support,
            'specificity': specificities,
            'avoid_recall': avoid_recall,
            'avoid_precision': avoid_precision,
            'avoid_f1': avoid_f1,
            'avoid_fnr': avoid_fnr,
            'false_safety_count': int(false_safety_count),
            'false_safety_rate': false_safety_rate,
            'accuracy': acc,
            'macro_f1': macro_f1,
            'auc': auc,
            'bands': band_results,
            'dangerous_errors': dangerous_errors.to_dict('records')
        }

    # 5. Print Report
    lgbm = results['lightgbm']
    xgb = results['xgboost']

    print("\n" + "-"*40)
    print("LIGHTGBM SAFETY REPORT")
    print("-"*40)
    print("\nConfusion Matrix (Rows=Actual, Cols=Pred):")
    print("            REC   CAUT  AVOID")
    for i, row in enumerate(lgbm['cm']):
        print(f"{label_names[i]:<12} {row[0]:<5} {row[1]:<5} {row[2]:<5}")

    print("\nPer-Class Metrics:")
    print("Class        Prec   Rec    F1     Spec   Support")
    for i in range(3):
        print(f"{label_names[i]:<12} {lgbm['precision'][i]:.3f}  {lgbm['recall'][i]:.3f}  {lgbm['f1'][i]:.3f}  {lgbm['specificity'][i]:.3f}  {lgbm['support'][i]}")

    print(f"\nSafety-Critical Metrics (AVOID):")
    print(f"AVOID Recall (Sensitivity): {lgbm['avoid_recall']:.4f}")
    print(f"AVOID False Negative Rate:  {lgbm['avoid_fnr']:.4f}")
    print(f"FALSE SAFETY Count:         {lgbm['false_safety_count']}")
    print(f"FALSE SAFETY Rate:          {lgbm['false_safety_rate']:.4%}")

    print("\nConfidence Band Analysis:")
    print("Band        Count  Accuracy  False Safety")
    for b in lgbm['bands']:
        print(f"{b['band']:<10} {b['count']:<6} {b['accuracy']:.2%}    {b['false_safety']}")

    print("\nTop 5 Dangerous Errors (Actual AVOID -> Pred RECOMMENDED):")
    for err in lgbm['dangerous_errors']:
        print(f"- Product: {err['product_name']} ({err['barcode']})")
        print(f"  Profile: {err['profile']}")
        print(f"  Conf:    {err['max_prob']:.1%}")

    print("\n" + "-"*40)
    print("MODEL COMPARISON (SAFETY)")
    print("-"*40)
    print("Metric          LightGBM    XGBoost")
    print(f"AVOID Recall    {lgbm['avoid_recall']:.4f}      {xgb['avoid_recall']:.4f}")
    print(f"AVOID FNR       {lgbm['avoid_fnr']:.4f}      {xgb['avoid_fnr']:.4f}")
    print(f"False Safety R  {lgbm['false_safety_rate']:.4%}     {xgb['false_safety_rate']:.4%}")
    print(f"Macro F1        {lgbm['macro_f1']:.4f}      {xgb['macro_f1']:.4f}")

if __name__ == "__main__":
    main()
