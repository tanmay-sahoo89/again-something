export interface Recommendation {
  shipment_id: string;
  risk_tier: string;
  delay_probability: number;
  primary_action: string;
  primary_description: string;
  fallback_action: string | null;
  cost_impact: string;
  estimated_time_saving: string;
  sla_impact: string;
  confidence: string;
  reasoning: string[];
}

export interface RiskMetrics {
  total_shipments: number;
  critical_alerts: number;
  high_alerts: number;
  medium_alerts: number;
  low_alerts: number;
  average_risk_score: number;
  shipments_at_risk: number;
}
