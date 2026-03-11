import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Shipment } from '../types/shipment';
import { ShipmentAlert } from '../types/alert';
import { RiskMetrics } from '../types/risk';
import { apiService } from '../services/api';

interface ShipmentContextType {
  shipments: Shipment[];
  alerts: ShipmentAlert[];
  metrics: RiskMetrics | null;
  loading: boolean;
  error: string | null;
  refreshData: () => Promise<void>;
}

const ShipmentContext = createContext<ShipmentContextType | undefined>(undefined);

export const useShipmentContext = () => {
  const context = useContext(ShipmentContext);
  if (!context) {
    throw new Error('useShipmentContext must be used within ShipmentProvider');
  }
  return context;
};

interface ShipmentProviderProps {
  children: ReactNode;
}

export const ShipmentProvider: React.FC<ShipmentProviderProps> = ({ children }) => {
  const [shipments, setShipments] = useState<Shipment[]>([]);
  const [alerts, setAlerts] = useState<ShipmentAlert[]>([]);
  const [metrics, setMetrics] = useState<RiskMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refreshData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [shipmentsData, alertsData, metricsData] = await Promise.all([
        apiService.getShipments(),
        apiService.getAlerts(),
        apiService.getRiskMetrics(),
      ]);

      setShipments(shipmentsData);
      setAlerts(alertsData);
      setMetrics(metricsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshData();
  }, []);

  const value: ShipmentContextType = {
    shipments,
    alerts,
    metrics,
    loading,
    error,
    refreshData,
  };

  return <ShipmentContext.Provider value={value}>{children}</ShipmentContext.Provider>;
};
