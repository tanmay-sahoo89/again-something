import React from 'react';
import { motion } from 'framer-motion';
import { RiskDistributionChart } from '../components/Charts/RiskDistributionChart';
import { AlertTrendChart } from '../components/Charts/AlertTrendChart';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const carrierData = [
  { name: 'FedEx', onTime: 420, delayed: 35 },
  { name: 'DHL', onTime: 385, delayed: 42 },
  { name: 'UPS', onTime: 398, delayed: 38 },
  { name: 'Maersk', onTime: 305, delayed: 68 },
  { name: 'DB Schenker', onTime: 342, delayed: 55 },
];

export const Analytics: React.FC = () => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-8"
    >
      <div>
        <h2 className="text-3xl font-bold text-white mb-2">Analytics & Insights</h2>
        <p className="text-light">Comprehensive performance metrics and trends</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RiskDistributionChart />
        <AlertTrendChart />
      </div>

      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="card"
      >
        <h3 className="text-xl font-bold text-white mb-6">Carrier Performance</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={carrierData}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
            <XAxis dataKey="name" stroke="#BEA8A7" />
            <YAxis stroke="#BEA8A7" />
            <Tooltip
              contentStyle={{
                backgroundColor: 'rgba(15, 15, 15, 0.9)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '8px',
                color: '#fff',
              }}
            />
            <Legend wrapperStyle={{ color: '#BEA8A7' }} />
            <Bar dataKey="onTime" fill="#10B981" name="On Time" />
            <Bar dataKey="delayed" fill="#DC2626" name="Delayed" />
          </BarChart>
        </ResponsiveContainer>
      </motion.div>
    </motion.div>
  );
};
