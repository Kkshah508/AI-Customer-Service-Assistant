import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Upload, FileText, Trash2, Loader2, Database } from 'lucide-react';
import { apiService } from '../services/api';
import toast from 'react-hot-toast';

const KnowledgeBase = () => {
  const [documents, setDocuments] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    setIsLoading(true);
    try {
      const docs = await apiService.getKnowledgeBaseDocuments();
      setDocuments(docs.documents || []);
    } catch (error) {
      console.error('Error loading documents:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
      toast.error('File too large. Maximum size is 10MB.');
      return;
    }

    setIsUploading(true);
    try {
      await apiService.uploadKnowledgeDocument(file);
      toast.success('Document uploaded and processed successfully');
      await loadDocuments();
    } catch (error) {
      toast.error('Failed to upload document');
    } finally {
      setIsUploading(false);
      event.target.value = '';
    }
  };

  const handleDelete = async (docId) => {
    try {
      await apiService.deleteKnowledgeDocument(docId);
      toast.success('Document deleted');
      await loadDocuments();
    } catch (error) {
      toast.error('Failed to delete document');
    }
  };

  return (
    <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl p-5 mb-6">
      <div className="flex items-center space-x-2 mb-3">
        <Database className="w-5 h-5 text-indigo-700" />
        <h3 className="font-bold text-indigo-900">Knowledge Base</h3>
      </div>

      <div className="mb-4">
        <label className="flex items-center justify-center w-full px-4 py-3 bg-white border-2 border-dashed border-indigo-300 rounded-lg cursor-pointer hover:border-indigo-500 hover:bg-indigo-50 transition-all">
          <input
            type="file"
            className="hidden"
            onChange={handleFileUpload}
            disabled={isUploading}
            accept=".pdf,.docx,.doc,.txt,.html,.md"
          />
          {isUploading ? (
            <div className="flex items-center space-x-2 text-indigo-600">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span className="text-sm font-medium">Processing...</span>
            </div>
          ) : (
            <div className="flex items-center space-x-2 text-indigo-600">
              <Upload className="w-4 h-4" />
              <span className="text-sm font-medium">Upload Document</span>
            </div>
          )}
        </label>
        <p className="text-xs text-indigo-600 mt-1 text-center">
          PDF, DOCX, TXT, HTML, MD (Max 10MB)
        </p>
      </div>

      <div className="space-y-2 max-h-48 overflow-y-auto">
        {isLoading ? (
          <div className="flex items-center justify-center py-4">
            <Loader2 className="w-5 h-5 animate-spin text-indigo-600" />
          </div>
        ) : documents.length === 0 ? (
          <p className="text-xs text-indigo-600 text-center py-4">
            No documents uploaded yet
          </p>
        ) : (
          documents.map((doc) => (
            <motion.div
              key={doc.id}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center justify-between bg-white/70 rounded-lg p-2"
            >
              <div className="flex items-center space-x-2 flex-1 min-w-0">
                <FileText className="w-4 h-4 text-indigo-600 flex-shrink-0" />
                <span className="text-xs text-indigo-900 truncate" title={doc.filename}>
                  {doc.filename}
                </span>
              </div>
              <button
                onClick={() => handleDelete(doc.id)}
                className="p-1 hover:bg-red-100 rounded transition-colors flex-shrink-0"
                title="Delete document"
              >
                <Trash2 className="w-3 h-3 text-red-600" />
              </button>
            </motion.div>
          ))
        )}
      </div>
    </div>
  );
};

export default KnowledgeBase;
