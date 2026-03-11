export type RiskTier = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type AlertType = 'IMMEDIATE' | '48H_WARNING' | '72H_WARNING';

export interface ShipmentAlert {
  shipment_id: string;
  risk_tier: RiskTier;
  delay_probability: number;
  eta: string;
  hours_to_sla: number;
  origin: string;
  destination: string;
  carrier: string;
  transport_mode: string;
  top_risk_factors: string[];
  action_required: string;
  alert_generated_at: string;
  alert_type: AlertType;
}
