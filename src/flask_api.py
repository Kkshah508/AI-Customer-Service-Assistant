from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import sys
import tempfile
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import io
from dotenv import load_dotenv
from functools import wraps
import time
from collections import defaultdict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main_assistant import HealthcareAssistant
from src.utils import validate_user_input
from src.knowledge_base import KnowledgeBase
from src.cache_manager import CacheManager
from src.auth_manager import generate_token, verify_token, optional_token

load_dotenv()

app = Flask(__name__)
CORS(app)

if not os.path.exists('logs'):
    os.makedirs('logs')

file_handler = RotatingFileHandler(
    'logs/app.log',
    maxBytes=10485760,
    backupCount=10
)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)

error_handler = RotatingFileHandler(
    'logs/errors.log',
    maxBytes=10485760,
    backupCount=10
)
error_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
error_handler.setLevel(logging.ERROR)

app.logger.addHandler(file_handler)
app.logger.addHandler(error_handler)
app.logger.setLevel(logging.INFO)

logger = logging.getLogger(__name__)
logger.addHandler(file_handler)
logger.addHandler(error_handler)

rate_limit_store = defaultdict(list)
RATE_LIMIT_REQUESTS = 60
RATE_LIMIT_WINDOW = 60

assistant = None
knowledge_base = None
cache_manager = CacheManager(max_size=1000, ttl=300)

def rate_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        now = time.time()
        
        rate_limit_store[client_ip] = [
            req_time for req_time in rate_limit_store[client_ip]
            if now - req_time < RATE_LIMIT_WINDOW
        ]
        
        if len(rate_limit_store[client_ip]) >= RATE_LIMIT_REQUESTS:
            return jsonify({
                'status': 'error',
                'message': 'Rate limit exceeded. Please try again later.'
            }), 429
        
        rate_limit_store[client_ip].append(now)
        return f(*args, **kwargs)
    return decorated_function

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Resource not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f'Internal server error: {error}')
    return jsonify({
        'status': 'error',
        'message': 'Internal server error. Please try again later.'
    }), 500

@app.errorhandler(Exception)
def handle_exception(error):
    logger.error(f'Unhandled exception: {error}', exc_info=True)
    return jsonify({
        'status': 'error',
        'message': 'An unexpected error occurred'
    }), 500

def get_assistant():
    global assistant
    if assistant is None:
        assistant = HealthcareAssistant()
    return assistant

def get_knowledge_base():
    global knowledge_base
    if knowledge_base is None:
        knowledge_base = KnowledgeBase()
    return knowledge_base

def get_livekit_token(room_name: str, participant_identity: str) -> str:
    try:
        from livekit import api
        
        livekit_url = os.getenv('LIVEKIT_URL')
        livekit_api_key = os.getenv('LIVEKIT_API_KEY')
        livekit_api_secret = os.getenv('LIVEKIT_API_SECRET')
        
        if not all([livekit_url, livekit_api_key, livekit_api_secret]):
            raise ValueError("LiveKit credentials not configured")
        
        token = api.AccessToken(livekit_api_key, livekit_api_secret)
        token.with_identity(participant_identity)
        token.with_name(participant_identity)
        token.with_grants(api.VideoGrants(
            room_join=True,
            room=room_name,
            can_publish=True,
            can_subscribe=True,
            can_publish_data=True
        ))
        
        return token.to_jwt()
    except Exception as e:
        logger.error(f"Error generating LiveKit token: {e}")
        raise

@app.route('/api/initialize', methods=['GET'])
def initialize():
    try:
        assistant_instance = get_assistant()
        capabilities = {
            'voice_enabled': hasattr(assistant_instance, 'voice_handler') and assistant_instance.voice_handler is not None,
            'intent_classification': True,
            'sentiment_analysis': True,
            'conversation_memory': True
        }
        return jsonify({
            'status': 'success',
            'message': 'AI Customer Service Assistant initialized successfully',
            'capabilities': capabilities
        })
    except Exception as e:
        logger.error(f"Initialization error: {e}")
        return jsonify({
            'status': 'success',
            'message': 'Assistant initialized in limited mode',
            'capabilities': {
                'voice_enabled': False,
                'intent_classification': True,
                'sentiment_analysis': True,
                'conversation_memory': True
            }
        })

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.json
        user_id = data.get('user_id')
        user_name = data.get('user_name', '')
        
        if not user_id:
            return jsonify({'status': 'error', 'message': 'User ID required'}), 400
        
        token = generate_token(user_id, {'name': user_name})
        
        return jsonify({
            'status': 'success',
            'token': token,
            'user_id': user_id
        })
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'status': 'error', 'message': 'Login failed'}), 500

