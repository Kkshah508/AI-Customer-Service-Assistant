import React from 'react';
import { Bot, Sparkles } from 'lucide-react';

const WelcomeMessage = () => {
  return (
    <div className="h-full flex items-center justify-center">
      <div className="text-center max-w-xl mx-auto bg-white/70 backdrop-blur rounded-2xl shadow-lg px-8 py-10">
        <div className="flex justify-center mb-4">
          <div className="relative">
            <div className="w-14 h-14 rounded-full bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center text-white">
              <Bot className="w-7 h-7" />
            </div>
            <div className="absolute -top-1 -right-1 text-yellow-300">
              <Sparkles className="w-4 h-4" />
            </div>
          </div>
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Welcome to your AI Customer Service Assistant
        </h2>
        <p className="text-sm text-gray-600 mb-4">
          Ask questions, handle customer issues, and explore voice and knowledge base features.
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-left text-sm text-gray-700">
          <div className="bg-primary-50 rounded-xl p-3">
            <p className="font-semibold text-primary-800 mb-1">Try asking:</p>
            <ul className="space-y-1 list-disc list-inside">
              <li>Where is my order?</li>
              <li>I need help with my account</li>
              <li>I want to return an item</li>
            </ul>
          </div>
          <div className="bg-gray-50 rounded-xl p-3">
            <p className="font-semibold text-gray-800 mb-1">Tips:</p>
            <ul className="space-y-1 list-disc list-inside">
              <li>Use voice recording to speak instead of typing.</li>
              <li>Upload documents to the knowledge base in the sidebar.</li>
              <li>Open Analytics to view system statistics.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WelcomeMessage;
