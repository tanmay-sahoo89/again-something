import pandas as pd
from dataclasses import dataclass, asdict
from typing import Optional


# ── Intervention Catalogue ────────────────────────────────────────────────────
INTERVENTIONS = {
    "REROUTE": {
        "label":       "Reroute Shipment",
        "description": "Divert the shipment to an alternative transit path that avoids the disrupted corridor.",
        "triggers":    ["Port Strike", "Natural Disaster", "Traffic Jam"],
        "modes":       ["Sea", "Road", "Rail"],
        "cost_impact": "Medium",
        "time_saving": "12–48 hours",
        "sla_impact":  "High",
    },
    "ALT_CARRIER": {
        "label":       "Assign Alternative Carrier",
        "description": "Transfer the shipment to a more reliable carrier with available capacity on the same route.",
        "triggers":    ["Equipment Failure", "carrier_reliability_low"],
        "modes":       ["Air", "Sea", "Road", "Rail"],
        "cost_impact": "Medium-High",
        "time_saving": "6–24 hours",
        "sla_impact":  "Medium",
    },
    "MODE_SWITCH_AIR": {
        "label":       "Upgrade to Air Freight",
        "description": "Switch from Sea/Road/Rail to Air freight to recover time against SLA.",
        "triggers":    ["high_delay_probability", "sla_breach_imminent"],
        "modes":       ["Sea", "Road", "Rail"],
        "cost_impact": "High",
        "time_saving": "24–96 hours",
        "sla_impact":  "Very High",
    },
    "PRIORITY_HANDLING": {
        "label":       "Priority / Express Handling",
        "description": "Flag for expedited processing at next handling point (customs, warehouse, port).",
        "triggers":    ["Customs Hold", "port_congestion_high"],
        "modes":       ["Air", "Sea", "Road", "Rail"],
        "cost_impact": "Low-Medium",
        "time_saving": "4–12 hours",
        "sla_impact":  "Medium",
    },
    "CUSTOMER_ALERT": {
        "label":       "Send Pre-Alert to Customer",
        "description": "Proactively notify the customer of potential delay, revised ETA, and mitigation steps.",
        "triggers":    ["any"],
        "modes":       ["Air", "Sea", "Road", "Rail"],
        "cost_impact": "None",
        "time_saving": "N/A (relationship management)",
        "sla_impact":  "Low (goodwill)",
    },
    "CUSTOMS_EXPEDITE": {
        "label":       "Expedite Customs Clearance",
        "description": "Engage customs broker for accelerated clearance to prevent dwell time accumulation.",
        "triggers":    ["Customs Hold", "customs_clearance_flag"],
        "modes":       ["Air", "Sea"],
        "cost_impact": "Low",
        "time_saving": "8–24 hours",
        "sla_impact":  "Medium-High",
    },
    "WAREHOUSE_HOLD": {
        "label":       "Hold at Nearest Warehouse",
        "description": "Pause shipment at nearest distribution hub; await disruption clearance before continuing.",
        "triggers":    ["Storm", "Blizzard", "Natural Disaster"],
        "modes":       ["Road", "Rail"],
        "cost_impact": "Low",
        "time_saving": "Variable",
        "sla_impact":  "Low",
    },
}


@dataclass
class Recommendation:
    shipment_id:         str
    risk_tier:           str
    delay_probability:   float
    primary_action:      str
    primary_description: str
    fallback_action:     Optional[str]
    cost_impact:         str
    estimated_time_saving: str
    sla_impact:          str
    confidence:          str
    reasoning:           list[str]

    def to_dict(self):
        return asdict(self)

    def __str__(self):
        lines = [
            f"\n{'─'*58}",
            f"  💡  RECOMMENDATION  [{self.shipment_id}]",
            f"{'─'*58}",
            f"  Risk Tier     : {self.risk_tier} ({self.delay_probability:.1%})",
            f"  Primary Action: {self.primary_action}",
            f"  Description   : {self.primary_description}",
            f"  Fallback      : {self.fallback_action or 'None'}",
            f"  Cost Impact   : {self.cost_impact}",
            f"  Time Saving   : {self.estimated_time_saving}",
            f"  SLA Impact    : {self.sla_impact}",
            f"  Confidence    : {self.confidence}",
            f"  Reasoning:",
        ]
        for r in self.reasoning:
            lines.append(f"    • {r}")
        lines.append(f"{'─'*58}")
        return "\n".join(lines)


