# 🤖# AI Customer Service Assistant

![Python](https://img.shields.io/badge/Python-3.9%2B-brightgreen.svg)
![React](https://img.shields.io/badge/React-18.2%2B-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0%2B-black.svg)
![AI Powered](https://img.shields.io/badge/AI-Powered-orange.svg)
## What This System Does

A complete customer service AI platform that:
- Understands customer intent across 8 major categories
- Provides intelligent, context-aware responses
- Supports both text and voice interactions
- Maintains conversation history and context
- Scales from development to production

## Key Features

### Frontend (React)
- **Modern UI**: Clean, responsive interface with Tailwind CSS
- **Real-time Chat**: Instant message processing and display
- **Voice Integration**: Record and send voice messages
- **Quick Actions**: Pre-defined buttons for common requests
- **Conversation Management**: History tracking and export

### Backend (Python/Flask)
- **Intent Classification**: 8 customer service categories
- **Sentiment Analysis**: Understands customer emotion and urgency
- **Voice Processing**: Speech-to-text and text-to-speech
- **LiveKit Voice Agent**: Real-time voice AI conversations
- **Conversation Memory**: Multi-turn dialogue support
- **RESTful API**: Complete API for all features

### AI Capabilities
- **Account Support**: Password resets, profile updates, account issues
- **Order Tracking**: Status updates, delivery information
- **Billing/Payment**: Refunds, payment issues, invoicing
- **Product Inquiry**: Specifications, availability, features
- **Returns/Exchanges**: Return policies, defective items
- **Technical Support**: Troubleshooting, error handling
- **Complaint Handling**: Escalation and resolution
- **General Information**: Business hours, contact details


## Quick Start Options

### Option 1: Full Stack with LiveKit Voice Agent (Recommended)
```bash
START_WITH_LIVEKIT.bat
```
Starts complete system with real-time voice AI. Requires LiveKit credentials in .env file.

### Option 2: Standard Mode (Text + Basic Voice)
```bash
START_APP.bat
```
Starts backend and React frontend. Works without LiveKit.

### Option 3: Backend Only
```bash
start_backend.bat
```
Starts Flask API server on port 5000.

### Option 4: Frontend Only
```bash
start_react.bat
```
Starts React development server on port 3000 (requires backend running).

## How to Run This Project

### Prerequisites
- Python 3.9 or newer
- Node.js 16 or newer
- Internet connection
- (Optional) OpenAI API key for LLM responses
- (Optional) LiveKit account for voice agent

### Easy Setup

1. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Frontend dependencies**
   ```bash
   cd frontend/react-app
   npm install
   cd ../..
   ```

3. **Configure environment (Optional)**
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key for better responses
   - Add LiveKit credentials for voice features

4. **Run the application**
   ```bash
   START_APP.bat
   ```

5. **Access the application**
   - Backend API: http://localhost:5000
   - React Frontend: http://localhost:3000

## 📁 Project Structure

```
ai-customer-service/
├── 📊 data/                    # Training data and configurations
│   ├── intents.json            # Intent classification patterns
│   ├── responses.json          # Response templates
│   └── medical_guidelines.json # Healthcare triage rules
├── 🧠 src/                    # Backend Python code
│   ├── main_assistant.py       # Main assistant orchestrator
│   ├── flask_api.py            # REST API endpoints
│   ├── database.py             # SQLite database layer
│   ├── dialogue_manager.py     # Conversation state management
│   └── ...                     # Other core modules
├── 🖥️ frontend/               # React web interface
│   └── react-app/              # React application
│       ├── src/                # React components
│       └── public/             # Static assets
├── 📋 requirements.txt         # Python dependencies
├── 🗄️ customer_service.db     # SQLite database (created on first run)
└── 📆 README.md               # This file
```

## 💬 How to Use

1. **Start the application** - Run `START_APP.bat`
2. **Open browser** - Navigate to http://localhost:3000
3. **Type a message** - Use the chat interface
4. **Quick actions** - Click preset buttons for common requests
5. **Voice input** - Click microphone icon to record voice messages
6. **Upload documents** - Add PDFs to knowledge base via sidebar
7. **View history** - Access past conversations in sidebar

### Example Conversations
- "I need help with my order"
- "Track my package"
- "I want to return an item"
- "What are your business hours?"
- "I have a billing question"


## 🎓 What I Learned Building This

This project helped me learn about:
- **Python Programming**: Using different libraries and modules
- **AI and Machine Learning**: How chatbots understand and respond to text
- **Web Development**: Building user interfaces with Streamlit
- **Software Structure**: Organizing code into different files and folders

## 🛠️ Technologies Used

### Core Technologies
- **Python 3.9+** - Main programming language
- **React 18** - Modern frontend framework
- **Flask** - Backend API server
- **LiveKit** - Real-time voice AI agent framework

### AI & Machine Learning
- **HuggingFace Transformers** - For AI language processing
- **OpenAI GPT** - Advanced language models
- **Deepgram/OpenAI Whisper** - Speech-to-text
- **ElevenLabs/OpenAI TTS** - Text-to-speech

### UI & Styling
- **Tailwind CSS** - Modern styling
- **Framer Motion** - Smooth animations
- **Lucide React** - Beautiful icons

## 📚 Next Steps

Ideas to make this project even better:
- Add more conversation topics
- Improve the bot's responses
- Add user authentication
- Create a mobile app version
- Connect to a real customer database

## 🎯 About This Project

This is a student learning project that demonstrates basic AI chatbot concepts. It's designed to be simple to understand and easy to modify for learning purposes.

---

*Built by a student learning AI and Python! 🎓*
