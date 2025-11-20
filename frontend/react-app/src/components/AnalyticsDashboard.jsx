import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Activity,
  Users,
  MessageSquare,
  AlertTriangle,
  Clock,
  TrendingUp,
  BarChart3,
  PieChart
} from 'lucide-react';
import { apiService } from '../services/api';

const AnalyticsDashboard = ({ onClose }) => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
    const interval = setInterval(loadStats, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadStats = async () => {
    try {
      const data = await apiService.getSystemStats();
      setStats(data);
      setLoading(false);
    } catch (error) {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      >
        <div className="bg-white rounded-2xl p-8 max-w-4xl w-full mx-4">
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-gray-200 rounded w-1/3" />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[1, 2, 3, 4].map(i => (
                <div key={i} className="h-32 bg-gray-200 rounded" />
              ))}
            </div>
          </div>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="bg-white rounded-2xl p-8 max-w-6xl w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-3xl font-bold text-gray-800 flex items-center">
            <BarChart3 className="mr-3 text-primary-600" />
            Analytics Dashboard
          </h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl font-bold"
          >
            ×
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            icon={<Users className="w-8 h-8" />}
            title="Active Sessions"
            value={stats?.active_sessions || 0}
            color="blue"
            trend="+12%"
          />
          <StatCard
            icon={<MessageSquare className="w-8 h-8" />}
            title="Total Conversations"
            value={stats?.total_conversations || 0}
            color="green"
            trend="+23%"
          />
          <StatCard
            icon={<AlertTriangle className="w-8 h-8" />}
            title="Emergency Responses"
            value={stats?.emergency_responses || 0}
            color="red"
            trend="-5%"
          />
          <StatCard
            icon={<Clock className="w-8 h-8" />}
            title="Uptime (hours)"
            value={(stats?.system_uptime_hours || 0).toFixed(1)}
            color="purple"
            trend="100%"
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6">
            <h3 className="text-lg font-bold text-blue-900 mb-4 flex items-center">
              <Activity className="w-5 h-5 mr-2" />
              System Health
            </h3>
            <div className="space-y-3">
              <HealthBar label="API Response Time" value={95} color="green" />
              <HealthBar label="Database Performance" value={88} color="blue" />
              <HealthBar label="Memory Usage" value={62} color="yellow" />
              <HealthBar label="CPU Usage" value={45} color="green" />
            </div>
          </div>

          <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-6">
            <h3 className="text-lg font-bold text-purple-900 mb-4 flex items-center">
              <PieChart className="w-5 h-5 mr-2" />
              Intent Distribution
            </h3>
            <div className="space-y-3">
              <IntentBar label="Order Status" percentage={35} color="blue" />
              <IntentBar label="Product Inquiry" percentage={28} color="green" />
              <IntentBar label="Complaint" percentage={18} color="red" />
              <IntentBar label="General Info" percentage={12} color="yellow" />
              <IntentBar label="Other" percentage={7} color="gray" />
            </div>
          </div>
        </div>

        <div className="mt-6 bg-gray-50 rounded-xl p-4">
          <p className="text-sm text-gray-600">
            Last updated: {new Date().toLocaleString()}
          </p>
        </div>
      </motion.div>
    </motion.div>
  );
};

const StatCard = ({ icon, title, value, color, trend }) => {
  const colorClasses = {
    blue: 'from-blue-500 to-blue-600',
    green: 'from-green-500 to-green-600',
    red: 'from-red-500 to-red-600',
    purple: 'from-purple-500 to-purple-600'
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 border-2 border-gray-100">
      <div className={`w-12 h-12 bg-gradient-to-br ${colorClasses[color]} rounded-lg flex items-center justify-center text-white mb-4`}>
        {icon}
      </div>
      <h3 className="text-sm font-medium text-gray-600 mb-1">{title}</h3>
      <div className="flex items-end justify-between">
        <p className="text-3xl font-bold text-gray-800">{value}</p>
        <div className="flex items-center text-xs text-green-600">
          <TrendingUp className="w-3 h-3 mr-1" />
          {trend}
        </div>
      </div>
    </div>
  );
};

const HealthBar = ({ label, value, color }) => {
  const colorClasses = {
    green: 'bg-green-500',
    blue: 'bg-blue-500',
    yellow: 'bg-yellow-500',
    red: 'bg-red-500'
  };

  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="font-medium text-blue-900">{label}</span>
        <span className="text-blue-700">{value}%</span>
      </div>
      <div className="w-full bg-blue-200 rounded-full h-2">
        <div
          className={`${colorClasses[color]} h-2 rounded-full transition-all duration-500`}
          style={{ width: `${value}%` }}
        />
      </div>
    </div>
  );
};

const IntentBar = ({ label, percentage, color }) => {
  const colorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    red: 'bg-red-500',
    yellow: 'bg-yellow-500',
    gray: 'bg-gray-500'
  };

  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="font-medium text-purple-900">{label}</span>
        <span className="text-purple-700">{percentage}%</span>
      </div>
      <div className="w-full bg-purple-200 rounded-full h-2">
        <div
          className={`${colorClasses[color]} h-2 rounded-full transition-all duration-500`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};

export default AnalyticsDashboard;
