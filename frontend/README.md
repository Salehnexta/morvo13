# Morvo13 Frontend

A simple, beautiful frontend interface for the Morvo13 AI Marketing Assistant platform.

## 🚀 Quick Start

### Option 1: Using Python HTTP Server (Recommended)
```bash
# From the project root
cd frontend
python -m http.server 3001
```

### Option 2: Using the Custom Server Script
```bash
# From the project root
python start_frontend.py
```

### Option 3: Direct File Access
You can also open `frontend/index.html` directly in your browser, but some features may not work due to CORS restrictions.

## 🌐 Access

- **Frontend URL**: http://localhost:3001
- **Backend API**: http://localhost:8000

## ✨ Features

### 🎯 Real-time System Status
- Live connection to FastAPI backend
- System health monitoring
- Agent status display
- WebSocket connection count

### 🤖 AI Agent Dashboard
Displays all 5 active AI agents:
- 🧠 **محلل استراتيجي متقدم** (Strategic Analyst)
- 👁️ **مراقب وسائل التواصل** (Social Media Monitor)
- ⚡ **محسن الحملات** (Campaign Optimizer)
- ✍️ **استراتيجي المحتوى** (Content Strategist)
- 📊 **محلل البيانات** (Data Analyst)

### 💬 Chat Interface
- Direct communication with AI agents
- Real-time message processing
- Error handling and loading states
- Enter key support for sending messages

### 🔗 Quick Actions
- **Health Check**: Direct link to `/health` endpoint
- **API Docs**: Access to FastAPI documentation
- **Protocols**: View protocol status
- **A2A Network**: Agent-to-agent network status

## 🎨 Design Features

- **Modern UI**: Clean, gradient-based design
- **Responsive**: Works on desktop and mobile
- **Animations**: Smooth hover effects and loading states
- **Status Indicators**: Real-time visual feedback
- **CORS Enabled**: Seamless backend communication

## 🛠️ Technical Details

### Frontend Stack
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with gradients and animations
- **Vanilla JavaScript**: No frameworks, pure JS
- **Fetch API**: For backend communication

### Backend Integration
- Connects to FastAPI backend on port 8000
- Real-time health monitoring
- RESTful API communication
- Error handling for offline scenarios

## 📱 Usage

1. **Start Backend**: Make sure your FastAPI server is running on port 8000
2. **Start Frontend**: Use one of the methods above
3. **Open Browser**: Navigate to http://localhost:3001
4. **Explore**: 
   - Check system status
   - View active agents
   - Try the chat interface
   - Use quick action buttons

## 🔧 Customization

### Changing the Backend URL
Edit the `API_BASE` constant in `index.html`:
```javascript
const API_BASE = 'http://localhost:8000';  // Change this if needed
```

### Styling
All styles are contained in the `<style>` section of `index.html`. You can easily customize:
- Colors and gradients
- Layout and spacing
- Animations and transitions
- Typography

### Adding Features
The JavaScript code is modular and easy to extend:
- Add new API endpoints
- Create additional UI components
- Implement new chat features
- Add more monitoring capabilities

## 🚨 Troubleshooting

### Frontend Won't Load
- Check if port 3001 is available
- Try a different port: `python -m http.server 3002`
- Ensure you're in the `frontend` directory

### Can't Connect to Backend
- Verify FastAPI server is running on port 8000
- Check the browser console for CORS errors
- Ensure both servers are on the same network

### Chat Not Working
- The chat feature requires the `/api/v1/chat` endpoint to be implemented
- Check browser console for API errors
- Verify the request format matches your backend expectations

## 📝 Notes

- This is a development frontend - for production, consider using a proper web server
- CORS is enabled for development - configure properly for production
- The interface automatically detects if the backend is offline
- All agent names support Arabic text for bilingual display

## 🎯 Next Steps

Consider enhancing with:
- User authentication
- Chat history persistence
- File upload capabilities
- Real-time WebSocket chat
- Advanced analytics dashboard
- Mobile app version 