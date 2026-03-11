import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.model_selection import train_test_split
import joblib, os, warnings
warnings.filterwarnings("ignore")

ARTIFACTS_DIR = "/home/claude/shipment_ews/artifacts"
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

# ── Column groups ─────────────────────────────────────────────────────────────
CATEGORICAL_COLS = ["carrier", "transport_mode", "origin", "destination",
                    "shipment_status", "weather_condition", "disruption_type"]

NUMERIC_FEATURES = [
    "weather_severity_score", "traffic_congestion_level", "port_congestion_score",
    "disruption_impact_score", "carrier_reliability_score", "historical_delay_rate",
    "route_risk_score", "days_in_transit", "planned_transit_days",
    "package_weight_kg", "num_stops", "customs_clearance_flag",
    "transit_progress_ratio", "composite_risk_score",
    "carrier_enc", "transport_enc", "origin_enc", "destination_enc",
    "status_enc", "weather_enc", "disruption_enc",
]

TARGET = "is_delayed"


class ShipmentFeatureEngineer:
    """
    Full preprocessing pipeline:
      1. Clean & validate raw data
      2. Engineer derived features
      3. Encode categoricals
      4. Scale numerics
      5. Split train / val / test
    """

    def __init__(self):
        self.label_encoders: dict[str, LabelEncoder] = {}
        self.scaler = MinMaxScaler()
        self.feature_cols: list[str] = []

    # ── 1. Cleaning ────────────────────────────────────────────────────────
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        print("[Pipeline] Step 1 – Cleaning …")
        df = df.copy()

        # Drop duplicates
        before = len(df)
        df.drop_duplicates(subset="shipment_id", inplace=True)
        print(f"           Dropped {before - len(df)} duplicate rows.")

        # Clamp scores to valid ranges
        df["weather_severity_score"]   = df["weather_severity_score"].clip(0, 10)
        df["traffic_congestion_level"] = df["traffic_congestion_level"].clip(1, 10)
        df["port_congestion_score"]    = df["port_congestion_score"].clip(1, 10)
        df["disruption_impact_score"]  = df["disruption_impact_score"].clip(0, 10)
        df["carrier_reliability_score"]= df["carrier_reliability_score"].clip(0, 1)
        df["historical_delay_rate"]    = df["historical_delay_rate"].clip(0, 1)
        df["route_risk_score"]         = df["route_risk_score"].clip(0, 1)

        # Fill any NaNs
        df[CATEGORICAL_COLS] = df[CATEGORICAL_COLS].fillna("Unknown")
        num_cols = df.select_dtypes(include=np.number).columns
        df[num_cols] = df[num_cols].fillna(df[num_cols].median())

        print(f"           Remaining rows: {len(df):,}")
        return df

    # ── 2. Feature Engineering ─────────────────────────────────────────────
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        print("[Pipeline] Step 2 – Engineering features …")
        df = df.copy()

        # Transit progress (how far through the journey)
        df["transit_progress_ratio"] = (
            df["days_in_transit"] / df["planned_transit_days"].replace(0, np.nan)
        ).fillna(0).clip(0, 2)

        # Composite risk score — weighted blend of external signals
        df["composite_risk_score"] = (
            df["weather_severity_score"]   * 0.20 +
            df["traffic_congestion_level"] * 0.15 +
            df["disruption_impact_score"]  * 0.25 +
            df["port_congestion_score"]    * 0.10 +
            (1 - df["carrier_reliability_score"]) * 10 * 0.15 +
            df["historical_delay_rate"]    * 10 * 0.10 +
            df["route_risk_score"]         * 10 * 0.05
        ).round(4)

        # Customs penalty
        df["composite_risk_score"] += df["customs_clearance_flag"] * 0.8

        # Weight bucket (log scale to reduce outlier influence)
        df["log_weight"] = np.log1p(df["package_weight_kg"])

        # SLA pressure: planned ETA within 2 days adds urgency
        df["sla_pressure"] = (df["planned_transit_days"] - df["days_in_transit"]).clip(0, 10)

        print(f"           Composite risk — mean: {df['composite_risk_score'].mean():.3f}, "
              f"max: {df['composite_risk_score'].max():.3f}")
        return df

    # ── 3. Encode categoricals ─────────────────────────────────────────────
    def encode(self, df: pd.DataFrame, fit: bool = True) -> pd.DataFrame:
        print("[Pipeline] Step 3 – Encoding categoricals …")
        df = df.copy()
        col_map = {
            "carrier": "carrier_enc", "transport_mode": "transport_enc",
            "origin": "origin_enc", "destination": "destination_enc",
            "shipment_status": "status_enc",
            "weather_condition": "weather_enc",
            "disruption_type": "disruption_enc",
        }
        for raw_col, enc_col in col_map.items():
            if fit:
                le = LabelEncoder()
                df[enc_col] = le.fit_transform(df[raw_col].astype(str))
                self.label_encoders[raw_col] = le
            else:
                le = self.label_encoders[raw_col]
                df[enc_col] = df[raw_col].astype(str).map(
                    lambda x, le=le: le.transform([x])[0] if x in le.classes_ else -1
                )
        return df

    # ── 4. Scale ───────────────────────────────────────────────────────────
    def scale(self, df: pd.DataFrame, fit: bool = True) -> pd.DataFrame:
        print("[Pipeline] Step 4 – Scaling numeric features …")
        df = df.copy()
        extra_feats = ["log_weight", "sla_pressure"]
        all_num = [c for c in NUMERIC_FEATURES + extra_feats if c in df.columns]
        self.feature_cols = all_num

        if fit:
            df[all_num] = self.scaler.fit_transform(df[all_num])
        else:
            df[all_num] = self.scaler.transform(df[all_num])
        return df

    # ── 5. Split ───────────────────────────────────────────────────────────
    def split(self, df: pd.DataFrame):
        print("[Pipeline] Step 5 – Splitting data …")
        X = df[self.feature_cols]
        y = df[TARGET]
        X_train, X_temp, y_train, y_temp = train_test_split(
            X, y, test_size=0.30, stratify=y, random_state=42)
        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp, test_size=0.50, stratify=y_temp, random_state=42)
        print(f"           Train: {len(X_train):,}  Val: {len(X_val):,}  Test: {len(X_test):,}")
        return X_train, X_val, X_test, y_train, y_val, y_test

    # ── Full pipeline ──────────────────────────────────────────────────────
    def fit_transform(self, df: pd.DataFrame):
        df = self.clean(df)
        df = self.engineer_features(df)
        df = self.encode(df, fit=True)
        df = self.scale(df, fit=True)
        splits = self.split(df)

        # Persist artifacts
        joblib.dump(self.label_encoders, f"{ARTIFACTS_DIR}/label_encoders.pkl")
        joblib.dump(self.scaler,         f"{ARTIFACTS_DIR}/scaler.pkl")
        joblib.dump(self.feature_cols,   f"{ARTIFACTS_DIR}/feature_cols.pkl")
        df.to_csv(f"{ARTIFACTS_DIR}/processed_data.csv", index=False)
        print(f"[Pipeline] ✅  Artifacts saved → {ARTIFACTS_DIR}/")
        return df, *splits

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply saved pipeline to new inference data (no fitting)."""
        self.label_encoders = joblib.load(f"{ARTIFACTS_DIR}/label_encoders.pkl")
        self.scaler         = joblib.load(f"{ARTIFACTS_DIR}/scaler.pkl")
        self.feature_cols   = joblib.load(f"{ARTIFACTS_DIR}/feature_cols.pkl")
        df = self.clean(df)
        df = self.engineer_features(df)
        df = self.encode(df, fit=False)
        df = self.scale(df, fit=False)
        return df[self.feature_cols]


if __name__ == "__main__":
    raw = pd.read_csv("/home/claude/shipment_ews/data/shipments_raw.csv")
    fe  = ShipmentFeatureEngineer()
    processed, X_train, X_val, X_test, y_train, y_val, y_test = fe.fit_transform(raw)
    print(f"\nFeatures used ({len(fe.feature_cols)}):\n  {fe.feature_cols}")