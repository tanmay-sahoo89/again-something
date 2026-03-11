import { Shipment } from '../types/shipment';
import { ShipmentAlert } from '../types/alert';
import { Recommendation, RiskMetrics } from '../types/risk';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

class ApiService {
  private async fetchWithTimeout(
    url: string,
    options: RequestInit = {},
    timeout = 10000
  ): Promise<Response> {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
      });
      clearTimeout(id);
      return response;
    } catch (error) {
      clearTimeout(id);
      throw error;
    }
  }

  async getShipments(): Promise<Shipment[]> {
    try {
      const response = await this.fetchWithTimeout(`${API_BASE_URL}/shipments`);
      if (!response.ok) throw new Error('Failed to fetch shipments');
      return await response.json();
    } catch (error) {
      console.error('Error fetching shipments:', error);
      return this.getMockShipments();
    }
  }

  async getShipmentById(id: string): Promise<Shipment | null> {
    try {
      const response = await this.fetchWithTimeout(`${API_BASE_URL}/shipments/${id}`);
      if (!response.ok) throw new Error('Failed to fetch shipment');
      return await response.json();
    } catch (error) {
      console.error('Error fetching shipment:', error);
      return null;
    }
  }

  async getAlerts(): Promise<ShipmentAlert[]> {
    try {
      const response = await this.fetchWithTimeout(`${API_BASE_URL}/alerts`);
      if (!response.ok) throw new Error('Failed to fetch alerts');
      return await response.json();
    } catch (error) {
      console.error('Error fetching alerts:', error);
      return this.getMockAlerts();
    }
  }

  async getRecommendations(shipmentId: string): Promise<Recommendation[]> {
    try {
      const response = await this.fetchWithTimeout(
        `${API_BASE_URL}/recommendations`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ shipment_id: shipmentId }),
        }
      );
      if (!response.ok) throw new Error('Failed to fetch recommendations');
      return await response.json();
    } catch (error) {
      console.error('Error fetching recommendations:', error);
      return [];
    }
  }

  async getRiskMetrics(): Promise<RiskMetrics> {
    try {
      const response = await this.fetchWithTimeout(`${API_BASE_URL}/analytics`);
      if (!response.ok) throw new Error('Failed to fetch analytics');
      return await response.json();
    } catch (error) {
      console.error('Error fetching analytics:', error);
      return this.getMockMetrics();
    }
  }

  async executeIntervention(
    shipmentId: string,
    action: string
  ): Promise<{ success: boolean; message: string }> {
    try {
      const response = await this.fetchWithTimeout(
        `${API_BASE_URL}/interventions`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ shipment_id: shipmentId, action }),
        }
      );
      if (!response.ok) throw new Error('Failed to execute intervention');
      return await response.json();
    } catch (error) {
      console.error('Error executing intervention:', error);
      return { success: false, message: 'Failed to execute action' };
    }
  }

  // Mock data for development
  private getMockShipments(): Shipment[] {
    return [];
  }

  private getMockAlerts(): ShipmentAlert[] {
    return [
      {
        shipment_id: 'SHP100123',
        risk_tier: 'CRITICAL',
        delay_probability: 0.92,
        eta: '2026-03-15',
        hours_to_sla: 18,
        origin: 'Shanghai',
        destination: 'New York',
        carrier: 'Maersk',
        transport_mode: 'Sea',
        top_risk_factors: [
          'Disruption: Port Strike [score: 9.0]',
          'Weather severity (Storm) [score: 8.5]',
          'Port congestion [score: 9.0]',
        ],
        action_required: 'Escalate to operations manager; activate emergency reroute.',
        alert_generated_at: '2026-03-11 19:00 UTC',
        alert_type: 'IMMEDIATE',
      },
      {
        shipment_id: 'SHP100456',
        risk_tier: 'HIGH',
        delay_probability: 0.78,
        eta: '2026-03-16',
        hours_to_sla: 42,
        origin: 'Hamburg',
        destination: 'London',
        carrier: 'DHL',
        transport_mode: 'Road',
        top_risk_factors: [
          'Traffic congestion level (Road) [score: 7.0]',
          'Weather severity (Heavy Rain) [score: 5.5]',
          'High route risk [score: 4.2]',
        ],
        action_required: 'Trigger intervention protocol immediately.',
        alert_generated_at: '2026-03-11 19:00 UTC',
        alert_type: '48H_WARNING',
      },
    ];
  }

  private getMockMetrics(): RiskMetrics {
    return {
      total_shipments: 500,
      critical_alerts: 12,
      high_alerts: 45,
      medium_alerts: 128,
      low_alerts: 315,
      average_risk_score: 0.34,
      shipments_at_risk: 185,
    };
  }
}

export const apiService = new ApiService();
