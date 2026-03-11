import pandas as pd
import numpy as np
import joblib, json, os
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Optional

ARTIFACTS_DIR = "/home/claude/shipment_ews/artifacts"

# ── Risk Tier Thresholds ──────────────────────────────────────────────────────
RISK_TIERS = {
    "LOW":    (0.00, 0.30),   # Green
    "MEDIUM": (0.30, 0.60),   # Amber
    "HIGH":   (0.60, 0.90),   # Orange
    "CRITICAL":(0.90, 1.00),  # Red
}

TIER_COLORS = {
    "LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🟠", "CRITICAL": "🔴"}

TIER_ACTIONS = {
    "LOW":      "Monitor – no immediate action required.",
    "MEDIUM":   "Review carrier updates; prepare contingency options.",
    "HIGH":     "Trigger intervention protocol immediately.",
    "CRITICAL": "Escalate to operations manager; activate emergency reroute.",
}


# ── Alert Dataclass ───────────────────────────────────────────────────────────
@dataclass
class ShipmentAlert:
    shipment_id:       str
    risk_tier:         str
    delay_probability: float
    eta:               str
    hours_to_sla:      float
    origin:            str
    destination:       str
    carrier:           str
    transport_mode:    str
    top_risk_factors:  list
    action_required:   str
    alert_generated_at:str
    alert_type:        str   # "48H_WARNING" | "72H_WARNING" | "IMMEDIATE"

    def to_dict(self):
        return asdict(self)

    def __str__(self):
        tier_icon = TIER_COLORS[self.risk_tier]
        lines = [
            f"\n{'─'*58}",
            f"  {tier_icon}  SHIPMENT ALERT  [{self.alert_type}]",
            f"{'─'*58}",
            f"  Shipment ID   : {self.shipment_id}",
            f"  Route         : {self.origin} → {self.destination}",
            f"  Carrier       : {self.carrier} ({self.transport_mode})",
            f"  ETA           : {self.eta}",
            f"  Hours to SLA  : {self.hours_to_sla:.1f} h",
            f"  Delay Prob    : {self.delay_probability:.1%}",
            f"  Risk Tier     : {self.risk_tier}",
            f"  Top Factors   :",
        ]
        for f in self.top_risk_factors:
            lines.append(f"    • {f}")
        lines += [
            f"  Action        : {self.action_required}",
            f"  Generated At  : {self.alert_generated_at}",
            f"{'─'*58}",
        ]
        return "\n".join(lines)


