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
This starts the complete system with real-time voice AI capabilities.
See `LIVEKIT_SETUP.txt` for LiveKit configuration instructions.

### Option 2: Standard Mode (Text + Basic Voice)
```bash
START_APP.bat
```
This starts the backend and frontend without LiveKit voice agent.

### Option 3: Backend Only
```bash
start_backend.bat
```

### Option 4: Frontend Only
```bash
start_react.bat
```

## How to Run This Project
- Basic understanding of Python
- Internet connection
- (Optional) LiveKit Cloud account for voice agent

### Easy Setup

1. **Download the project files**
   - Download or clone this repository to your computer

2. **Install Python libraries**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the chatbot**
   ```bash
   streamlit run frontend/streamlit_app.py
   ```

4. **Open in browser**
   - Your web browser will open automatically
   - If not, go to `http://localhost:8501`

## 📁 Project Files

```
ai-customer-service/
├── 📊 data/                    # Bot training data
│   ├── intents.json            # What the bot can understand
│   └── responses.json          # How the bot responds
├── 🧠 src/                    # Main bot code
│   ├── main_assistant.py       # Main bot logic
│   └── (other Python files)    # Supporting functions
├── 🖥️ frontend/               # Web interface
│   └── streamlit_app.py        # The web app you see
├── 📋 requirements.txt         # List of needed Python libraries
└── 📆 README.md               # This file
```

## 💬 How to Use

1. **Start the app** - Run the command above
2. **Open your browser** - Go to the web address shown
3. **Type a message** - Ask the bot anything!
4. **Try the quick buttons** - Click "Say Hello" or "Ask Question"
5. **Have a conversation** - The bot remembers what you talked about

### Example Conversations
- "Hello, how are you?"
- "I need help with my account"
- "What can you do?"
- "Tell me a joke"


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
