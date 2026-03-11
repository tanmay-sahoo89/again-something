import os, sys, argparse, time
import pandas as pd

BASE_DIR    = "/home/claude/shipment_ews"
DATA_DIR    = f"{BASE_DIR}/data"
OUTPUT_DIR  = f"{BASE_DIR}/outputs"
ARTIFACTS   = f"{BASE_DIR}/artifacts"

for d in [DATA_DIR, OUTPUT_DIR, ARTIFACTS]:
    os.makedirs(d, exist_ok=True)


def banner(title: str):
    width = 60
    print("\n" + "═" * width)
    print(f"  {title}")
    print("═" * width)


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 1 — Training
# ─────────────────────────────────────────────────────────────────────────────
def run_training(n_samples: int = 6000):
    from data_generator      import generate_shipment_data
    from feature_engineering import ShipmentFeatureEngineer
    from model_training      import train_all, select_and_evaluate, save_model, print_comparison

    banner("PHASE 1 — DATA GENERATION")
    raw = generate_shipment_data(n_samples)
    raw.to_csv(f"{DATA_DIR}/shipments_raw.csv", index=False)
    print(f"  Raw data saved → {DATA_DIR}/shipments_raw.csv")

    banner("PHASE 2 — FEATURE ENGINEERING")
    fe = ShipmentFeatureEngineer()
    _, X_train, X_val, X_test, y_train, y_val, y_test = fe.fit_transform(raw)

    banner("PHASE 3 — MODEL TRAINING")
    results = train_all(X_train, y_train, X_val, y_val)
    print_comparison(results)
    best_name, best_clf = select_and_evaluate(results, X_test, y_test)
    save_model(best_clf, best_name)

    return fe


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 2 — Prediction (live batch)
# ─────────────────────────────────────────────────────────────────────────────
def run_prediction(fe=None, n_live: int = 500):
    from data_generator        import generate_shipment_data
    from feature_engineering   import ShipmentFeatureEngineer
    from risk_scoring          import RiskScoringEngine, print_alert_summary, export_alerts_csv
    from recommendation_engine import RecommendationEngine, export_recommendations_csv

    banner("PHASE 4 — LIVE SHIPMENT SCORING")
    live_raw = generate_shipment_data(n_live)
    live_raw.to_csv(f"{DATA_DIR}/live_shipments.csv", index=False)

    if fe is None:
        fe = ShipmentFeatureEngineer()
    X_live = fe.transform(live_raw)

    engine = RiskScoringEngine()
    alerts = engine.generate_alerts(live_raw, X_live, min_tier="MEDIUM")
    print_alert_summary(alerts)
    export_alerts_csv(alerts, f"{OUTPUT_DIR}/alerts.csv")

    banner("PHASE 5 — RECOMMENDATION ENGINE")
    rec_engine = RecommendationEngine()
    recs = rec_engine.batch_recommend(alerts, live_raw, min_tier="HIGH")
    export_recommendations_csv(recs, f"{OUTPUT_DIR}/recommendations.csv")

    # Print sample alerts and recommendations
    print("\n── Sample Alerts (first 2) ──")
    for a in alerts[:2]:
        print(a)

    print("\n── Sample Recommendations (first 2) ──")
    for r in recs[:2]:
        print(r)

    return alerts, recs


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 3 — Scenario Demo
# ─────────────────────────────────────────────────────────────────────────────
def run_scenario_demo():
    """
    Real-world scenario:
    Shipment SHP999999 travelling Shanghai→New York via Sea (Maersk).
    A storm has developed + port strike announced 60 hours before SLA.
    System detects HIGH risk and recommends rerouting + air freight upgrade.
    """
    banner("PHASE 6 — REAL-WORLD SCENARIO DEMO")
    from feature_engineering   import ShipmentFeatureEngineer
    from risk_scoring          import RiskScoringEngine
    from recommendation_engine import RecommendationEngine
    from datetime import datetime, timedelta

    scenario = {
        "shipment_id":               "SHP999999",
        "origin":                    "Shanghai",
        "destination":               "New York",
        "carrier":                   "Maersk",
        "transport_mode":            "Sea",
        "shipment_date":             "2024-03-01",
        "planned_eta":               (datetime.utcnow() + timedelta(hours=60)).strftime("%Y-%m-%d"),
        "planned_transit_days":      25,
        "days_in_transit":           22,
        "shipment_status":           "At Port",
        "package_weight_kg":         1200.0,
        "num_stops":                 3,
        "customs_clearance_flag":    0,
        "weather_condition":         "Storm",
        "weather_severity_score":    8.5,
        "traffic_congestion_level":  7,
        "port_congestion_score":     9,
        "disruption_type":           "Port Strike",
        "disruption_impact_score":   9.0,
        "carrier_reliability_score": 0.85,
        "historical_delay_rate":     0.32,
        "route_risk_score":          0.35,
        "is_delayed":                0,
        "delay_probability":         0.0,
        "actual_delay_hours":        0.0,
    }

    df_scenario = pd.DataFrame([scenario])

    fe = ShipmentFeatureEngineer()
    X  = fe.transform(df_scenario)

    engine = RiskScoringEngine()
    alerts = engine.generate_alerts(df_scenario, X, min_tier="LOW")

    rec_engine = RecommendationEngine()
    recs = rec_engine.batch_recommend(alerts, df_scenario, min_tier="LOW")

    print("\n📦  Scenario: Storm + Port Strike on Shanghai → New York route")
    for a in alerts:
        print(a)
    for r in recs:
        print(r)


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 4 — Summary Report
# ─────────────────────────────────────────────────────────────────────────────
def print_final_summary():
    banner("SYSTEM OUTPUT SUMMARY")
    files = {
        "Raw Training Data"    : f"{DATA_DIR}/shipments_raw.csv",
        "Live Shipments"       : f"{DATA_DIR}/live_shipments.csv",
        "Alerts Report"        : f"{OUTPUT_DIR}/alerts.csv",
        "Recommendations"      : f"{OUTPUT_DIR}/recommendations.csv",
        "Model Comparison"     : f"{ARTIFACTS}/model_comparison.csv",
        "Feature Importances"  : f"{ARTIFACTS}/feature_importances.csv",
        "Trained Model"        : f"{ARTIFACTS}/best_model.pkl",
    }
    for label, path in files.items():
        exists = "✅" if os.path.exists(path) else "❌"
        size   = f"({os.path.getsize(path):,} bytes)" if os.path.exists(path) else ""
        print(f"  {exists}  {label:<25s}  {path}  {size}")


# ─────────────────────────────────────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Shipment Delay Early Warning System")
    parser.add_argument("--mode", choices=["train", "predict", "full", "demo"],
                        default="full", help="Execution mode")
    parser.add_argument("--train-samples", type=int, default=6000)
    parser.add_argument("--live-samples",  type=int, default=500)
    args = parser.parse_args()

    t0 = time.time()

    if args.mode in ("train", "full"):
        fe = run_training(args.train_samples)
    else:
        fe = None

    if args.mode in ("predict", "full"):
        run_prediction(fe, args.live_samples)

    if args.mode in ("demo", "full"):
        run_scenario_demo()

    print_final_summary()
    print(f"\n  ⏱  Total runtime: {time.time() - t0:.1f}s")
    banner("PIPELINE COMPLETE")