# ── Scoring Engine ────────────────────────────────────────────────────────────
class RiskScoringEngine:
    """
    Loads the trained model + pipeline artifacts and scores
    new shipment records in batch or one-by-one.
    """

    def __init__(self):
        self.model      = joblib.load(f"{ARTIFACTS_DIR}/best_model.pkl")
        self.feature_cols = joblib.load(f"{ARTIFACTS_DIR}/feature_cols.pkl")
        with open(f"{ARTIFACTS_DIR}/best_model_name.txt") as f:
            self.model_name = f.read().strip()
        print(f"[RiskEngine] Loaded model: {self.model_name}")

    def score(self, X: pd.DataFrame) -> np.ndarray:
        """Return delay probability for each row in X (feature matrix)."""
        return self.model.predict_proba(X)[:, 1]

    @staticmethod
    def classify_tier(prob: float) -> str:
        for tier, (lo, hi) in RISK_TIERS.items():
            if lo <= prob < hi:
                return tier
        return "CRITICAL"

    @staticmethod
    def _top_factors(row: pd.Series) -> list[str]:
        """Return top 3 human-readable risk drivers for a single shipment."""
        signals = {
            f"Weather severity ({row.get('weather_condition','N/A')})"       : row.get("weather_severity_score",0),
            f"Traffic congestion level ({row.get('transport_mode','N/A')})"  : row.get("traffic_congestion_level",0),
            f"Disruption: {row.get('disruption_type','None')}"               : row.get("disruption_impact_score",0),
            "Port congestion"                                                 : row.get("port_congestion_score",0),
            "Low carrier reliability"                                         : (1 - row.get("carrier_reliability_score",1)) * 10,
            "High historical delay rate"                                      : row.get("historical_delay_rate",0) * 10,
            "High route risk"                                                 : row.get("route_risk_score",0) * 10,
            "Customs hold active"                                             : row.get("customs_clearance_flag",0) * 8,
        }
        top = sorted(signals.items(), key=lambda x: x[1], reverse=True)[:3]
        return [f"{name} [score: {val:.1f}]" for name, val in top if val > 0]

    @staticmethod
    def _alert_type(hours_to_sla: float) -> str:
        if hours_to_sla <= 24:
            return "IMMEDIATE"
        elif hours_to_sla <= 48:
            return "48H_WARNING"
        else:
            return "72H_WARNING"

    def generate_alerts(
        self,
        raw_df: pd.DataFrame,
        feature_matrix: pd.DataFrame,
        min_tier: str = "MEDIUM"
    ) -> list[ShipmentAlert]:
        """
        Score every shipment and return alerts for those at or above min_tier.
        raw_df     – original dataframe (for human-readable fields)
        feature_matrix – preprocessed features aligned to model input
        min_tier   – lowest tier to raise an alert ("LOW"|"MEDIUM"|"HIGH"|"CRITICAL")
        """
        tier_order = list(RISK_TIERS.keys())
        min_idx    = tier_order.index(min_tier)

        probs = self.score(feature_matrix)
        now   = datetime.utcnow()
        alerts = []

        for i, (idx, row) in enumerate(raw_df.iterrows()):
            prob = float(probs[i])
            tier = self.classify_tier(prob)

            if tier_order.index(tier) < min_idx:
                continue   # below threshold – skip

            # Estimate hours remaining to SLA
            try:
                eta_dt = datetime.strptime(str(row["planned_eta"]), "%Y-%m-%d")
                hours_to_sla = (eta_dt - now).total_seconds() / 3600
                hours_to_sla = max(hours_to_sla, 0)
            except Exception:
                hours_to_sla = 48.0

            alert = ShipmentAlert(
                shipment_id       = str(row["shipment_id"]),
                risk_tier         = tier,
                delay_probability = round(prob, 4),
                eta               = str(row["planned_eta"]),
                hours_to_sla      = round(hours_to_sla, 1),
                origin            = str(row["origin"]),
                destination       = str(row["destination"]),
                carrier           = str(row["carrier"]),
                transport_mode    = str(row["transport_mode"]),
                top_risk_factors  = self._top_factors(row),
                action_required   = TIER_ACTIONS[tier],
                alert_generated_at= now.strftime("%Y-%m-%d %H:%M UTC"),
                alert_type        = self._alert_type(hours_to_sla),
            )
            alerts.append(alert)

        return alerts


# ── Alert Reporter ────────────────────────────────────────────────────────────
def print_alert_summary(alerts: list[ShipmentAlert]):
    print("\n" + "="*60)
    print("  EARLY WARNING SYSTEM — ALERT SUMMARY")
    print("="*60)
    counts = {t: 0 for t in RISK_TIERS}
    for a in alerts:
        counts[a.risk_tier] += 1

    for tier, cnt in counts.items():
        icon = TIER_COLORS[tier]
        bar  = "█" * cnt
        print(f"  {icon} {tier:<10s}  {cnt:>4d}  {bar}")

    print(f"\n  Total alerts raised : {len(alerts)}")
    print(f"  High + Critical     : {counts['HIGH'] + counts['CRITICAL']}")


def export_alerts_csv(alerts: list[ShipmentAlert], path: str):
    rows = [a.to_dict() for a in alerts]
    pd.DataFrame(rows).to_csv(path, index=False)
    print(f"[RiskEngine] ✅  Alerts exported → {path}")


# ── Demo / standalone run ─────────────────────────────────────────────────────
if __name__ == "__main__":
    from data_generator      import generate_shipment_data
    from feature_engineering import ShipmentFeatureEngineer

    raw = generate_shipment_data(500)
    fe  = ShipmentFeatureEngineer()
    X   = fe.transform(raw)

    engine = RiskScoringEngine()
    alerts = engine.generate_alerts(raw, X, min_tier="MEDIUM")

    # Print first 3 alerts
    for a in alerts[:3]:
        print(a)

    print_alert_summary(alerts)
    os.makedirs("/home/claude/shipment_ews/outputs", exist_ok=True)
    export_alerts_csv(alerts, "/home/claude/shipment_ews/outputs/alerts.csv")