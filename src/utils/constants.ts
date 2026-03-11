export const RISK_TIER_COLORS = {
  LOW: '#10B981',
  MEDIUM: '#F59E0B',
  HIGH: '#F97316',
  CRITICAL: '#DC2626',
} as const;

export const RISK_TIER_ICONS = {
  LOW: '🟢',
  MEDIUM: '🟡',
  HIGH: '🟠',
  CRITICAL: '🔴',
} as const;

export const RISK_TIER_LABELS = {
  LOW: 'Low Risk',
  MEDIUM: 'Medium Risk',
  HIGH: 'High Risk',
  CRITICAL: 'Critical Risk',
} as const;

export const CARRIERS = [
  'FedEx',
  'DHL',
  'UPS',
  'Maersk',
  'DB Schenker',
  'XPO Logistics',
] as const;

export const TRANSPORT_MODES = ['Air', 'Sea', 'Road', 'Rail'] as const;

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
