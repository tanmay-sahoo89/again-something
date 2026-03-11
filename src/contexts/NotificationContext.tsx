import React, { createContext, useContext, useState, ReactNode, useCallback } from 'react';

type NotificationType = 'success' | 'error' | 'warning' | 'info';

interface Notification {
  id: string;
  type: NotificationType;
  message: string;
  duration?: number;
}

interface NotificationContextType {
  notifications: Notification[];
  addNotification: (type: NotificationType, message: string, duration?: number) => void;
  removeNotification: (id: string) => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export const useNotification = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotification must be used within NotificationProvider');
  }
  return context;
};

interface NotificationProviderProps {
  children: ReactNode;
}

export const NotificationProvider: React.FC<NotificationProviderProps> = ({ children }) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  const removeNotification = useCallback((id: string) => {
    setNotifications((prev) => prev.filter((notif) => notif.id !== id));
  }, []);

  const addNotification = useCallback(
    (type: NotificationType, message: string, duration = 5000) => {
      const id = `notif-${Date.now()}-${Math.random()}`;
      const notification: Notification = { id, type, message, duration };

      setNotifications((prev) => [...prev, notification]);

      if (duration > 0) {
        setTimeout(() => {
          removeNotification(id);
        }, duration);
      }
    },
    [removeNotification]
  );

  const value: NotificationContextType = {
    notifications,
    addNotification,
    removeNotification,
  };

  return <NotificationContext.Provider value={value}>{children}</NotificationContext.Provider>;
};
