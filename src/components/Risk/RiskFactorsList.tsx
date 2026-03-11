import React from 'react';
import { CircleAlert as AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';

interface RiskFactorsListProps {
  factors: string[];
}

export const RiskFactorsList: React.FC<RiskFactorsListProps> = ({ factors }) => {
  return (
    <div className="space-y-2">
      <h4 className="text-sm font-semibold text-accent flex items-center space-x-2">
        <AlertCircle className="w-4 h-4" />
        <span>Top Risk Factors</span>
      </h4>
      <ul className="space-y-1">
        {factors.map((factor, index) => (
          <motion.li
            key={index}
            initial={{ x: -20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: index * 0.1 }}
            className="text-sm text-light flex items-start space-x-2"
          >
            <span className="text-accent mt-1">•</span>
            <span>{factor}</span>
          </motion.li>
        ))}
      </ul>
    </div>
  );
};