@app.route('/api/auth/verify', methods=['POST'])
def verify():
    try:
        data = request.json
        token = data.get('token')
        
        if not token:
            return jsonify({'status': 'error', 'message': 'Token required'}), 400
        
        result = verify_token(token)
        
        if result['valid']:
            return jsonify({
                'status': 'success',
                'valid': True,
                'user_id': result['payload']['user_id']
            })
        else:
            return jsonify({
                'status': 'error',
                'valid': False,
                'message': result['error']
            }), 401
    except Exception as e:
        logger.error(f"Verify error: {e}")
        return jsonify({'status': 'error', 'message': 'Verification failed'}), 500

@app.route('/api/process', methods=['POST'])
@rate_limit
@optional_token
def process_message():
    try:
        data = request.json
        user_id = data.get('user_id')
        message = data.get('message')
        patient_age = data.get('patient_age')

        if not user_id or not message:
            return jsonify({
                'status': 'error',
                'message': 'Missing required fields'
            }), 400

        validation_result = validate_user_input(message)
        if not validation_result.get('is_valid'):
            return jsonify({
                'status': 'error',
                'message': 'Invalid input'
            }), 400

        assistant_instance = get_assistant()
        response = assistant_instance.process_message(
            user_id=user_id,
            message=message,
            patient_age=patient_age
        )

        return jsonify({
            'status': 'success',
            'message': response.get('message', ''),
            'conversation_id': response.get('conversation_id'),
            'metadata': response.get('metadata', {})
        })

    except Exception as e:
        logger.error(f"Message processing error: {e}")
        return jsonify({
            'status': 'success',
            'message': 'I am having trouble with some services right now, but I can still help with basic questions.',
            'conversation_id': None,
            'metadata': { 'fallback': True }
        })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        cache_key = 'system_stats'
        cached_stats = cache_manager.get(cache_key)
        
        if cached_stats:
            return jsonify(cached_stats)
        
        assistant_instance = get_assistant()
        stats = assistant_instance.get_system_stats()
        
        cache_manager.set(cache_key, stats)
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({
            'active_sessions': 0,
            'total_conversations': 0,
            'emergency_responses': 0,
            'system_uptime_hours': 0
        })

