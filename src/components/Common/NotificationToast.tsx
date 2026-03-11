import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, CircleCheck as CheckCircle, CircleAlert as AlertCircle, Info, TriangleAlert as AlertTriangle } from 'lucide-react';
import { useNotification } from '../../contexts/NotificationContext';

export const NotificationToast: React.FC = () => {
  const { notifications, removeNotification } = useNotification();

  const getIcon = (type: string) => {
    switch (type) {
      case 'success':
        return <CheckCircle className="w-5 h-5" />;
      case 'error':
        return <AlertCircle className="w-5 h-5" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5" />;
      case 'info':
        return <Info className="w-5 h-5" />;
      default:
        return <Info className="w-5 h-5" />;
    }
  };

  const getColor = (type: string) => {
    switch (type) {
      case 'success':
        return 'from-green-500 to-green-600';
      case 'error':
        return 'from-red-500 to-red-600';
      case 'warning':
        return 'from-orange-500 to-orange-600';
      case 'info':
        return 'from-blue-500 to-blue-600';
      default:
        return 'from-gray-500 to-gray-600';
    }
  };

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2">
      <AnimatePresence>
        {notifications.map((notification) => (
          <motion.div
            key={notification.id}
            initial={{ opacity: 0, x: 100 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 100 }}
            className={`glass border border-white/20 rounded-lg p-4 shadow-2xl max-w-sm`}
          >
            <div className="flex items-start space-x-3">
              <div className={`p-1 rounded bg-gradient-to-br ${getColor(notification.type)}`}>
                {getIcon(notification.type)}
              </div>
              <p className="flex-1 text-sm text-white">{notification.message}</p>
              <button
                onClick={() => removeNotification(notification.id)}
                className="text-light hover:text-white transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
};
