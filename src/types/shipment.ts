export type TransportMode = 'Air' | 'Sea' | 'Road' | 'Rail';
export type ShipmentStatus = 'In Transit' | 'Customs Hold' | 'Out for Delivery' | 'Delayed' | 'At Port';
export type WeatherCondition = 'Clear' | 'Rain' | 'Heavy Rain' | 'Storm' | 'Fog' | 'Snow' | 'Blizzard';
export type DisruptionType = 'None' | 'Port Strike' | 'Traffic Jam' | 'Natural Disaster' | 'Equipment Failure';

export interface Shipment {
  shipment_id: string;
  origin: string;
  destination: string;
  carrier: string;
  transport_mode: TransportMode;
  shipment_date: string;
  planned_eta: string;
  planned_transit_days: number;
  days_in_transit: number;
  shipment_status: ShipmentStatus;
  package_weight_kg: number;
  num_stops: number;
  customs_clearance_flag: number;
  weather_condition: WeatherCondition;
  weather_severity_score: number;
  traffic_congestion_level: number;
  port_congestion_score: number;
  disruption_type: DisruptionType;
  disruption_impact_score: number;
  carrier_reliability_score: number;
  historical_delay_rate: number;
  route_risk_score: number;
  delay_probability: number;
  is_delayed: number;
  actual_delay_hours: number;
}