@app.route('/api/export/<user_id>', methods=['GET'])
def export_conversation(user_id):
    try:
        assistant_instance = get_assistant()
        export_data = assistant_instance.export_conversation(user_id)
        return jsonify(export_data)
    except Exception as e:
        logger.error(f"Export error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/reset', methods=['POST'])
def reset_conversation():
    try:
        data = request.json
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({
                'status': 'error',
                'message': 'Missing user_id'
            }), 400

        assistant_instance = get_assistant()
        assistant_instance.reset_conversation(user_id)
        
        return jsonify({
            'status': 'success',
            'message': 'Conversation reset successfully'
        })
    except Exception as e:
        logger.error(f"Reset error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/voice/process', methods=['POST'])
@rate_limit
def process_voice():
    try:
        if 'audio' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No audio file provided'
            }), 400

        audio_file = request.files['audio']
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            audio_file.save(tmp_file.name)
            tmp_file_path = tmp_file.name

        try:
            assistant_instance = get_assistant()
            if hasattr(assistant_instance, 'voice_handler') and assistant_instance.voice_handler:
                text = assistant_instance.voice_handler.process_audio_file(tmp_file_path)
                
                if text:
                    return jsonify({
                        'status': 'success',
                        'text': text
                    })
                else:
                    return jsonify({
                        'status': 'error',
                        'message': 'Could not understand audio'
                    }), 400
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Voice processing not available'
                }), 503
        finally:
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)

    except Exception as e:
        logger.error(f"Voice processing error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/voice/tts', methods=['POST'])
@rate_limit
def text_to_speech():
    try:
        data = request.json
        text = data.get('text')

        if not text:
            return jsonify({
                'status': 'error',
                'message': 'No text provided'
            }), 400

        assistant_instance = get_assistant()
        vh = getattr(assistant_instance, 'voice_handler', None)
        if not vh:
            try:
                from src.voice_handler import VoiceHandler
                assistant_instance.voice_handler = VoiceHandler()
                vh = assistant_instance.voice_handler
            except Exception:
                vh = None
        if vh:
            audio_data = vh.text_to_speech(text)
            if audio_data:
                return send_file(
                    io.BytesIO(audio_data),
                    mimetype='audio/wav',
                    as_attachment=False
                )
            return jsonify({
                'status': 'error',
                'message': 'TTS generation failed'
            }), 500
        return jsonify({
            'status': 'error',
            'message': 'TTS not available'
        }), 503

    except Exception as e:
        logger.error(f"TTS error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/conversation/<user_id>', methods=['GET'])
def get_conversation_history(user_id):
    try:
        assistant_instance = get_assistant()
        if hasattr(assistant_instance, 'dialogue_manager'):
            conversation = assistant_instance.dialogue_manager.get_conversation_history(user_id)
            return jsonify({
                'status': 'success',
                'conversation': conversation
            })
        return jsonify({
            'status': 'success',
            'conversation': []
        })
    except Exception as e:
        logger.error(f"Get conversation error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/intents', methods=['GET'])
def get_available_intents():
    try:
        assistant_instance = get_assistant()
        if hasattr(assistant_instance, 'intent_classifier'):
            intents = list(assistant_instance.intent_classifier.training_data.keys())
            return jsonify({
                'status': 'success',
                'intents': intents
            })
        return jsonify({
            'status': 'success',
            'intents': []
        })
    except Exception as e:
        logger.error(f"Get intents error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/capabilities', methods=['GET'])
def get_capabilities():
    try:
        assistant_instance = get_assistant()
        capabilities = {
            'voice_input': hasattr(assistant_instance, 'voice_handler') and assistant_instance.voice_handler is not None,
            'voice_output': hasattr(assistant_instance, 'voice_handler') and assistant_instance.voice_handler is not None,
            'intent_classification': hasattr(assistant_instance, 'intent_classifier'),
            'sentiment_analysis': hasattr(assistant_instance, 'sentiment_analyzer'),
            'conversation_memory': hasattr(assistant_instance, 'dialogue_manager'),
            'multi_turn_dialogue': True,
            'context_awareness': True
        }
        return jsonify({
            'status': 'success',
            'capabilities': capabilities
        })
    except Exception as e:
        logger.error(f"Get capabilities error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/livekit/token', methods=['POST'])
def generate_livekit_token():
    try:
        data = request.json
        room_name = data.get('room_name')
        participant_identity = data.get('participant_identity')
        
        if not room_name or not participant_identity:
            return jsonify({
                'status': 'error',
                'message': 'Missing room_name or participant_identity'
            }), 400
        
        livekit_url = os.getenv('LIVEKIT_URL')
        if not livekit_url:
            return jsonify({
                'status': 'error',
                'message': 'LiveKit not configured'
            }), 503
        
        token = get_livekit_token(room_name, participant_identity)
        
        return jsonify({
            'status': 'success',
            'token': token,
            'url': livekit_url,
            'room_name': room_name
        })
        
    except Exception as e:
        logger.error(f"Error generating LiveKit token: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/livekit/room/create', methods=['POST'])
def create_livekit_room():
    try:
        data = request.json
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({
                'status': 'error',
                'message': 'Missing user_id'
            }), 400
        
        room_prefix = os.getenv('LIVEKIT_ROOM_PREFIX', 'customer-service')
        room_name = f"{room_prefix}-{user_id}"
        
        livekit_url = os.getenv('LIVEKIT_URL')
        if not livekit_url:
            return jsonify({
                'status': 'error',
                'message': 'LiveKit not configured'
            }), 503
        
        token = get_livekit_token(room_name, user_id)
        
        return jsonify({
            'status': 'success',
            'room_name': room_name,
            'token': token,
            'url': livekit_url
        })
        
    except Exception as e:
        logger.error(f"Error creating LiveKit room: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/livekit/status', methods=['GET'])
def livekit_status():
    try:
        livekit_enabled = os.getenv('ENABLE_LIVEKIT_AGENT', 'false').lower() == 'true'
        livekit_url = os.getenv('LIVEKIT_URL')
        livekit_configured = all([
            livekit_url,
            os.getenv('LIVEKIT_API_KEY'),
            os.getenv('LIVEKIT_API_SECRET')
        ])
        
        return jsonify({
            'status': 'success',
            'livekit_enabled': livekit_enabled,
            'livekit_configured': livekit_configured,
            'livekit_url': livekit_url if livekit_configured else None
        })
    except Exception as e:
        logger.error(f"Error checking LiveKit status: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/knowledge/documents', methods=['GET'])
def get_knowledge_documents():
    try:
        kb = get_knowledge_base()
        documents = kb.get_all_documents()
        return jsonify({
            'status': 'success',
            'documents': documents
        })
    except Exception as e:
        logger.error(f"Error getting documents: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'documents': []
        }), 500

@app.route('/api/knowledge/upload', methods=['POST'])
@rate_limit
def upload_knowledge_document():
    try:
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No file provided'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'No file selected'
            }), 400
        
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'knowledge_storage', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, file.filename)
        file.save(file_path)
        
        kb = get_knowledge_base()
        result = kb.process_document(file_path, file.filename)
        
        return jsonify({
            'status': 'success',
            'document': result
        })
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/knowledge/documents/<doc_id>', methods=['DELETE'])
def delete_knowledge_document(doc_id):
    try:
        kb = get_knowledge_base()
        success = kb.delete_document(doc_id)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Document deleted'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Document not found'
            }), 404
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/health', methods=['GET'])
@app.route('/', methods=['GET'])
def health_check():
    try:
        assistant_instance = get_assistant()
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'assistant_ready': assistant_instance is not None,
            'service': 'AI Customer Service Assistant'
        })
    except:
        return jsonify({
            'status': 'degraded',
            'timestamp': datetime.now().isoformat(),
            'assistant_ready': False
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
