import pandas as pd
import numpy as np
import joblib, os, json, warnings
warnings.filterwarnings("ignore")

from sklearn.linear_model    import LogisticRegression
from sklearn.ensemble        import RandomForestClassifier, GradientBoostingClassifier, ExtraTreesClassifier
from sklearn.metrics         import (
    classification_report, roc_auc_score, f1_score,
    precision_score, recall_score, confusion_matrix
)

ARTIFACTS_DIR = "/home/claude/shipment_ews/artifacts"
os.makedirs(ARTIFACTS_DIR, exist_ok=True)


# ── Model zoo ─────────────────────────────────────────────────────────────────
def build_models():
    return {
        "Logistic Regression": LogisticRegression(
            max_iter=1000, class_weight="balanced", C=0.5, random_state=42
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=200, max_depth=12, min_samples_leaf=5,
            class_weight="balanced", n_jobs=-1, random_state=42
        ),
        "Gradient Boosting": GradientBoostingClassifier(
            n_estimators=200, learning_rate=0.05, max_depth=5,
            subsample=0.8, random_state=42
        ),
        "Extra Trees": ExtraTreesClassifier(
            n_estimators=200, max_depth=12, min_samples_leaf=5,
            class_weight="balanced", n_jobs=-1, random_state=42
        ),
    }


# ── Training ──────────────────────────────────────────────────────────────────
def train_all(X_train, y_train, X_val, y_val) -> dict:
    models = build_models()
    results = {}

    print("\n" + "="*60)
    print("  MODEL TRAINING & VALIDATION")
    print("="*60)

    for name, clf in models.items():
        print(f"\n▶  Training  {name} …")
        clf.fit(X_train, y_train)

        y_pred  = clf.predict(X_val)
        y_prob  = clf.predict_proba(X_val)[:, 1]

        metrics = {
            "ROC-AUC":   round(roc_auc_score(y_val, y_prob), 4),
            "F1":        round(f1_score(y_val, y_pred), 4),
            "Precision": round(precision_score(y_val, y_pred), 4),
            "Recall":    round(recall_score(y_val, y_pred), 4),
        }
        results[name] = {"model": clf, "metrics": metrics}

        print(f"   ROC-AUC  : {metrics['ROC-AUC']:.4f}")
        print(f"   F1-Score : {metrics['F1']:.4f}")
        print(f"   Precision: {metrics['Precision']:.4f}")
        print(f"   Recall   : {metrics['Recall']:.4f}")

    return results


# ── Select best & evaluate on test set ───────────────────────────────────────
def select_and_evaluate(results: dict, X_test, y_test) -> str:
    best_name = max(results, key=lambda k: results[k]["metrics"]["ROC-AUC"])
    best_clf  = results[best_name]["model"]

    print("\n" + "="*60)
    print(f"  BEST MODEL: {best_name}")
    print("="*60)

    y_pred = best_clf.predict(X_test)
    y_prob = best_clf.predict_proba(X_test)[:, 1]

    print(f"\n  Test ROC-AUC : {roc_auc_score(y_test, y_prob):.4f}")
    print(f"  Test F1      : {f1_score(y_test, y_pred):.4f}")
    print("\n  Classification Report:")
    print(classification_report(y_test, y_pred, target_names=["On Time", "Delayed"]))

    cm = confusion_matrix(y_test, y_pred)
    print("  Confusion Matrix:")
    print(f"    {'':15s} Pred On-Time  Pred Delayed")
    print(f"    {'Actual On-Time':15s}  {cm[0,0]:>10}    {cm[0,1]:>10}")
    print(f"    {'Actual Delayed':15s}  {cm[1,0]:>10}    {cm[1,1]:>10}")

    # Feature importance (tree-based models)
    if hasattr(best_clf, "feature_importances_"):
        feat_cols = joblib.load(f"{ARTIFACTS_DIR}/feature_cols.pkl")
        fi = pd.Series(best_clf.feature_importances_, index=feat_cols)
        fi_sorted = fi.sort_values(ascending=False).head(10)
        print("\n  Top-10 Feature Importances:")
        for feat, imp in fi_sorted.items():
            bar = "█" * int(imp * 80)
            print(f"    {feat:<35s} {imp:.4f}  {bar}")
        fi.to_csv(f"{ARTIFACTS_DIR}/feature_importances.csv", header=["importance"])

    return best_name, best_clf


# ── Save ──────────────────────────────────────────────────────────────────────
def save_model(model, name: str):
    path = f"{ARTIFACTS_DIR}/best_model.pkl"
    joblib.dump(model, path)
    with open(f"{ARTIFACTS_DIR}/best_model_name.txt", "w") as f:
        f.write(name)
    print(f"\n[ModelTrainer] ✅  Best model saved → {path}")


# ── Comparison summary table ──────────────────────────────────────────────────
def print_comparison(results: dict):
    print("\n" + "="*60)
    print("  MODEL COMPARISON SUMMARY")
    print("="*60)
    rows = []
    for name, info in results.items():
        m = info["metrics"]
        rows.append({"Model": name, **m})
    df = pd.DataFrame(rows).sort_values("ROC-AUC", ascending=False)
    print(df.to_string(index=False))
    df.to_csv(f"{ARTIFACTS_DIR}/model_comparison.csv", index=False)


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    from data_generator    import generate_shipment_data
    from feature_engineering import ShipmentFeatureEngineer

    raw = generate_shipment_data(6000)
    fe  = ShipmentFeatureEngineer()
    _, X_train, X_val, X_test, y_train, y_val, y_test = fe.fit_transform(raw)

    results = train_all(X_train, y_train, X_val, y_val)
    print_comparison(results)

    best_name, best_clf = select_and_evaluate(results, X_test, y_test)
    save_model(best_clf, best_name)