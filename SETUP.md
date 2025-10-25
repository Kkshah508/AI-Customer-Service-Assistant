# React Frontend Setup Guide

## Quick Start

### 1. Install Dependencies

```bash
cd frontend/react-app
npm install
```

### 2. Start Backend API

Open a new terminal:

```bash
cd ../..
python src/flask_api.py
```

Backend will run at: http://localhost:5000

### 3. Start React App

In the react-app directory:

```bash
npm start
```

Frontend will open at: http://localhost:3000

## Detailed Setup

### Prerequisites

- Node.js 16+ and npm
- Python 3.8+
- All Python dependencies installed

### Backend Setup

1. Install Python dependencies:
```bash
pip install flask flask-cors
```

2. Verify backend dependencies are installed:
```bash
pip install -r requirements.txt
```

3. Start Flask API:
```bash
python src/flask_api.py
```

### Frontend Setup

1. Navigate to React app:
```bash
cd frontend/react-app
```

2. Install Node dependencies:
```bash
npm install
```

3. (Optional) Create environment file:
```bash
echo "REACT_APP_API_URL=http://localhost:5000" > .env.local
```

4. Start development server:
```bash
npm start
```

## Testing the Application

1. Open browser to http://localhost:3000
2. Try quick actions: "Say Hello", "Get Support", "Ask Question"
3. Type a message in the chat input
4. Test voice recording (requires microphone permission)
5. Test voice output with "Test Voice" button

## Production Build

### Build React App

```bash
npm run build
```

### Serve Production Build

```bash
npm install -g serve
serve -s build -l 3000
```

### Deploy Backend

For production, use a production WSGI server:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 src.flask_api:app
```

## Troubleshooting

### Port Already in Use

If port 3000 or 5000 is in use:

**React (port 3000):**
- Set PORT environment variable: `PORT=3001 npm start`

**Flask (port 5000):**
- Modify flask_api.py: `app.run(port=5001)`
- Update .env.local: `REACT_APP_API_URL=http://localhost:5001`

### CORS Errors

Ensure Flask-CORS is installed and configured in flask_api.py

### Voice Not Working

1. Grant microphone permissions in browser
2. Use HTTPS or localhost only
3. Check browser console for errors
4. Verify voice_handler is initialized in backend

### API Connection Failed

1. Verify backend is running
2. Check API URL in .env.local
3. Ensure no firewall blocking ports
4. Check browser network tab for errors

## Environment Variables

### Development (.env.local)
```
REACT_APP_API_URL=http://localhost:5000
```

### Production (.env.production)
```
REACT_APP_API_URL=https://your-api-domain.com
```

## Available Features

### Chat Interface
- Real-time messaging
- Message history
- Typing indicators
- Urgency level indicators

### Voice Features
- Voice recording
- Speech-to-text
- Text-to-speech
- Voice response playback

### Quick Actions
- Pre-defined message templates
- One-click common queries
- Fast interaction

### System Monitoring
- Active sessions count
- Total conversations
- Emergency responses
- System uptime

### Settings
- User name customization
- Clear chat history
- System status display

## Development Tips

### Hot Reload

React auto-reloads on file changes. Flask requires restart unless using:
```bash
FLASK_ENV=development python src/flask_api.py
```

### Debug Mode

Enable React DevTools and check console for errors.

For Flask debugging, check terminal output.

### API Testing

Use tools like Postman or curl to test API endpoints:

```bash
curl http://localhost:5000/health
curl -X POST http://localhost:5000/api/initialize
```

## Next Steps

1. Customize branding and colors in tailwind.config.js
2. Add authentication if needed
3. Implement conversation export/download
4. Add more quick action templates
5. Enhance error handling
6. Add loading states
7. Implement retry logic
