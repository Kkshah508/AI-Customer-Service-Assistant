import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Phone, PhoneOff, Loader2, Volume2, VolumeX } from 'lucide-react';
import { Room, RoomEvent } from 'livekit-client';
import { apiService } from '../services/api';
import toast from 'react-hot-toast';

const LiveKitVoice = ({ userId }) => {
  const [room, setRoom] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [agentSpeaking, setAgentSpeaking] = useState(false);
  const [livekitAvailable, setLivekitAvailable] = useState(false);

  useEffect(() => {
    checkLiveKitStatus();
    
    return () => {
      if (room) {
        room.disconnect();
      }
    };
  }, []);

  const checkLiveKitStatus = async () => {
    try {
      const status = await apiService.getLiveKitStatus();
      setLivekitAvailable(status.livekit_enabled && status.livekit_configured);
    } catch (error) {
      console.error('Error checking LiveKit status:', error);
      setLivekitAvailable(false);
    }
  };

  const connectToVoiceAgent = async () => {
    if (isConnecting || isConnected) return;

    setIsConnecting(true);
    try {
      const roomData = await apiService.createLiveKitRoom(userId);
      if (!roomData || !roomData.token || !roomData.url) {
        toast.error('Voice agent unavailable. Please try again later.');
        setIsConnecting(false);
        return;
      }
      
      const newRoom = new Room({
        adaptiveStream: true,
        dynacast: true,
        audioCaptureDefaults: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });

      newRoom.on(RoomEvent.Connected, () => {
        console.log('Connected to LiveKit room');
        setIsConnected(true);
        setIsConnecting(false);
        toast.success('Connected to voice agent');
      });

      newRoom.on(RoomEvent.Disconnected, () => {
        console.log('Disconnected from LiveKit room');
        setIsConnected(false);
        setIsConnecting(false);
        toast('Disconnected from voice agent');
      });

      newRoom.on(RoomEvent.TrackSubscribed, (track, publication, participant) => {
        if (track.kind === 'audio' && participant.identity !== userId) {
          const audioElement = track.attach();
          document.body.appendChild(audioElement);
          audioElement.play().catch(e => console.error('Error playing audio:', e));
        }
      });

      newRoom.on(RoomEvent.TrackUnsubscribed, (track) => {
        track.detach().forEach(element => element.remove());
      });

      newRoom.on(RoomEvent.ActiveSpeakersChanged, (speakers) => {
        const isAgentSpeaking = speakers.some(s => s.identity !== userId);
        setAgentSpeaking(isAgentSpeaking);
      });

      newRoom.on(RoomEvent.ConnectionStateChanged, (state) => {
        console.log('Connection state:', state);
      });

      await newRoom.connect(roomData.url, roomData.token);
      
      await newRoom.localParticipant.setMicrophoneEnabled(true);

      setRoom(newRoom);
    } catch (error) {
      console.error('Error connecting to voice agent:', error);
      toast.error('Failed to connect to voice agent');
      setIsConnecting(false);
    }
  };

  const disconnectFromVoiceAgent = useCallback(() => {
    if (room) {
      room.disconnect();
      setRoom(null);
      setIsConnected(false);
    }
  }, [room]);

  const toggleMute = async () => {
    if (room && room.localParticipant) {
      const enabled = !isMuted;
      await room.localParticipant.setMicrophoneEnabled(enabled);
      setIsMuted(!enabled);
      toast.success(enabled ? 'Microphone unmuted' : 'Microphone muted');
    }
  };

  if (!livekitAvailable) {
    return null;
  }

  return (
    <div className="border-b border-gray-200 bg-gradient-to-r from-indigo-50 to-purple-50 px-4 py-3">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="relative">
              <Phone className="w-5 h-5 text-indigo-600" />
              {isConnected && agentSpeaking && (
                <motion.div
                  className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full"
                  animate={{ scale: [1, 1.3, 1] }}
                  transition={{ repeat: Infinity, duration: 1.5 }}
                />
              )}
            </div>
            <div>
              <span className="text-sm font-semibold text-indigo-800">
                Voice Agent
              </span>
              {isConnected && (
                <p className="text-xs text-indigo-600">
                  {agentSpeaking ? 'Agent speaking...' : 'Connected'}
                </p>
              )}
            </div>
          </div>

          <div className="flex items-center space-x-2">
            {!isConnected ? (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={connectToVoiceAgent}
                disabled={isConnecting}
                className="flex items-center space-x-2 bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-4 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isConnecting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Connecting...</span>
                  </>
                ) : (
                  <>
                    <Phone className="w-4 h-4" />
                    <span>Connect</span>
                  </>
                )}
              </motion.button>
            ) : (
              <>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={toggleMute}
                  className="flex items-center space-x-2 bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium py-2 px-4 rounded-lg transition-all"
                >
                  {isMuted ? (
                    <>
                      <VolumeX className="w-4 h-4" />
                      <span>Unmute</span>
                    </>
                  ) : (
                    <>
                      <Volume2 className="w-4 h-4" />
                      <span>Mute</span>
                    </>
                  )}
                </motion.button>

                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={disconnectFromVoiceAgent}
                  className="flex items-center space-x-2 bg-red-500 hover:bg-red-600 text-white font-medium py-2 px-4 rounded-lg transition-all"
                >
                  <PhoneOff className="w-4 h-4" />
                  <span>Disconnect</span>
                </motion.button>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LiveKitVoice;
