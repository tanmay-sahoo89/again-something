import React from 'react';
import { RiskTier as RiskTierType } from '../../types/alert';
import { getRiskTierColor } from '../../utils/helpers';
import { motion } from 'framer-motion';

interface RiskTierProps {
  tier: RiskTierType;
  probability: number;
  showProbability?: boolean;
}

export const RiskTier: React.FC<RiskTierProps> = ({ tier, probability, showProbability = true }) => {
  const color = getRiskTierColor(tier);

  return (
    <motion.div
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      className="inline-flex items-center space-x-2"
    >
      <div
        className="px-3 py-1 rounded-full font-semibold text-white text-sm shadow-lg"
        style={{ backgroundColor: color }}
      >
        {tier}
      </div>
      {showProbability && (
        <span className="text-sm text-light font-mono">
          {(probability * 100).toFixed(1)}%
        </span>
      )}
    </motion.div>
  );
};
