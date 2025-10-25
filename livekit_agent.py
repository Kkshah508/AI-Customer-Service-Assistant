import asyncio
import logging
import os
from typing import Dict, Any
from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, JobContext
from livekit.plugins import noise_cancellation, silero, openai
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from src.main_assistant import HealthcareAssistant
from src.intent_classifier import IntentClassifier
from src.sentiment_analyzer import SentimentAnalyzer

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CustomerServiceAgent(Agent):
    def __init__(self, healthcare_assistant: HealthcareAssistant) -> None:
        super().__init__(
            instructions="""You are a professional and empathetic AI customer service assistant for a healthcare organization.

Your key responsibilities:
- Provide accurate information about symptoms, medical conditions, and healthcare services
- Assess symptom urgency and recommend appropriate care levels
- Maintain a compassionate, patient-centered approach
- Ask clarifying questions when needed to provide better assistance
- Escalate emergency situations immediately
- Respect patient privacy and handle sensitive information appropriately

Communication style:
- Be warm, understanding, and professional
- Use clear, simple language avoiding medical jargon when possible
- Keep responses concise and to the point
- Show empathy for patient concerns
- Ask one question at a time to avoid overwhelming the patient

Important:
- For emergencies (chest pain, severe bleeding, difficulty breathing, loss of consciousness), immediately direct to call 911
- For urgent symptoms, recommend visiting an emergency room or urgent care
- For routine concerns, suggest scheduling an appointment with their healthcare provider
- Never diagnose or prescribe medication
- Always prioritize patient safety"""
        )
        self.healthcare_assistant = healthcare_assistant
        self.user_sessions: Dict[str, Dict[str, Any]] = {}
    
    async def on_message(self, message: str, participant_id: str) -> str:
        try:
            logger.info(f"Processing message from {participant_id}: {message[:50]}...")
            
            if participant_id not in self.user_sessions:
                self.user_sessions[participant_id] = {
                    'user_id': participant_id,
                    'message_count': 0
                }
            
            session = self.user_sessions[participant_id]
            session['message_count'] += 1
            
            response = self.healthcare_assistant.process_message(
                user_id=participant_id,
                message=message,
                patient_age=None
            )
            
            response_text = response.get('message', '')
            
            if response.get('urgency_level') == 'critical':
                logger.warning(f"CRITICAL urgency detected for {participant_id}")
            
            logger.info(f"Response generated for {participant_id}: {response_text[:50]}...")
            
            return response_text
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return "I apologize, but I'm experiencing technical difficulties. For urgent medical needs, please call 911 or contact your healthcare provider directly."


async def entrypoint(ctx: JobContext):
    try:
        await ctx.connect()
        logger.info(f"Agent connected to room: {ctx.room.name}")
        
        healthcare_assistant = HealthcareAssistant()
        logger.info("Healthcare Assistant initialized")
        
        stt_provider = os.getenv('STT_PROVIDER', 'deepgram').lower()
        tts_provider = os.getenv('TTS_PROVIDER', 'openai').lower()
        
        if stt_provider == 'deepgram':
            from livekit.plugins import deepgram
            stt = deepgram.STT(model="nova-3")
        else:
            stt = "openai/whisper-1"
        
        if tts_provider == 'openai':
            tts = openai.TTS(voice="alloy")
        elif tts_provider == 'elevenlabs':
            try:
                from livekit.plugins import elevenlabs
                voice_id = os.getenv('ELEVENLABS_VOICE_ID', 'EXAVITQu4vr4xnSDxMaL')
                tts = elevenlabs.TTS(voice=voice_id)
            except ImportError:
                logger.warning("ElevenLabs not available, falling back to OpenAI TTS")
                tts = openai.TTS(voice="alloy")
        else:
            tts = openai.TTS(voice="alloy")
        
        session = AgentSession(
            stt=stt,
            llm="openai/gpt-4o-mini",
            tts=tts,
            vad=silero.VAD.load(),
            turn_detection=MultilingualModel(),
        )
        
        agent = CustomerServiceAgent(healthcare_assistant)
        
        await session.start(
            room=ctx.room,
            agent=agent,
            room_input_options=RoomInputOptions(
                noise_cancellation=noise_cancellation.BVC(),
            ),
        )
        
        logger.info("LiveKit Agent session started")
        
        await session.generate_reply(
            instructions="Greet the user warmly and introduce yourself as their AI healthcare customer service assistant. Ask how you can help them today."
        )
        
        logger.info("Initial greeting generated")
        
    except Exception as e:
        logger.error(f"Error in agent entrypoint: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    logger.info("Starting LiveKit Healthcare Customer Service Agent...")
    
    required_env_vars = ['LIVEKIT_URL', 'LIVEKIT_API_KEY', 'LIVEKIT_API_SECRET', 'OPENAI_API_KEY']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please configure these in your .env file")
        exit(1)
    
    logger.info("All required environment variables present")
    logger.info(f"LiveKit URL: {os.getenv('LIVEKIT_URL')}")
    
    agents.cli.run_app(
        agents.WorkerOptions(
            entrypoint_fnc=entrypoint
        )
    )
