import React from 'react';
import { motion } from 'framer-motion';
import { TriangleAlert as AlertTriangle, TrendingUp, Package, Activity } from 'lucide-react';
import { useShipmentContext } from '../../contexts/ShipmentContext';
import { formatNumber, formatPercentage } from '../../utils/formatters';

export const RiskMetrics: React.FC = () => {
  const { metrics, loading } = useShipmentContext();

  if (loading || !metrics) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="card animate-pulse">
            <div className="h-24 bg-white/5 rounded"></div>
          </div>
        ))}
      </div>
    );
  }

  const cards = [
    {
      title: 'Total Shipments',
      value: formatNumber(metrics.total_shipments),
      icon: Package,
      color: 'from-blue-500 to-blue-600',
      change: '+12%',
    },
    {
      title: 'Critical Alerts',
      value: formatNumber(metrics.critical_alerts),
      icon: AlertTriangle,
      color: 'from-red-500 to-red-600',
      change: '-5%',
    },
    {
      title: 'Shipments at Risk',
      value: formatNumber(metrics.shipments_at_risk),
      icon: TrendingUp,
      color: 'from-orange-500 to-orange-600',
      change: '+8%',
    },
    {
      title: 'Avg Risk Score',
      value: formatPercentage(metrics.average_risk_score),
      icon: Activity,
      color: 'from-accent to-secondary',
      change: '-3%',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {cards.map((card, index) => (
        <motion.div
          key={card.title}
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: index * 0.1 }}
          className="card hover:scale-105"
        >
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-light mb-1">{card.title}</p>
              <p className="text-3xl font-bold text-white">{card.value}</p>
              <p className="text-xs text-green-400 mt-1">{card.change} vs last week</p>
            </div>
            <div className={`p-3 rounded-lg bg-gradient-to-br ${card.color}`}>
              <card.icon className="w-6 h-6 text-white" />
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  );
};
