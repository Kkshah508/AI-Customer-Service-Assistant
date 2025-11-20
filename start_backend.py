import sys
import os
import subprocess
import threading
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from src.flask_api import app

def start_livekit_agent():
    livekit_enabled = os.getenv('ENABLE_LIVEKIT_AGENT', 'false').lower() == 'true'
    
    if not livekit_enabled:
        print("\n[LiveKit] Disabled in .env - skipping agent startup")
        return
    
    required_vars = ['LIVEKIT_URL', 'LIVEKIT_API_KEY', 'LIVEKIT_API_SECRET', 'OPENAI_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"\n[LiveKit] Missing credentials: {', '.join(missing_vars)}")
        print("[LiveKit] Agent will not start. Configure these in .env to enable voice.")
        return
    
    print("\n[LiveKit] Starting voice agent in dev mode...")
    print("[LiveKit] Agent will connect to LiveKit Cloud")
    
    try:
        agent_process = subprocess.Popen(
            [sys.executable, 'livekit_agent.py', 'dev'],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        for line in agent_process.stdout:
            print(f"[LiveKit Agent] {line.rstrip()}")
            
    except Exception as e:
        print(f"\n[LiveKit] Failed to start agent: {e}")
        print("[LiveKit] Voice features will not be available")

if __name__ == '__main__':
    print("=" * 60)
    print("Starting AI Customer Service Backend API")
    print("=" * 60)
    
    if not os.path.exists('.env'):
        print("\n[WARNING] No .env file found")
        print("The system will work with basic features only.")
        print("For enhanced features, copy .env.example to .env and configure:")
        print("  - OPENAI_API_KEY for LLM responses")
        print("  - LIVEKIT credentials for voice features")
        print()
    else:
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key and len(openai_key) > 10:
            print("\n[OK] OpenAI API key detected - LLM responses enabled")
        else:
            print("\n[INFO] No OpenAI API key - using template responses")
        
        livekit_url = os.getenv('LIVEKIT_URL')
        if livekit_url:
            print("[OK] LiveKit configured - voice features available")
        else:
            print("[INFO] LiveKit not configured - voice features disabled")
        print()
    
    print("\nBackend API will be available at: http://localhost:5000")
    print("Health check endpoint: http://localhost:5000/health")
    
    livekit_thread = threading.Thread(target=start_livekit_agent, daemon=True)
    livekit_thread.start()
    
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
