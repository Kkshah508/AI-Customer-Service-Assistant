import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const e = new Error('Request failed');
    e.status = (error && error.response && error.response.status) ? error.response.status : 0;
    return Promise.reject(e);
  }
);

export const apiService = {
  async processMessage(userId, message, patientAge = null) {
    const response = await api.post('/api/process', {
      user_id: userId,
      message: message,
      patient_age: patientAge
    });
    return response.data;
  },

  async getSystemStats() {
    const response = await api.get('/api/stats');
    return response.data;
  },

  async exportConversation(userId) {
    const response = await api.get(`/api/export/${userId}`);
    return response.data;
  },

  async resetConversation(userId) {
    const response = await api.post('/api/reset', { user_id: userId });
    return response.data;
  },

  async processVoiceAudio(audioBlob) {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.wav');
    
    const response = await api.post('/api/voice/process', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async textToSpeech(text) {
    const response = await api.post('/api/voice/tts', 
      { text }, 
      { responseType: 'blob' }
    );
    return response.data;
  },

  async initializeAssistant() {
    const response = await api.get('/api/initialize');
    return response.data;
  },

  async getLiveKitStatus() {
    const response = await api.get('/api/livekit/status');
    return response.data;
  },

  async createLiveKitRoom(userId) {
    const response = await api.post('/api/livekit/room/create', {
      user_id: userId
    });
    return response.data;
  },

  async getLiveKitToken(roomName, participantIdentity) {
    const response = await api.post('/api/livekit/token', {
      room_name: roomName,
      participant_identity: participantIdentity
    });
    return response.data;
  },

  async getKnowledgeBaseDocuments() {
    const response = await api.get('/api/knowledge/documents');
    return response.data;
  },

  async uploadKnowledgeDocument(file) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/api/knowledge/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async deleteKnowledgeDocument(docId) {
    const response = await api.delete(`/api/knowledge/documents/${docId}`);
    return response.data;
  }
};

export default api;
