import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Settings,
  RotateCcw,
  Info,
  Activity,
  Users,
  MessageSquare,
  AlertTriangle,
  Clock,
  ChevronLeft,
  ChevronRight,
  Download,
  BarChart3
} from 'lucide-react';
import useStore from '../store/useStore';
import { apiService } from '../services/api';
import toast from 'react-hot-toast';
import KnowledgeBase from './KnowledgeBase';
import AnalyticsDashboard from './AnalyticsDashboard';

const Sidebar = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [showAnalytics, setShowAnalytics] = useState(false);
  const { 
    userName, 
    setUserName, 
    clearConversation, 
    systemStats,
    userId 
  } = useStore();

  const handleReset = async () => {
    try {
      await apiService.resetConversation(userId);
      clearConversation();
      toast.success('Conversation cleared successfully');
    } catch (error) {
      toast.error('Failed to clear conversation');
    }
  };

  const handleExport = async () => {
    try {
      const data = await apiService.exportConversation(userId);
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `conversation_${userId}_${new Date().toISOString()}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      toast.success('Conversation exported successfully');
    } catch (error) {
      toast.error('Failed to export conversation');
    }
  };

  return (
    <motion.aside
      initial={{ x: -300 }}
      animate={{ x: 0, width: isCollapsed ? '80px' : '320px' }}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
      className="bg-white shadow-2xl relative flex flex-col"
    >
      <button
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="absolute -right-3 top-6 bg-primary-500 text-white p-2 rounded-full shadow-lg hover:bg-primary-600 transition-colors z-10"
      >
        {isCollapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
      </button>

      <AnimatePresence mode="wait">
        {!isCollapsed && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex-1 overflow-y-auto p-6"
          >
            <div className="mb-8">
              <div className="flex items-center space-x-2 mb-4">
                <Settings className="w-5 h-5 text-primary-600" />
                <h2 className="text-xl font-bold text-gray-800">Settings</h2>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Your Name
                  </label>
                  <input
                    type="text"
                    value={userName}
                    onChange={(e) => setUserName(e.target.value)}
                    placeholder="Enter your name"
                    className="input-field"
                  />
                </div>
              </div>
            </div>

            <div className="border-t border-gray-200 pt-6 mb-6 space-y-3">
              <button
                onClick={handleExport}
                className="w-full flex items-center justify-center space-x-2 bg-blue-50 hover:bg-blue-100 text-blue-600 font-medium py-3 px-4 rounded-lg transition-all"
              >
                <Download size={18} />
                <span>Export Chat</span>
              </button>
              <button
                onClick={handleReset}
                className="w-full flex items-center justify-center space-x-2 bg-red-50 hover:bg-red-100 text-red-600 font-medium py-3 px-4 rounded-lg transition-all"
              >
                <RotateCcw size={18} />
                <span>Clear Chat</span>
              </button>
              <button
                onClick={() => setShowAnalytics(true)}
                className="w-full flex items-center justify-center space-x-2 bg-purple-50 hover:bg-purple-100 text-purple-600 font-medium py-3 px-4 rounded-lg transition-all"
              >
                <BarChart3 size={18} />
                <span>Analytics</span>
              </button>
            </div>

            <KnowledgeBase />

            <div className="bg-gradient-to-br from-primary-50 to-primary-100 rounded-xl p-5 mb-6">
              <div className="flex items-center space-x-2 mb-3">
                <Activity className="w-5 h-5 text-primary-700" />
                <h3 className="font-bold text-primary-900">System Status</h3>
              </div>
              
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-primary-700">Status</span>
                  <span className="flex items-center text-sm font-semibold text-green-600">
                    <span className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></span>
                    Operational
                  </span>
                </div>
                
                <StatItem
                  icon={<Users size={16} />}
                  label="Active Sessions"
                  value={systemStats.active_sessions}
                />
                
                <StatItem
                  icon={<MessageSquare size={16} />}
                  label="Total Conversations"
                  value={systemStats.total_conversations}
                />
                
                <StatItem
                  icon={<AlertTriangle size={16} />}
                  label="Emergency Responses"
                  value={systemStats.emergency_responses}
                />
                
                <StatItem
                  icon={<Clock size={16} />}
                  label="Uptime (hours)"
                  value={systemStats.system_uptime_hours?.toFixed(1) || '0.0'}
                />
              </div>
            </div>

            <div className="bg-blue-50 rounded-xl p-5">
              <div className="flex items-start space-x-2">
                <Info className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                <div>
                  <h4 className="font-bold text-blue-900 mb-2">About</h4>
                  <p className="text-sm text-blue-700 leading-relaxed">
                    AI Assistant with intelligent customer service capabilities, 
                    voice and text support.
                  </p>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {isCollapsed && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex flex-col items-center space-y-6 p-4 mt-4"
        >
          <Settings className="w-6 h-6 text-gray-600" />
          <button
            onClick={handleReset}
            className="p-3 bg-red-50 hover:bg-red-100 text-red-600 rounded-lg transition-colors"
          >
            <RotateCcw size={20} />
          </button>
          <Activity className="w-6 h-6 text-primary-600" />
        </motion.div>
      )}
      
      {showAnalytics && <AnalyticsDashboard onClose={() => setShowAnalytics(false)} />}
    </motion.aside>
  );
};

const StatItem = ({ icon, label, value }) => (
  <div className="flex items-center justify-between bg-white/50 rounded-lg p-2">
    <div className="flex items-center space-x-2">
      <span className="text-primary-600">{icon}</span>
      <span className="text-xs text-primary-700">{label}</span>
    </div>
    <span className="text-sm font-bold text-primary-900">{value}</span>
  </div>
);

export default Sidebar;
