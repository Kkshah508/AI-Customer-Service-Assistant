import { create } from 'zustand';

const useStore = create((set, get) => ({
  userId: `user_${Date.now()}`,
  userName: '',
  conversationHistory: [],
  currentSessionId: null,
  emergencyMode: false,
  isAssistantReady: false,
  isLoading: false,
  darkMode: false,
  systemStats: {
    active_sessions: 0,
    total_conversations: 0,
    emergency_responses: 0,
    system_uptime_hours: 0
  },

  setUserName: (name) => set({ userName: name }),
  
  addMessage: (message) => set((state) => ({
    conversationHistory: [...state.conversationHistory, {
      ...message,
      timestamp: new Date().toISOString()
    }]
  })),
  
  clearConversation: () => set({
    conversationHistory: [],
    emergencyMode: false,
    currentSessionId: null
  }),
  
  setSessionId: (id) => set({ currentSessionId: id }),
  
  setEmergencyMode: (mode) => set({ emergencyMode: mode }),
  
  setAssistantReady: (ready) => set({ isAssistantReady: ready }),
  
  setLoading: (loading) => set({ isLoading: loading }),
  
  setSystemStats: (stats) => set({ systemStats: stats }),
  
  toggleDarkMode: () => set((state) => ({ darkMode: !state.darkMode })),
  
  updateSystemStats: () => {
    set((state) => ({
      systemStats: {
        ...state.systemStats,
        total_conversations: state.conversationHistory.length
      }
    }));
  }
}));

export default useStore;
