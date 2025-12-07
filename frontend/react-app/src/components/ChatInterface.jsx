import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Send, Loader2, Hand, Phone, HelpCircle } from 'lucide-react';
import useStore from '../store/useStore';
import { apiService } from '../services/api';
import toast from 'react-hot-toast';
import ChatMessage from './ChatMessage';
import VoiceRecorder from './VoiceRecorder';
import QuickActions from './QuickActions';
import LiveKitVoice from './LiveKitVoice';
import TypingIndicator from './TypingIndicator';
import ConversationSearch from './ConversationSearch';

const ChatInterface = () => {
  const [inputMessage, setInputMessage] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const chatEndRef = useRef(null);
  const inputRef = useRef(null);
  const messageRefs = useRef([]);
  
  const { 
    userId, 
    conversationHistory, 
    addMessage, 
    setSessionId,
    isAssistantReady,
    updateSystemStats
  } = useStore();

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversationHistory]);

  const handleSendMessage = async (message = inputMessage, isVoice = false) => {
    if (!message.trim() || isProcessing) return;

    const userMessage = message.trim();
    setInputMessage('');
    setIsProcessing(true);

    addMessage({
      role: 'user',
      message: userMessage,
      is_voice: isVoice
    });

    try {
      const response = await apiService.processMessage(userId, userMessage, null);
      
      addMessage({
        role: 'assistant',
        message: response.message || 'Sorry, I had trouble understanding that.',
        metadata: response.metadata || {}
      });

      if (response.conversation_id) {
        setSessionId(response.conversation_id);
      }

      updateSystemStats();

      if (isVoice && response.message) {
        try {
          const audioBlob = await apiService.textToSpeech(response.message);
          const audioUrl = URL.createObjectURL(audioBlob);
          const audio = new Audio(audioUrl);
          audio.play();
        } catch (error) {
          console.log('Voice response not available');
        }
      }

    } catch (error) {
      console.error('Error processing message:', error);
      toast.error('Temporary issue. Showing basic response.');
      
      addMessage({
        role: 'assistant',
        message: 'I am having trouble with some services right now, but I can still help with basic questions.',
        metadata: { fallback: true }
      });
    } finally {
      setIsProcessing(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleQuickAction = (message) => {
    handleSendMessage(message);
  };

  const scrollToMessage = (index) => {
    if (messageRefs.current[index]) {
      messageRefs.current[index].scrollIntoView({ behavior: 'smooth', block: 'center' });
      messageRefs.current[index].classList.add('ring-2', 'ring-primary-500');
      setTimeout(() => {
        messageRefs.current[index]?.classList.remove('ring-2', 'ring-primary-500');
      }, 2000);
    }
  };

  return (
    <div className="flex-1 flex flex-col bg-gradient-to-br from-gray-50 to-gray-100 h-full overflow-hidden">
      <div className="flex-1 flex flex-col max-w-6xl w-full mx-auto h-full overflow-hidden">
        <div className="flex-shrink-0">
          <QuickActions onAction={handleQuickAction} />
        </div>
        
        {conversationHistory.length > 0 && (
          <div className="px-6 pt-4 flex-shrink-0">
            <ConversationSearch 
              messages={conversationHistory} 
              onResultClick={scrollToMessage}
            />
          </div>
        )}

        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4 min-h-0 scroll-smooth" style={{ scrollBehavior: 'smooth' }}>
          {conversationHistory.length === 0 ? (
            <WelcomeMessage />
          ) : (
            conversationHistory.map((msg, index) => (
              <div key={index} ref={el => messageRefs.current[index] = el} className="rounded-lg transition-all">
                <ChatMessage message={msg} />
              </div>
            ))
          )}
          {isProcessing && <TypingIndicator />}
          <div ref={chatEndRef} />
        </div>

        <div className="border-t border-gray-200 bg-white">
          <LiveKitVoice userId={userId} />
          <VoiceRecorder onTranscript={(text) => handleSendMessage(text, true)} />
          
          <div className="p-4 max-w-4xl mx-auto">
            <div className="flex items-end space-x-3">
              <div className="flex-1 relative">
                <textarea
                  ref={inputRef}
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your message here... (e.g., 'I need help with my order')"
                  disabled={!isAssistantReady || isProcessing}
                  rows={1}
                  className="w-full px-4 py-3 pr-12 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition-all resize-none disabled:bg-gray-100 disabled:cursor-not-allowed"
                  style={{ minHeight: '48px', maxHeight: '120px' }}
                />
              </div>
              
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => handleSendMessage()}
                disabled={!inputMessage.trim() || !isAssistantReady || isProcessing}
                className="btn-primary flex items-center justify-center w-12 h-12 rounded-xl"
              >
                {isProcessing ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </motion.button>
            </div>
            
            <p className="text-xs text-gray-500 mt-2 text-center">
              Press Enter to send • Shift+Enter for new line
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

const WelcomeMessage = () => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    className="card max-w-2xl mx-auto"
  >
    <div className="text-center">
      <motion.div
        animate={{ rotate: [0, 10, -10, 0] }}
        transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
        className="inline-block mb-4"
      >
        <Hand className="w-16 h-16 text-primary-500" />
      </motion.div>
      
      <h2 className="text-2xl font-bold text-gray-800 mb-3">
        Welcome to Customer Service
      </h2>
      
      <p className="text-gray-600 mb-6">
        I can help you with various inquiries and support needs
      </p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-left">
        <FeatureCard
          icon={<Phone className="w-6 h-6" />}
          title="Account Support"
          description="Get help with your account and services"
        />
        <FeatureCard
          icon={<HelpCircle className="w-6 h-6" />}
          title="General Inquiries"
          description="Ask questions about our services"
        />
      </div>
      
      <p className="text-sm text-gray-500 mt-6">
        Choose a quick action above or type your message below!
      </p>
    </div>
  </motion.div>
);

const FeatureCard = ({ icon, title, description }) => (
  <div className="flex items-start space-x-3 p-4 bg-gradient-to-br from-primary-50 to-primary-100 rounded-lg">
    <div className="text-primary-600 mt-1">{icon}</div>
    <div>
      <h3 className="font-semibold text-gray-800 mb-1">{title}</h3>
      <p className="text-sm text-gray-600">{description}</p>
    </div>
  </div>
);

const TypingIndicatorLocal = () => (
  <motion.div
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    className="flex items-center space-x-2"
  >
    <div className="chat-bubble-assistant">
      <div className="flex space-x-2">
        <motion.div
          animate={{ scale: [1, 1.5, 1] }}
          transition={{ duration: 1, repeat: Infinity, delay: 0 }}
          className="w-2 h-2 bg-gray-400 rounded-full"
        />
        <motion.div
          animate={{ scale: [1, 1.5, 1] }}
          transition={{ duration: 1, repeat: Infinity, delay: 0.2 }}
          className="w-2 h-2 bg-gray-400 rounded-full"
        />
        <motion.div
          animate={{ scale: [1, 1.5, 1] }}
          transition={{ duration: 1, repeat: Infinity, delay: 0.4 }}
          className="w-2 h-2 bg-gray-400 rounded-full"
        />
      </div>
    </div>
  </motion.div>
);

export default ChatInterface;
