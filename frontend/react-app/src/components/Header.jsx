import React from 'react';
import { Bot, Sparkles, Moon, Sun } from 'lucide-react';
import { motion } from 'framer-motion';
import useStore from '../store/useStore';

const Header = () => {
  const { darkMode, toggleDarkMode } = useStore();
  
  return (
    <motion.header 
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className={`${darkMode ? 'bg-gradient-to-r from-gray-800 to-gray-900' : 'bg-gradient-to-r from-primary-500 to-primary-600'} text-white shadow-xl relative`}
    >
      <div className="px-6 py-5">
        <button
          onClick={toggleDarkMode}
          className="absolute right-6 top-1/2 -translate-y-1/2 p-2 rounded-lg hover:bg-white/10 transition-colors"
        >
          {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
        </button>
        
        <div className="flex items-center justify-center space-x-3">
          <motion.div
            animate={{ rotate: [0, 360] }}
            transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
            className="relative"
          >
            <Bot className="w-10 h-10" />
            <motion.div
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
              className="absolute -top-1 -right-1"
            >
              <Sparkles className="w-4 h-4 text-yellow-300" />
            </motion.div>
          </motion.div>
          
          <div className="text-center">
            <h1 className="text-3xl font-bold tracking-tight">
              AI Customer Service Assistant
            </h1>
            <p className="text-primary-100 text-sm mt-1">
              Intelligent Support & Automated Assistance
            </p>
          </div>
        </div>
      </div>
    </motion.header>
  );
};

export default Header;
