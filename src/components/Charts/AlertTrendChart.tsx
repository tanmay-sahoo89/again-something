import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { motion } from 'framer-motion';
import { RISK_TIER_COLORS } from '../../utils/constants';

const mockData = [
  { date: 'Mon', critical: 8, high: 32, medium: 98, low: 245 },
  { date: 'Tue', critical: 12, high: 38, medium: 105, low: 268 },
  { date: 'Wed', critical: 10, high: 42, medium: 112, low: 290 },
  { date: 'Thu', critical: 15, high: 45, medium: 120, low: 302 },
  { date: 'Fri', critical: 12, high: 45, medium: 128, low: 315 },
];

export const AlertTrendChart: React.FC = () => {
  return (
    <motion.div
      initial={{ scale: 0.9, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      className="card"
    >
      <h3 className="text-xl font-bold text-white mb-6">Alert Trends (Last 5 Days)</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={mockData}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
          <XAxis dataKey="date" stroke="#BEA8A7" />
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
          <Line
            type="monotone"
            dataKey="critical"
            stroke={RISK_TIER_COLORS.CRITICAL}
            strokeWidth={2}
            name="Critical"
          />
          <Line
            type="monotone"
            dataKey="high"
            stroke={RISK_TIER_COLORS.HIGH}
            strokeWidth={2}
            name="High"
          />
          <Line
            type="monotone"
            dataKey="medium"
            stroke={RISK_TIER_COLORS.MEDIUM}
            strokeWidth={2}
            name="Medium"
          />
          <Line
            type="monotone"
            dataKey="low"
            stroke={RISK_TIER_COLORS.LOW}
            strokeWidth={2}
            name="Low"
          />
        </LineChart>
      </ResponsiveContainer>
    </motion.div>
  );
};
