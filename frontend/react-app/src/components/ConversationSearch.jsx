import React, { useState, useMemo } from 'react';
import { Search, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const ConversationSearch = ({ messages, onResultClick }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [showResults, setShowResults] = useState(false);

  const searchResults = useMemo(() => {
    if (!searchQuery.trim()) return [];
    
    const query = searchQuery.toLowerCase();
    return messages.filter((msg, index) => {
      const messageText = msg.message.toLowerCase();
      return messageText.includes(query);
    }).map((msg, idx) => ({
      ...msg,
      originalIndex: messages.indexOf(msg)
    }));
  }, [searchQuery, messages]);

  const handleSearch = (e) => {
    const value = e.target.value;
    setSearchQuery(value);
    setShowResults(value.trim().length > 0);
  };

  const clearSearch = () => {
    setSearchQuery('');
    setShowResults(false);
  };

  const highlightText = (text, query) => {
    if (!query) return text;
    
    const parts = text.split(new RegExp(`(${query})`, 'gi'));
    return parts.map((part, i) => 
      part.toLowerCase() === query.toLowerCase() ? 
        <mark key={i} className="bg-yellow-200 dark:bg-yellow-600 rounded px-1">{part}</mark> : 
        part
    );
  };

  return (
    <div className="relative">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          type="text"
          value={searchQuery}
          onChange={handleSearch}
          placeholder="Search conversations..."
          className="w-full pl-10 pr-10 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
        {searchQuery && (
          <button
            onClick={clearSearch}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      <AnimatePresence>
        {showResults && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute top-full mt-2 w-full bg-white rounded-lg shadow-xl border border-gray-200 max-h-96 overflow-y-auto z-50"
          >
            {searchResults.length > 0 ? (
              <div className="p-2">
                <div className="text-xs text-gray-500 px-3 py-2 font-medium">
                  Found {searchResults.length} {searchResults.length === 1 ? 'result' : 'results'}
                </div>
                {searchResults.map((result, idx) => (
                  <button
                    key={idx}
                    onClick={() => {
                      onResultClick(result.originalIndex);
                      clearSearch();
                    }}
                    className="w-full text-left px-3 py-3 hover:bg-gray-50 rounded-lg transition-colors"
                  >
                    <div className="flex items-center space-x-2 mb-1">
                      <span className={`text-xs font-semibold ${result.role === 'user' ? 'text-primary-600' : 'text-gray-600'}`}>
                        {result.role === 'user' ? 'You' : 'Assistant'}
                      </span>
                      <span className="text-xs text-gray-400">
                        {result.timestamp ? new Date(result.timestamp).toLocaleTimeString() : ''}
                      </span>
                    </div>
                    <p className="text-sm text-gray-700 line-clamp-2">
                      {highlightText(result.message, searchQuery)}
                    </p>
                  </button>
                ))}
              </div>
            ) : (
              <div className="p-8 text-center text-gray-500">
                <Search className="w-12 h-12 mx-auto mb-2 opacity-30" />
                <p className="text-sm">No results found</p>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ConversationSearch;
