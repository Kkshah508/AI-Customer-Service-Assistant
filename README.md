# AI Customer Service Assistant - React Frontend

A professional, modern React frontend for the AI-powered customer service assistant with voice and text support.

## Features

- **Modern UI/UX**: Built with React, TailwindCSS, and Framer Motion
- **Real-time Chat**: Instant messaging with the AI assistant
- **Voice Support**: Voice recording and text-to-speech capabilities
- **Quick Actions**: Pre-defined message templates for common queries
- **System Monitoring**: Real-time system stats and status
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Smooth Animations**: Engaging user experience with motion effects

## Tech Stack

- **React 18**: Latest React features and hooks
- **TailwindCSS**: Utility-first CSS framework
- **Framer Motion**: Animation library
- **Zustand**: Lightweight state management
- **Axios**: HTTP client for API requests
- **Lucide React**: Beautiful icon library
- **React Hot Toast**: Elegant notifications

## Installation

1. Install dependencies:
```bash
cd frontend/react-app
npm install
```

2. Create environment file (optional):
```bash
cp .env.example .env
```

Edit `.env` to set your API URL:
```
REACT_APP_API_URL=http://localhost:5000
```

## Running the Application

### Development Mode

```bash
npm start
```

The app will open at [http://localhost:3000](http://localhost:3000)

### Production Build

```bash
npm run build
```

The optimized build will be in the `build/` directory.

## Backend API

The React frontend requires the Flask API backend to be running. Start the backend:

```bash
cd ../..
python src/flask_api.py
```

The API will run at [http://localhost:5000](http://localhost:5000)

## Project Structure

```
src/
├── components/          # React components
│   ├── Header.jsx      # App header with branding
│   ├── Sidebar.jsx     # Settings and system stats
│   ├── ChatInterface.jsx   # Main chat interface
│   ├── ChatMessage.jsx     # Message display component
│   ├── VoiceRecorder.jsx   # Voice recording component
│   └── QuickActions.jsx    # Quick action buttons
├── services/           # API services
│   └── api.js         # API integration
├── store/             # State management
│   └── useStore.js    # Zustand store
├── App.js             # Main app component
├── index.js           # Entry point
└── index.css          # Global styles
```

## Available Scripts

- `npm start` - Start development server
- `npm build` - Create production build
- `npm test` - Run tests
- `npm eject` - Eject from Create React App (irreversible)

## Configuration

### API Integration

The app connects to the Flask backend API. Configure the API URL in:
- Development: `.env.local` or proxy in `package.json`
- Production: Environment variables

### Voice Features

Voice recording requires:
- Microphone permissions
- HTTPS in production (or localhost)
- Backend voice processing support

## Deployment

### Deploy to Vercel/Netlify

1. Build the app: `npm run build`
2. Deploy the `build` folder
3. Set environment variable: `REACT_APP_API_URL=<your-api-url>`

### Docker Deployment

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
RUN npm install -g serve
CMD ["serve", "-s", "build", "-l", "3000"]
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Troubleshooting

### API Connection Issues

1. Ensure backend is running: `python src/flask_api.py`
2. Check CORS settings in Flask backend
3. Verify API URL in environment variables

### Voice Not Working

1. Grant microphone permissions
2. Use HTTPS or localhost
3. Check browser compatibility
4. Verify backend voice handler is initialized

## License

Part of the AI Customer Service Assistant project.
