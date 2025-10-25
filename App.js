import React, { useEffect } from 'react';
import { Toaster } from 'react-hot-toast';
import ChatInterface from './components/ChatInterface';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import useStore from './store/useStore';
import { apiService } from './services/api';

function App() {
  const { setAssistantReady, setSystemStats } = useStore();

  useEffect(() => {
    const initializeApp = async () => {
      try {
        await apiService.initializeAssistant();
        setAssistantReady(true);
        
        const stats = await apiService.getSystemStats();
        setSystemStats(stats);
      } catch (error) {
        console.error('Failed to initialize assistant:', error);
        setAssistantReady(false);
      }
    };

    initializeApp();

    const statsInterval = setInterval(async () => {
      try {
        const stats = await apiService.getSystemStats();
        setSystemStats(stats);
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      }
    }, 30000);

    return () => clearInterval(statsInterval);
  }, [setAssistantReady, setSystemStats]);

  return (
    <div className="flex h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#333',
            color: '#fff',
          },
        }}
      />
      
      <Sidebar />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <ChatInterface />
      </div>
    </div>
  );
}

export default App;
