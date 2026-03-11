import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import warnings
warnings.filterwarnings("ignore")

np.random.seed(42)
random.seed(42)

# ── Constants ────────────────────────────────────────────────────────────────
CARRIERS     = ["FedEx", "DHL", "UPS", "Maersk", "DB Schenker", "XPO Logistics"]
ORIGINS      = ["Shanghai", "Hamburg", "Los Angeles", "Mumbai", "Rotterdam", "Dubai"]
DESTINATIONS = ["New York", "London", "Tokyo", "Sydney", "Chicago", "Singapore"]
TRANSPORT    = ["Air", "Sea", "Road", "Rail"]
STATUSES     = ["In Transit", "Customs Hold", "Out for Delivery", "Delayed", "At Port"]
WEATHER_COND = ["Clear", "Rain", "Heavy Rain", "Storm", "Fog", "Snow", "Blizzard"]
DISRUPTIONS  = ["None", "Port Strike", "Traffic Jam", "Natural Disaster", "Equipment Failure"]

CARRIER_RELIABILITY = {
    "FedEx": 0.92, "DHL": 0.89, "UPS": 0.91,
    "Maersk": 0.85, "DB Schenker": 0.87, "XPO Logistics": 0.83
}

WEATHER_SEVERITY = {
    "Clear": 0, "Rain": 2, "Heavy Rain": 5,
    "Storm": 8, "Fog": 4, "Snow": 6, "Blizzard": 9
}

DISRUPTION_IMPACT = {
    "None": 0, "Port Strike": 9, "Traffic Jam": 4,
    "Natural Disaster": 10, "Equipment Failure": 6
}

ROUTE_RISK = {
    ("Shanghai", "New York"): 0.35,
    ("Hamburg", "London"): 0.10,
    ("Los Angeles", "Tokyo"): 0.25,
    ("Mumbai", "Sydney"): 0.30,
    ("Rotterdam", "Chicago"): 0.20,
    ("Dubai", "Singapore"): 0.15,
}


def _route_risk(origin, dest):
    key = (origin, dest)
    return ROUTE_RISK.get(key, round(random.uniform(0.10, 0.45), 2))


def _traffic_score(transport_mode):
    base = {"Air": 1, "Sea": 3, "Road": 6, "Rail": 2}
    return base[transport_mode] + random.randint(0, 3)


def _compute_delay_probability(row):
    """Deterministic heuristic to create ground-truth labels."""
    score = 0.0
    score += row["weather_severity_score"]   * 0.025
    score += row["traffic_congestion_level"] * 0.020
    score += (1 - row["carrier_reliability_score"]) * 1.2
    score += row["route_risk_score"]         * 0.80
    score += row["disruption_impact_score"]  * 0.028
    score += row["historical_delay_rate"]    * 0.60
    score += (row["days_in_transit"] / max(row["planned_transit_days"], 1)) * 0.10
    score += random.gauss(0, 0.04)            # noise
    return min(max(score, 0.0), 1.0)          # clamp [0,1]


def generate_shipment_data(n: int = 5000) -> pd.DataFrame:
    """
    Generate n synthetic shipment records with features and delay labels.
    Returns a DataFrame ready for EDA and model training.
    """
    records = []
    start_date = datetime(2023, 1, 1)

    for i in range(n):
        origin      = random.choice(ORIGINS)
        destination = random.choice([d for d in DESTINATIONS])
        carrier     = random.choice(CARRIERS)
        transport   = random.choice(TRANSPORT)
        status      = random.choice(STATUSES)
        weather     = random.choice(WEATHER_COND)
        disruption  = random.choice(DISRUPTIONS)

        ship_date     = start_date + timedelta(days=random.randint(0, 700))
        planned_days  = {"Air": random.randint(2, 5), "Sea": random.randint(18, 35),
                         "Road": random.randint(3, 10), "Rail": random.randint(7, 15)}[transport]
        eta           = ship_date + timedelta(days=planned_days)
        days_in_transit = random.randint(0, planned_days + 5)

        carrier_rel   = CARRIER_RELIABILITY[carrier] + random.gauss(0, 0.02)
        weather_sev   = WEATHER_SEVERITY[weather] + random.uniform(-0.5, 0.5)
        traffic_cong  = _traffic_score(transport)
        route_risk    = _route_risk(origin, destination)
        disruption_imp= DISRUPTION_IMPACT[disruption] + random.uniform(-0.5, 0.5)
        hist_delay_rt = round(random.uniform(0.02, 0.40), 3)
        port_congestion = random.randint(1, 10)
        num_stops     = random.randint(1, 5)
        package_weight= round(random.uniform(0.5, 5000), 2)  # kg
        customs_flag  = random.choice([0, 0, 0, 1])           # 25% customs

        row = {
            "shipment_id":              f"SHP{100000 + i}",
            "origin":                   origin,
            "destination":              destination,
            "carrier":                  carrier,
            "transport_mode":           transport,
            "shipment_date":            ship_date.strftime("%Y-%m-%d"),
            "planned_eta":              eta.strftime("%Y-%m-%d"),
            "planned_transit_days":     planned_days,
            "days_in_transit":          days_in_transit,
            "shipment_status":          status,
            "package_weight_kg":        package_weight,
            "num_stops":                num_stops,
            "customs_clearance_flag":   customs_flag,
            # ── External signals ──────────────────────────────────────────
            "weather_condition":        weather,
            "weather_severity_score":   round(max(weather_sev, 0), 2),
            "traffic_congestion_level": traffic_cong,
            "port_congestion_score":    port_congestion,
            "disruption_type":          disruption,
            "disruption_impact_score":  round(max(disruption_imp, 0), 2),
            # ── Engineered / historical features ─────────────────────────
            "carrier_reliability_score": round(min(max(carrier_rel, 0), 1), 3),
            "historical_delay_rate":     hist_delay_rt,
            "route_risk_score":          route_risk,
        }

        # Ground-truth delay probability → binary label
        delay_prob = _compute_delay_probability(row)
        row["delay_probability"]    = round(delay_prob, 4)
        row["is_delayed"]           = int(delay_prob >= 0.50)
        row["actual_delay_hours"]   = (
            round(random.uniform(6, 96) * delay_prob, 1) if row["is_delayed"] else 0.0
        )
        records.append(row)

    df = pd.DataFrame(records)
    print(f"[DataGenerator] ✅  Generated {len(df):,} shipment records.")
    print(f"[DataGenerator]     Delay rate : {df['is_delayed'].mean():.1%}")
    return df


if __name__ == "__main__":
    df = generate_shipment_data(5000)
    df.to_csv("/home/claude/shipment_ews/data/shipments_raw.csv", index=False)
    print("[DataGenerator] Saved → data/shipments_raw.csv")
    print(df.head(3).to_string())