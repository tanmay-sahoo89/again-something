import React from 'react';
import { Link } from 'react-router-dom';
import { Ship, Bell, User, LogOut } from 'lucide-react';
import { motion } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext';
import { useShipmentContext } from '../../contexts/ShipmentContext';

export const Header: React.FC = () => {
  const { user, logout } = useAuth();
  const { alerts } = useShipmentContext();

  const criticalCount = alerts.filter((a) => a.risk_tier === 'CRITICAL').length;

  return (
    <motion.header
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      className="glass border-b border-white/10 sticky top-0 z-50"
    >
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center space-x-3">
            <div className="gradient-primary p-2 rounded-lg">
              <Ship className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white text-shadow">Ship Risk AI</h1>
              <p className="text-xs text-light">Intelligent Risk Management</p>
            </div>
          </Link>

          <div className="flex items-center space-x-6">
            <Link to="/dashboard" className="relative">
              <Bell className="w-6 h-6 text-light hover:text-accent transition-colors" />
              {criticalCount > 0 && (
                <motion.span
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="absolute -top-2 -right-2 bg-risk-critical text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold"
                >
                  {criticalCount}
                </motion.span>
              )}
            </Link>

            {user ? (
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <User className="w-5 h-5 text-light" />
                  <span className="text-sm text-light">{user.email}</span>
                </div>
                <button
                  onClick={logout}
                  className="flex items-center space-x-1 text-light hover:text-accent transition-colors"
                >
                  <LogOut className="w-5 h-5" />
                  <span className="text-sm">Logout</span>
                </button>
              </div>
            ) : (
              <Link to="/login" className="btn-primary">
                Login
              </Link>
            )}
          </div>
        </div>
      </div>
    </motion.header>
  );
};
