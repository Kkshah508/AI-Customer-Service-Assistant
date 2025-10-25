import React from 'react';
import { motion } from 'framer-motion';
import { Hand, Phone, HelpCircle, Package, CreditCard, ShoppingBag } from 'lucide-react';

const QuickActions = ({ onAction }) => {
  const actions = [
    {
      icon: <Hand className="w-5 h-5" />,
      label: 'Say Hello',
      message: 'Hello! How can you help me today?',
      color: 'from-blue-500 to-blue-600'
    },
    {
      icon: <Package className="w-5 h-5" />,
      label: 'Track Order',
      message: 'I need to track my order status.',
      color: 'from-green-500 to-green-600'
    },
    {
      icon: <Phone className="w-5 h-5" />,
      label: 'Account Help',
      message: 'I need help with my account.',
      color: 'from-purple-500 to-purple-600'
    },
    {
      icon: <CreditCard className="w-5 h-5" />,
      label: 'Billing Issue',
      message: 'I have a billing or payment question.',
      color: 'from-orange-500 to-orange-600'
    },
    {
      icon: <ShoppingBag className="w-5 h-5" />,
      label: 'Return Item',
      message: 'I need to return or exchange an item.',
      color: 'from-red-500 to-red-600'
    },
    {
      icon: <HelpCircle className="w-5 h-5" />,
      label: 'General Help',
      message: 'I have a general question.',
      color: 'from-indigo-500 to-indigo-600'
    }
  ];

  return (
    <div className="border-b border-gray-200 bg-white px-6 py-4">
      <div className="max-w-4xl mx-auto">
        <h3 className="text-sm font-semibold text-gray-700 mb-3">Quick Actions</h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {actions.map((action, index) => (
            <motion.button
              key={index}
              whileHover={{ scale: 1.02, y: -2 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => onAction(action.message)}
              className={`flex items-center justify-center space-x-2 bg-gradient-to-r ${action.color} text-white font-medium py-3 px-4 rounded-lg shadow-md hover:shadow-lg transition-all`}
            >
              {action.icon}
              <span>{action.label}</span>
            </motion.button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default QuickActions;
