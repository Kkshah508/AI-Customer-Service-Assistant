# AI Customer Service Assistant - API Documentation

## API Overview

The backend API provides a complete REST interface for the AI Customer Service Assistant. It connects the React frontend with all AI-powered functionalities including intent classification, sentiment analysis, voice processing, and conversation management.

## Base URL

```
http://localhost:5000
```

## API Endpoints

### Health & Initialization

#### GET /health
Health check endpoint to verify API status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-03T08:00:00",
  "assistant_ready": true,
  "service": "AI Customer Service Assistant"
}
```

#### GET /api/initialize
Initialize the AI assistant and get its capabilities.

**Response:**
```json
{
  "status": "success",
  "message": "AI Customer Service Assistant initialized successfully",
  "capabilities": {
    "voice_enabled": true,
    "intent_classification": true,
    "sentiment_analysis": true,
    "conversation_memory": true
  }
}
```

### Message Processing

#### POST /api/process
Process a user message and get an AI-generated response.

**Request Body:**
```json
{
  "user_id": "user_123",
  "message": "I need help with my order",
  "patient_age": null
}
```

**Response:**
```json
{
  "status": "success",
  "message": "I'll be happy to help you check on your order. Do you have your order number handy?",
  "conversation_id": "conv_123",
  "metadata": {
    "intent": "order_status",
    "sentiment": "neutral",
    "confidence": 0.95,
    "urgency_level": "low"
  }
}
```

### Voice Processing

#### POST /api/voice/process
Convert audio input to text using speech recognition.

**Request:**
- Content-Type: `multipart/form-data`
- Body: Audio file (WAV format)

**Response:**
```json
{
  "status": "success",
  "text": "I need help with my account"
}
```

#### POST /api/voice/tts
Convert text to speech audio.

**Request Body:**
```json
{
  "text": "Hello! How can I help you today?"
}
```

**Response:**
- Content-Type: `audio/wav`
- Body: Audio binary data

### Conversation Management

#### GET /api/conversation/<user_id>
Retrieve conversation history for a specific user.

**Response:**
```json
{
  "status": "success",
  "conversation": [
    {
      "role": "user",
      "message": "I need help",
      "timestamp": "2025-10-03T08:00:00"
    },
    {
      "role": "assistant",
      "message": "I'm here to help",
      "timestamp": "2025-10-03T08:00:01"
    }
  ]
}
```

#### POST /api/reset
Reset conversation history for a user.

**Request Body:**
```json
{
  "user_id": "user_123"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Conversation reset successfully"
}
```

#### GET /api/export/<user_id>
Export complete conversation history.

**Response:**
```json
{
  "user_id": "user_123",
  "conversations": [...],
  "export_date": "2025-10-03T08:00:00"
}
```

### System Information

#### GET /api/stats
Get system statistics and usage metrics.

**Response:**
```json
{
  "active_sessions": 5,
  "total_conversations": 127,
  "emergency_responses": 0,
  "system_uptime_hours": 48.5
}
```

#### GET /api/intents
Get list of supported intents.

**Response:**
```json
{
  "status": "success",
  "intents": [
    "account_support",
    "order_status",
    "billing_payment",
    "product_inquiry",
    "returns_exchanges",
    "technical_support",
    "complaint",
    "general_inquiry"
  ]
}
```

#### GET /api/capabilities
Get detailed AI capabilities.

**Response:**
```json
{
  "status": "success",
  "capabilities": {
    "voice_input": true,
    "voice_output": true,
    "intent_classification": true,
    "sentiment_analysis": true,
    "conversation_memory": true,
    "multi_turn_dialogue": true,
    "context_awareness": true
  }
}
```

## Error Handling

All endpoints follow consistent error response format:

```json
{
  "status": "error",
  "message": "Error description",
  "error": "Detailed error information"
}
```

### Common Status Codes

- `200` - Success
- `400` - Bad Request (invalid input)
- `500` - Internal Server Error
- `503` - Service Unavailable (feature not available)

## Request Examples

### cURL Examples

**Process a message:**
```bash
curl -X POST http://localhost:5000/api/process \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user_123","message":"Where is my order?"}'
```

**Health check:**
```bash
curl http://localhost:5000/health
```

**Get capabilities:**
```bash
curl http://localhost:5000/api/capabilities
```

### JavaScript/React Examples

**Initialize assistant:**
```javascript
const response = await fetch('http://localhost:5000/api/initialize');
const data = await response.json();
console.log(data.capabilities);
```

**Send message:**
```javascript
const response = await fetch('http://localhost:5000/api/process', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_id: 'user_123',
    message: 'I need help'
  })
});
const data = await response.json();
```

**Process voice:**
```javascript
const formData = new FormData();
formData.append('audio', audioBlob, 'recording.wav');

const response = await fetch('http://localhost:5000/api/voice/process', {
  method: 'POST',
  body: formData
});
const data = await response.json();
```

## Supported Intents

The system understands and processes the following customer service intents:

- **account_support** - Account-related issues (login, password, profile)
- **order_status** - Order tracking and delivery information
- **billing_payment** - Payment issues, refunds, billing questions
- **product_inquiry** - Product information, specifications, availability
- **returns_exchanges** - Returns, exchanges, refund policies
- **technical_support** - Technical issues, troubleshooting
- **complaint** - Customer complaints and escalations
- **general_inquiry** - General questions about services

## Rate Limiting

Currently no rate limiting is enforced. For production deployment, implement appropriate rate limiting based on your requirements.

## CORS Configuration

CORS is enabled for all origins in development. For production, update the CORS configuration in `flask_api.py`:

```python
CORS(app, resources={r"/api/*": {"origins": "https://yourdomain.com"}})
```

## Authentication

Currently no authentication is required. For production:

1. Implement JWT authentication
2. Add API key validation
3. Use environment variables for secrets
4. Enable HTTPS

## Running the API

**Development:**
```bash
python start_backend.py
```

**Production (with Gunicorn):**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 src.flask_api:app
```

## Environment Variables

Create a `.env` file based on `.env.example`:

```env
FLASK_ENV=development
FLASK_DEBUG=True
API_PORT=5000
LOG_LEVEL=INFO
```

## Testing the API

**Quick test:**
```bash
curl http://localhost:5000/health
```

**Full test with Python:**
```python
import requests

response = requests.post('http://localhost:5000/api/process', json={
    'user_id': 'test_user',
    'message': 'Hello, I need help'
})
print(response.json())
```

## Integration with React Frontend

The React frontend connects automatically using the proxy configuration in `package.json`. All API calls are made through the `apiService` in `src/services/api.js`.

## Troubleshooting

**API not responding:**
- Check if backend is running: `curl http://localhost:5000/health`
- Verify port 5000 is not in use
- Check firewall settings

**CORS errors:**
- Verify CORS is enabled in `flask_api.py`
- Check the proxy setting in React `package.json`

**Voice features not working:**
- Ensure voice dependencies are installed
- Check if audio libraries are available
- Verify microphone permissions in browser
