import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { Mic, Square, Volume2, Loader2 } from 'lucide-react';
import { apiService } from '../services/api';
import toast from 'react-hot-toast';

const VoiceRecorder = ({ onTranscript }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        await processAudio(audioBlob);
        
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      toast.success('Recording started');
    } catch (error) {
      console.error('Error accessing microphone:', error);
      toast.error('Failed to access microphone');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const processAudio = async (audioBlob) => {
    setIsProcessing(true);
    try {
      const response = await apiService.processVoiceAudio(audioBlob);
      if (response.text) {
        toast.success(`Recognized: ${response.text}`);
        onTranscript(response.text);
      } else {
        toast.error('Could not understand the audio');
      }
    } catch (error) {
      console.error('Error processing audio:', error);
      toast.error('Failed to process voice input');
    } finally {
      setIsProcessing(false);
    }
  };

  const testVoice = async () => {
    try {
      const audioBlob = await apiService.textToSpeech(
        "Hello! I'm your customer service assistant. How can I help you today?"
      );
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      audio.play();
      toast.success('Playing test voice');
    } catch (error) {
      console.error('Error testing voice:', error);
      toast.error('Voice output not available');
    }
  };

  return (
    <div className="border-b border-gray-200 bg-gradient-to-r from-primary-50 to-primary-100 px-4 py-3">
      <div className="max-w-4xl mx-auto flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Mic className="w-5 h-5 text-primary-600" />
          <span className="text-sm font-semibold text-primary-800">Voice Chat</span>
        </div>

        <div className="flex items-center space-x-3">
          {!isRecording ? (
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={startRecording}
              disabled={isProcessing}
              className="flex items-center space-x-2 bg-primary-500 hover:bg-primary-600 text-white font-medium py-2 px-4 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Mic className="w-4 h-4" />
              <span>Start Recording</span>
            </motion.button>
          ) : (
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={stopRecording}
              className="flex items-center space-x-2 bg-red-500 hover:bg-red-600 text-white font-medium py-2 px-4 rounded-lg transition-all animate-pulse"
            >
              <Square className="w-4 h-4" />
              <span>Stop Recording</span>
            </motion.button>
          )}

          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={testVoice}
            disabled={isProcessing || isRecording}
            className="flex items-center space-x-2 bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium py-2 px-4 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            title="Test voice output"
          >
            {isProcessing ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Volume2 className="w-4 h-4" />
            )}
            <span>Test Voice</span>
          </motion.button>
        </div>
      </div>
    </div>
  );
};

export default VoiceRecorder;
