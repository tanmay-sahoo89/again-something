import React from 'react';
import { motion } from 'framer-motion';
import { RiskMetrics } from '../components/Dashboard/RiskMetrics';
import { ShipmentAlerts } from '../components/Dashboard/ShipmentAlerts';
import { RiskDistributionChart } from '../components/Charts/RiskDistributionChart';
import { AlertTrendChart } from '../components/Charts/AlertTrendChart';

export const Dashboard: React.FC = () => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-8"
    >
      <div>
        <h2 className="text-3xl font-bold text-white mb-2">Dashboard Overview</h2>
        <p className="text-light">Real-time shipment risk monitoring and alerts</p>
      </div>

      <RiskMetrics />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RiskDistributionChart />
        <AlertTrendChart />
      </div>

      <div>
        <h3 className="text-2xl font-bold text-white mb-4">Active Alerts</h3>
        <ShipmentAlerts />
      </div>
    </motion.div>
  );
};
