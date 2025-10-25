import React from 'react';
import { motion } from 'framer-motion';
import { Bot, User, Mic, AlertTriangle, AlertCircle } from 'lucide-react';
import { format } from 'date-fns';

const ChatMessage = ({ message }) => {
  const isUser = message.role === 'user';
  const isSystem = message.role === 'system';
  const timestamp = message.timestamp ? new Date(message.timestamp) : new Date();
  const timeStr = format(timestamp, 'HH:mm:ss');
  
  const urgency = message.metadata?.urgency_level || 'low';
  const isVoice = message.is_voice;

  const getUrgencyColor = () => {
    switch (urgency) {
      case 'critical':
        return 'border-red-500 bg-red-50';
      case 'high':
        return 'border-orange-500 bg-orange-50';
      case 'medium':
        return 'border-yellow-500 bg-yellow-50';
      default:
        return 'border-gray-200';
    }
  };

  if (isSystem) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="flex justify-center"
      >
        <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-2 rounded-lg text-sm">
          {message.message}
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: isUser ? 20 : -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
      className={`flex items-start space-x-3 ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}
    >
      <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
        isUser ? 'bg-primary-500' : 'bg-gray-700'
      }`}>
        {isUser ? (
          <User className="w-5 h-5 text-white" />
        ) : (
          <Bot className="w-5 h-5 text-white" />
        )}
      </div>

      <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} max-w-[70%]`}>
        <div className="flex items-center space-x-2 mb-1">
          <span className="text-xs font-semibold text-gray-600">
            {isUser ? 'You' : 'Customer Service Assistant'}
          </span>
          <span className="text-xs text-gray-400">{timeStr}</span>
          {isVoice && (
            <div className="flex items-center space-x-1 text-xs text-primary-600">
              <Mic className="w-3 h-3" />
            </div>
          )}
        </div>

        <div className={`${
          isUser ? 'chat-bubble-user' : `chat-bubble-assistant ${getUrgencyColor()}`
        }`}>
          {urgency === 'critical' && !isUser && (
            <div className="flex items-center space-x-2 mb-2 text-red-600">
              <AlertTriangle className="w-4 h-4" />
              <span className="text-xs font-bold">URGENT</span>
            </div>
          )}
          {urgency === 'high' && !isUser && (
            <div className="flex items-center space-x-2 mb-2 text-orange-600">
              <AlertCircle className="w-4 h-4" />
              <span className="text-xs font-bold">HIGH PRIORITY</span>
            </div>
          )}
          
          <p className="whitespace-pre-wrap leading-relaxed">
            {message.message}
          </p>
        </div>
      </div>
    </motion.div>
  );
};

export default ChatMessage;
