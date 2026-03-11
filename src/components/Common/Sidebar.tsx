import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Package, TriangleAlert as AlertTriangle, Lightbulb, ChartBar as BarChart3 } from 'lucide-react';
import { motion } from 'framer-motion';

const navItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/shipments', icon: Package, label: 'Shipments' },
  { to: '/alerts', icon: AlertTriangle, label: 'Alerts' },
  { to: '/recommendations', icon: Lightbulb, label: 'Recommendations' },
  { to: '/analytics', icon: BarChart3, label: 'Analytics' },
];

export const Sidebar: React.FC = () => {
  return (
    <motion.aside
      initial={{ x: -100, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      className="glass w-64 min-h-screen p-6 border-r border-white/10"
    >
      <nav className="space-y-2">
        {navItems.map((item, index) => (
          <motion.div
            key={item.to}
            initial={{ x: -50, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: index * 0.1 }}
          >
            <NavLink
              to={item.to}
              className={({ isActive }) =>
                `flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                  isActive
                    ? 'bg-gradient-to-r from-primary to-secondary text-white shadow-lg'
                    : 'text-light hover:bg-white/5 hover:text-accent'
                }`
              }
            >
              <item.icon className="w-5 h-5" />
              <span className="font-medium">{item.label}</span>
            </NavLink>
          </motion.div>
        ))}
      </nav>
    </motion.aside>
  );
};
