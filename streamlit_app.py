"""
Streamlit Frontend for AI-Powered Customer Service Assistant

A professional interface for customer support and automated assistance.
"""

import streamlit as st
import sys
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import base64
import tempfile
try:
    from st_audiorec import st_audiorec
    AUDIO_AVAILABLE = True
except ImportError:
    try:
        from streamlit_audiorecorder import audiorecorder
        AUDIO_AVAILABLE = True
    except ImportError:
        AUDIO_AVAILABLE = False
        audiorecorder = None

# Add src directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.main_assistant import HealthcareAssistant
    from src.utils import validate_user_input, mask_sensitive_info, validate_age_input
except ImportError as e:
    st.error(f"Error importing healthcare assistant modules: {e}")
    st.stop()


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'assistant' not in st.session_state:
        with st.spinner('Initializing Customer Service Assistant...'):
            try:
                st.session_state.assistant = HealthcareAssistant()
                st.session_state.assistant_ready = True
            except Exception as e:
                st.error(f"Failed to initialize Customer Service Assistant: {e}")
                st.session_state.assistant_ready = False
                st.stop()
    
    if 'user_id' not in st.session_state:
        st.session_state.user_id = f"user_{int(time.time())}"
    
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    if 'current_session_id' not in st.session_state:
        st.session_state.current_session_id = None
    
    if 'emergency_mode' not in st.session_state:
        st.session_state.emergency_mode = False


def display_service_disclaimer():
    """Display service disclaimer."""
    st.sidebar.markdown("### ⚠️ Service Disclaimer")
    st.sidebar.warning(
        "**This AI assistant provides general information and support only.**\n\n"
        "**For urgent issues, please contact your support team directly.**\n\n"
        "Always verify important information with authorized representatives."
    )


def display_support_contacts():
    """Display support contact information."""
    st.sidebar.markdown("### 📞 Support Contacts")
    st.sidebar.info("**Priority Support: Contact your team lead**")
    st.sidebar.info(
        "**Support Channels:**\n"
        "• Email: support@company.com\n"
        "• Phone: 1-800-SUPPORT\n"
        "• Live Chat: Available 24/7"
    )


def display_system_stats():
    """Display system statistics in sidebar."""
    if st.session_state.assistant_ready:
        try:
            stats = st.session_state.assistant.get_system_stats()
            
            st.sidebar.markdown("### 📊 System Status")
            st.sidebar.success("System: Operational")
            st.sidebar.metric("Active Sessions", stats.get('active_sessions', 0))
            st.sidebar.metric("Total Conversations", stats.get('total_conversations', 0))
            st.sidebar.metric("Emergency Responses", stats.get('emergency_responses', 0))
            
            uptime = stats.get('system_uptime_hours', 0)
            st.sidebar.metric("System Uptime (hours)", f"{uptime:.1f}")
            
            
        except Exception as e:
            st.sidebar.error(f"Error loading system stats: {e}")


def format_message(message: Dict[str, Any], is_user: bool = True) -> None:
    """Format and display a chat message."""
    timestamp = message.get('timestamp', datetime.now().isoformat())
    content = message.get('message', '')
    
    # Parse timestamp
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        time_str = dt.strftime('%H:%M:%S')
    except:
        time_str = timestamp[:8] if len(timestamp) > 8 else timestamp
    
    if is_user:
        st.chat_message("user").write(f"**You** *({time_str})*\n\n{content}")
    else:
        # Check for priority or urgent messages
        metadata = message.get('metadata', {})
        urgency = metadata.get('urgency_level', 'low')
        
        if urgency == 'critical' or 'urgent' in content.lower():
            st.chat_message("assistant").error(f"**Customer Service Assistant** *({time_str})*\n\n{content}")
        elif urgency == 'high':
            st.chat_message("assistant").warning(f"**Customer Service Assistant** *({time_str})*\n\n{content}")
        else:
            st.chat_message("assistant").write(f"**Customer Service Assistant** *({time_str})*\n\n{content}")


