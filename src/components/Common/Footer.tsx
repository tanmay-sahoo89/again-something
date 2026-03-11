import React from 'react';
import { motion } from 'framer-motion';

export const Footer: React.FC = () => {
  return (
    <motion.footer
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="glass border-t border-white/10 mt-auto"
    >
      <div className="container mx-auto px-4 py-6">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="text-light text-sm mb-4 md:mb-0">
            2026 Ship Risk AI. All rights reserved.
          </div>
          <div className="flex space-x-6 text-sm text-light">
            <a href="#" className="hover:text-accent transition-colors">
              Documentation
            </a>
            <a href="#" className="hover:text-accent transition-colors">
              API
            </a>
            <a href="#" className="hover:text-accent transition-colors">
              Support
            </a>
            <a href="#" className="hover:text-accent transition-colors">
              Privacy
            </a>
          </div>
        </div>
      </div>
    </motion.footer>
  );
};
