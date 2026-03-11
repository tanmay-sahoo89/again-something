import { RiskTier } from '../types/alert';
import { RISK_TIER_COLORS } from './constants';

export const getRiskTierColor = (tier: RiskTier): string => {
  return RISK_TIER_COLORS[tier];
};

export const calculateDaysRemaining = (etaDate: string): number => {
  const eta = new Date(etaDate);
  const now = new Date();
  const diffTime = eta.getTime() - now.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  return diffDays;
};

export const classNames = (...classes: (string | boolean | undefined)[]): string => {
  return classes.filter(Boolean).join(' ');
};

export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
};