def display_conversation_history():
    """Display the conversation history."""
    if st.session_state.conversation_history:
        for msg in st.session_state.conversation_history:
            if msg.get('role') == 'user':
                format_message(msg, is_user=True)
            else:
                format_message(msg, is_user=False)


def handle_user_input(user_input: str, patient_age: Optional[int] = None, is_voice: bool = False):
    """Process user input and generate response."""
    if not user_input.strip():
        return
    
    try:
        # Validate input
        if not validate_user_input(user_input):
            st.error("Please enter a valid message.")
            return
        
        # Show user message
        with st.chat_message("user"):
            if is_voice:
                st.write(f"🎤 {user_input}")
            else:
                st.write(user_input)
        
        # Add to conversation history
        st.session_state.conversation_history.append({
            "role": "user", 
            "message": user_input,
            "timestamp": datetime.now().isoformat(),
            "patient_age": patient_age,
            "is_voice": is_voice
        })
        
        # Process with assistant
        with st.spinner("🤖 Analyzing your message..."):
            response = st.session_state.assistant.process_message(
                user_id=st.session_state.user_id,
                message=user_input,
                patient_age=patient_age
            )
        
        # Display assistant response
        with st.chat_message("assistant"):
            bot_message = response.get('message', 'Sorry, I had trouble understanding that.')
            st.write(bot_message)
            
            # Add voice response if available and user used voice
            if is_voice and st.session_state.assistant_ready:
                if hasattr(st.session_state.assistant, 'voice_handler') and st.session_state.assistant.voice_handler:
                    with st.spinner("🔊 Generating voice response..."):
                        try:
                            voice_response = st.session_state.assistant.voice_handler.text_to_speech(bot_message)
                            if voice_response:
                                st.audio(voice_response, format="audio/wav")
                        except Exception as e:
                            st.info("Voice response not available")
        
        # Add assistant response to conversation history
        st.session_state.conversation_history.append({
            "role": "assistant",
            "message": response.get('message', ''),
            "timestamp": datetime.now().isoformat(),
            "metadata": response.get('metadata', {})
        })
        
        
        # Update current session ID
        st.session_state.current_session_id = response.get('conversation_id')
            
    except Exception as e:
        st.error(f"Error processing message: {e}")
        
        # Add error message to history
        error_msg = {
            'role': 'system',
            'message': f"System error: {str(e)}",
            'timestamp': datetime.now().isoformat()
        }
        st.session_state.conversation_history.append(error_msg)


