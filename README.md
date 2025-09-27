# 🤖 AI Customer Service Assistant - Student Project

A basic AI-powered customer service chatbot built as a learning project. This simple assistant can have conversations and help with basic customer support questions.

![Python](https://img.shields.io/badge/Python-3.9%2B-brightgreen.svg)
![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-red.svg)
![Student Project](https://img.shields.io/badge/Level-Student%20Project-yellow.svg)
## 🎯 What This Project Does

This is a simple AI chatbot that can:
- 💬 Have basic conversations with users
- 🤖 Understand simple questions and provide helpful responses
- 📞 Help with basic customer service inquiries
- 🔊 Support voice input (when audio libraries are installed)

## ✨ Features

### Basic Capabilities
- **Simple Chat Interface**: Clean and easy-to-use chat interface built with Streamlit
- **Intent Understanding**: Can understand what users are asking for
- **Conversation Memory**: Remembers what you talked about during the chat session
- **Voice Support**: Optional voice input feature
- **User-Friendly**: Simple design perfect for learning and demonstrations

### What You Can Ask About
- General questions and conversation
- Basic customer support topics
- Simple information requests
- Help with common issues
- Account-related questions


## 🚀 How to Run This Project

### What You Need
- Python 3.9 or higher
- Basic understanding of Python
- Internet connection

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

- **Python** - Main programming language
- **Streamlit** - For creating the web interface
- **HuggingFace Transformers** - For AI language processing
- **JSON** - For storing conversation data

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