# ── Recommendation Engine ─────────────────────────────────────────────────────
class RecommendationEngine:
    """
    Rule-based + heuristic engine that maps alert attributes to
    ranked intervention actions.

    Priority order:
      1. MODE_SWITCH_AIR   (if SLA < 24h and not already Air)
      2. REROUTE           (if disruption is a route-blocker)
      3. CUSTOMS_EXPEDITE  (if customs hold active)
      4. ALT_CARRIER       (if carrier reliability < 0.85)
      5. PRIORITY_HANDLING (if port congestion high)
      6. WAREHOUSE_HOLD    (if severe weather and road/rail)
      7. CUSTOMER_ALERT    (always appended as second recommendation)
    """

    def recommend(self, alert_row: dict, raw_row: pd.Series) -> Recommendation:
        shipment_id  = alert_row["shipment_id"]
        risk_tier    = alert_row["risk_tier"]
        delay_prob   = alert_row["delay_probability"]
        hours_to_sla = alert_row["hours_to_sla"]
        transport    = raw_row.get("transport_mode", "")
        disruption   = raw_row.get("disruption_type", "None")
        weather      = raw_row.get("weather_condition", "Clear")
        carrier_rel  = float(raw_row.get("carrier_reliability_score", 0.9))
        customs_flag = int(raw_row.get("customs_clearance_flag", 0))
        port_cong    = float(raw_row.get("port_congestion_score", 1))

        reasoning    = []
        primary_key  = None
        fallback_key = "CUSTOMER_ALERT"

        # ── Decision tree ─────────────────────────────────────────────────
        if hours_to_sla < 24 and transport != "Air":
            primary_key = "MODE_SWITCH_AIR"
            reasoning.append(f"SLA breach imminent ({hours_to_sla:.0f}h); air freight fastest recovery.")

        elif disruption in ("Port Strike", "Natural Disaster"):
            primary_key = "REROUTE"
            reasoning.append(f"Active disruption ({disruption}) blocking current route.")
            fallback_key = "ALT_CARRIER"

        elif disruption == "Traffic Jam" and transport in ("Road", "Rail"):
            primary_key = "REROUTE"
            reasoning.append("Traffic jam detected on road/rail segment; rerouting avoids delay.")

        elif customs_flag == 1:
            primary_key = "CUSTOMS_EXPEDITE"
            reasoning.append("Customs clearance flag active; broker escalation cuts dwell time.")
            fallback_key = "PRIORITY_HANDLING"

        elif carrier_rel < 0.85:
            primary_key = "ALT_CARRIER"
            reasoning.append(f"Carrier reliability ({carrier_rel:.0%}) below threshold; swap to higher-rated carrier.")

        elif port_cong >= 7:
            primary_key = "PRIORITY_HANDLING"
            reasoning.append(f"Port congestion score {port_cong:.0f}/10; priority slot reduces wait time.")

        elif weather in ("Storm", "Blizzard") and transport in ("Road", "Rail"):
            primary_key = "WAREHOUSE_HOLD"
            reasoning.append(f"Severe weather ({weather}) on road/rail; hold at hub until safe.")

        else:
            primary_key = "PRIORITY_HANDLING"
            reasoning.append("General elevated risk; priority handling advised as first response.")

        # Always add customer comms as secondary rationale
        reasoning.append("Customer pre-alert recommended to manage expectations proactively.")

        # Confidence heuristic
        if delay_prob >= 0.80:
            confidence = "High"
        elif delay_prob >= 0.60:
            confidence = "Medium"
        else:
            confidence = "Low"

        primary = INTERVENTIONS[primary_key]
        fallback = INTERVENTIONS.get(fallback_key, {})

        return Recommendation(
            shipment_id          = shipment_id,
            risk_tier            = risk_tier,
            delay_probability    = delay_prob,
            primary_action       = primary["label"],
            primary_description  = primary["description"],
            fallback_action      = fallback.get("label"),
            cost_impact          = primary["cost_impact"],
            estimated_time_saving= primary["time_saving"],
            sla_impact           = primary["sla_impact"],
            confidence           = confidence,
            reasoning            = reasoning,
        )

    def batch_recommend(
        self,
        alerts:  list,          # list[ShipmentAlert]
        raw_df:  pd.DataFrame,
        min_tier: str = "HIGH"
    ) -> list[Recommendation]:
        tier_order = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        min_idx    = tier_order.index(min_tier)
        recs = []

        raw_indexed = raw_df.set_index("shipment_id")

        for alert in alerts:
            if tier_order.index(alert.risk_tier) < min_idx:
                continue
            try:
                raw_row = raw_indexed.loc[alert.shipment_id]
                rec = self.recommend(alert.to_dict(), raw_row)
                recs.append(rec)
            except Exception as e:
                print(f"[RecEngine] Warning: could not process {alert.shipment_id}: {e}")

        print(f"[RecEngine] ✅  Generated {len(recs)} recommendations.")
        return recs


def export_recommendations_csv(recs: list[Recommendation], path: str):
    rows = [r.to_dict() for r in recs]
    pd.DataFrame(rows).to_csv(path, index=False)
    print(f"[RecEngine] Recommendations saved → {path}")


# ── Standalone demo ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    from data_generator      import generate_shipment_data
    from feature_engineering import ShipmentFeatureEngineer
    from risk_scoring        import RiskScoringEngine

    raw    = generate_shipment_data(300)
    fe     = ShipmentFeatureEngineer()
    X      = fe.transform(raw)

    engine = RiskScoringEngine()
    alerts = engine.generate_alerts(raw, X, min_tier="HIGH")

    rec_engine = RecommendationEngine()
    recs = rec_engine.batch_recommend(alerts, raw, min_tier="HIGH")

    for r in recs[:3]:
        print(r)

    import os
    os.makedirs("/home/claude/shipment_ews/outputs", exist_ok=True)
    export_recommendations_csv(recs, "/home/claude/shipment_ews/outputs/recommendations.csv")