def export_conversation():
    """Export conversation history."""
    if not st.session_state.conversation_history:
        st.warning("No conversation to export.")
        return
    
    try:
        export_data = st.session_state.assistant.export_conversation(st.session_state.user_id)
        
        # Format as JSON
        json_data = json.dumps(export_data, indent=2, ensure_ascii=False)
        
        # Create download
        st.download_button(
            label="📄 Download Conversation (JSON)",
            data=json_data,
            file_name=f"healthcare_conversation_{st.session_state.user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
        
        # Also create formatted text version
        from src.utils import format_conversation_export
        formatted_text = format_conversation_export(export_data)
        
        st.download_button(
            label="📝 Download Conversation (Text)",
            data=formatted_text,
            file_name=f"healthcare_conversation_{st.session_state.user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )
        
        st.success("Conversation export prepared for download.")
        
    except Exception as e:
        st.error(f"Error exporting conversation: {e}")


def reset_conversation():
    """Reset the conversation."""
    try:
        st.session_state.assistant.reset_conversation(st.session_state.user_id)
        st.session_state.conversation_history = []
        st.session_state.emergency_mode = False
        st.success("Conversation has been reset.")
        st.rerun()
    except Exception as e:
        st.error(f"Error resetting conversation: {e}")


def main():
    """Main Streamlit application."""
    
    # Page configuration
    st.set_page_config(
        page_title="AI Customer Service Assistant",
        page_icon="🤖",
        layout="centered"
    )
    
    # Initialize session state
    initialize_session_state()
    
    st.markdown("""
    <style>
    .main-header {
        background: #4CAF50;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        color: white;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main header
    st.markdown("""
    <div class="main-header">
        <h2>🤖 AI Customer Service Assistant</h2>
        <p>Intelligent Support & Automated Assistance</p>
    </div>
    """, unsafe_allow_html=True)
    
    
    # Simple sidebar
    with st.sidebar:
        st.markdown("## Settings")
        
        # Basic user info
        user_name = st.text_input("Your Name", placeholder="Enter your name")
        
        st.divider()
        
        # Simple controls
        if st.button("🔄 Clear Chat"):
            reset_conversation()
            st.rerun()
        
        st.divider()
        
        st.markdown("### About")
        st.info("🤖 **AI Assistant**\n\nIntelligent customer service assistant with voice and text support.")
    # Simple chat interface
    st.markdown("## 💬 Chat Interface")
    
    # Quick action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("👋 Say Hello"):
            st.session_state.quick_message = "Hello! How can you help me today?"
    
    with col2:
        if st.button("📞 Get Support"):
            st.session_state.quick_message = "I need customer support assistance."
    
    with col3:
        if st.button("❓ Ask Question"):
            st.session_state.quick_message = "I have a question about your services."
    
    # Display conversation history
    if st.session_state.conversation_history:
        st.markdown("#### Conversation History")
        display_conversation_history()
    else:
        # Welcome message
        st.info("""
        👋 **Welcome to Customer Service**
        
        I can help you with:
        • 📞 Account support and assistance
        • 📦 Order status and information
        • ❓ General questions and inquiries
        • 🗣️ Voice and text conversations
        
        Choose an option above or type your message below!
        """)
    
    # Voice input section
    if AUDIO_AVAILABLE:
        st.markdown("### 🎙️ Voice Chat")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            audio = audiorecorder("🎙️ Start Recording", "⏹️ Stop Recording", key="voice_input")
        
        with col2:
            if st.button("🔊 Test Voice", help="Test voice output"):
                if st.session_state.assistant_ready:
                    test_audio = st.session_state.assistant.voice_handler.text_to_speech("Hello! I'm your customer service assistant. How can I help you today?") if hasattr(st.session_state.assistant, 'voice_handler') and st.session_state.assistant.voice_handler else None
                    if test_audio:
                        st.audio(test_audio, format="audio/wav")
                    else:
                        st.info("Voice output not available")
        
        if len(audio) > 0:
            st.audio(audio.tobytes())
            
            with st.spinner("🎙️ Processing voice input..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                    tmp_file.write(audio.tobytes())
                    tmp_file_path = tmp_file.name
                
                try:
                    if st.session_state.assistant_ready and hasattr(st.session_state.assistant, 'voice_handler') and st.session_state.assistant.voice_handler:
                        text = st.session_state.assistant.voice_handler.process_audio_file(tmp_file_path)
                        if text:
                            st.success(f"🎙️ Recognized: {text}")
                            handle_user_input(text, None, is_voice=True)
                            st.rerun()
                        else:
                            st.error("Could not understand the audio. Please try again.")
                    else:
                        st.error("Voice processing not available")
                except Exception as e:
                    st.error(f"Voice processing error: {e}")
                finally:
                    if os.path.exists(tmp_file_path):
                        os.unlink(tmp_file_path)
    else:
        st.info("💡 Voice chat requires audio libraries. Install 'streamlit-audiorecorder' and 'SpeechRecognition' for voice functionality.")
    
    st.divider()
    
    # Chat input
    user_input = st.chat_input("Type your message here... (e.g., 'I need help with my order')")
    # Handle quick messages
    if hasattr(st.session_state, 'quick_message'):
        user_input = st.session_state.quick_message
        del st.session_state.quick_message
    
    # Process user input
    if user_input:
        handle_user_input(user_input, None)
        st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888; font-size: 0.9em;">
        <p>🤖 AI Customer Service Assistant | Powered by Advanced AI</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
