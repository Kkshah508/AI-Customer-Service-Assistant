import React from 'react';
import { motion } from 'framer-motion';

const LoadingSkeleton = () => {
  return (
    <div className="space-y-4 p-6">
      {[1, 2, 3].map((i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex items-start space-x-3"
        >
          <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gray-200 animate-pulse" />
          <div className="flex-1 space-y-2">
            <div className="h-3 bg-gray-200 rounded animate-pulse w-24" />
            <div className="h-20 bg-gray-200 rounded-2xl animate-pulse" />
          </div>
        </motion.div>
      ))}
    </div>
  );
};

export default LoadingSkeleton;
