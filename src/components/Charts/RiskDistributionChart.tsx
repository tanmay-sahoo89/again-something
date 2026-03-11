import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { useShipmentContext } from '../../contexts/ShipmentContext';
import { RISK_TIER_COLORS } from '../../utils/constants';
import { motion } from 'framer-motion';

export const RiskDistributionChart: React.FC = () => {
  const { metrics, loading } = useShipmentContext();

  if (loading || !metrics) {
    return (
      <div className="card animate-pulse">
        <div className="h-80 bg-white/5 rounded"></div>
      </div>
    );
  }

  const data = [
    { name: 'Critical', value: metrics.critical_alerts, color: RISK_TIER_COLORS.CRITICAL },
    { name: 'High', value: metrics.high_alerts, color: RISK_TIER_COLORS.HIGH },
    { name: 'Medium', value: metrics.medium_alerts, color: RISK_TIER_COLORS.MEDIUM },
    { name: 'Low', value: metrics.low_alerts, color: RISK_TIER_COLORS.LOW },
  ];

  return (
    <motion.div
      initial={{ scale: 0.9, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      className="card"
    >
      <h3 className="text-xl font-bold text-white mb-6">Risk Distribution</h3>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
            outerRadius={100}
            fill="#8884d8"
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: 'rgba(15, 15, 15, 0.9)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '8px',
              color: '#fff',
            }}
          />
          <Legend
            wrapperStyle={{ color: '#BEA8A7' }}
            iconType="circle"
          />
        </PieChart>
      </ResponsiveContainer>
    </motion.div>
  );
};
