# 📸 AK Lumora

> **AI-Powered Photography Studio Platform** — Advanced face recognition, real-time collaboration, and seamless cloud integration for modern photography studios.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3-4FC08D?style=flat-square&logo=vue.js)](https://vuejs.org/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

---

## ✨ Key Features

### 🤖 **AI-Powered Face Recognition**
- Advanced face detection and embeddings using **InsightFace**
- Intelligent face clustering and similarity matching
- Real-time face search across your photo library
- Vector-based similarity using **Qdrant** VectorDB
- Automatic model selection (buffalo_l/buffalo_s) based on system resources

### 🔐 **Authentication & Security**
- **Firebase Authentication** for secure user management
- Google OAuth integration
- Role-based access control
- JWT-based API tokens

### ☁️ **Cloud Integration**
- **Google Drive** seamless integration
- Automatic file uploads to cloud storage
- QR code generation for shared content
- Public file sharing with access control

### 📁 **Smart File Management**
- Automatic folder watching and monitoring
- Real-time file synchronization
- Batch upload capabilities
- File organization and tagging

### 🎬 **Live Presentation Mode**
- Real-time live streaming interface
- WebSocket-based instant updates
- Multi-client collaboration
- Dynamic dashboard with analytics

### 📊 **Studio Dashboard**
- Real-time statistics and analytics
- Upload tracking and management
- Performance monitoring
- Visual analytics with Chart.js

---

## 🏗️ Architecture

### Backend Stack
- **Framework**: FastAPI (async Python)
- **Database**: SQLAlchemy + SQLite/PostgreSQL
- **Real-time**: WebSocket support
- **AI/ML**: InsightFace, ONNX Runtime, OpenCV
- **Vector DB**: Qdrant
- **Cloud**: Firebase Admin SDK, Google APIs

### Frontend Stack
- **Framework**: Vue.js 3 + TypeScript
- **Build Tool**: Vite
- **State Management**: Pinia
- **HTTP Client**: Axios
- **Charts**: Chart.js + vue-chartjs
- **Animations**: GSAP
- **Authentication**: Firebase SDK
- **Code Generation**: QR Code library

---

## 📦 Project Structure

```
AK_Lumora/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application entry point
│   │   ├── config.py               # Configuration & environment variables
│   │   ├── database.py             # Database setup & ORM models
│   │   ├── websocket.py            # Real-time WebSocket manager
│   │   ├── models/                 # SQLAlchemy data models
│   │   │   ├── user.py
│   │   │   ├── folder.py
│   │   │   ├── upload.py
│   │   │   └── face.py
│   │   ├── routers/                # API endpoints
│   │   │   ├── auth.py            # Authentication endpoints
│   │   │   ├── drive.py           # Google Drive integration
│   │   │   ├── folders.py         # Folder management
│   │   │   ├── uploads.py         # File upload handling
│   │   │   └── face_search.py     # Face recognition API
│   │   ├── schemas/                # Pydantic request/response models
│   │   └── services/               # Business logic
│   │       ├── face_service.py    # Face detection engine
│   │       ├── face_clustering.py # Face clustering logic
│   │       ├── face_queue.py      # Async face processing queue
│   │       ├── vector_store.py    # Qdrant integration
│   │       ├── drive_service.py   # Google Drive operations
│   │       ├── file_monitor.py    # File system watcher
│   │       └── firebase_auth.py   # Firebase authentication
│   ├── requirements.txt             # Python dependencies
│   ├── .env                         # Environment variables (git-ignored)
│   └── qdrant_data/               # Local vector database storage
│
├── frontend/
│   ├── src/
│   │   ├── main.ts                # Vue app entry point
│   │   ├── App.vue                # Root component
│   │   ├── views/                 # Page components
│   │   │   ├── HomePage.vue       # Landing page
│   │   │   ├── LoginPage.vue      # Authentication
│   │   │   ├── DashboardView.vue  # Main dashboard
│   │   │   ├── LivePresentation.vue # Live mode
│   │   │   ├── StudioSetup.vue    # Configuration
│   │   │   ├── DriveConfig.vue    # Google Drive setup
│   │   │   └── OAuthCallback.vue  # OAuth redirect handler
│   │   ├── stores/                # Pinia state management
│   │   │   └── auth.js
│   │   ├── composables/           # Vue composition utilities
│   │   │   └── useFirebase.js
│   │   ├── router/                # Vue Router configuration
│   │   ├── utils/                 # Helper functions
│   │   │   └── api.js            # Axios configuration
│   │   └── assets/
│   │       └── styles/           # Global styles & animations
│   ├── package.json              # Node dependencies
│   ├── vite.config.js           # Vite configuration
│   ├── tsconfig.json            # TypeScript configuration
│   └── .env                      # Frontend environment variables (git-ignored)
│
└── README.md                      # This file
```

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+** with pip
- **Node.js 18+** with npm
- **Git** for version control

### Backend Setup

1. **Clone and navigate to backend**
   ```bash
   git clone https://github.com/abhishekpythoninmakes/AK_Lumora.git
   cd AK_Lumora/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Firebase, Google Drive, and other credentials
   ```

5. **Run backend server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   Backend runs at: `http://localhost:8000`
   API docs: `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend**
   ```bash
   cd AK_Lumora/frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Firebase and API configuration
   ```

4. **Run development server**
   ```bash
   npm run dev
   ```

   Frontend runs at: `http://localhost:5173`

---

## ⚙️ Configuration

### Environment Variables

#### Backend (`backend/.env`)
```env
# Core Settings
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite+aiosqlite:///./ak_lumora.db

# Firebase
FIREBASE_API_KEY=your-firebase-key
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-bucket.appspot.com

# Google Drive
GOOGLE_DRIVE_CLIENT_ID=your-client-id
GOOGLE_DRIVE_CLIENT_SECRET=your-client-secret
BACKEND_URL=http://localhost:8000

# Face Detection
FACE_SIMILARITY_THRESHOLD=0.45
FACE_CLUSTER_INTERVAL=50
FACE_MAX_WORKERS=0  # 0 = auto-detect
FACE_MODEL_PREFERENCE=auto  # auto | large | small

# Frontend CORS
FRONTEND_URL=http://localhost:5173
```

#### Frontend (`frontend/.env`)
```env
VITE_API_URL=http://localhost:8000
VITE_FIREBASE_API_KEY=your-firebase-key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-bucket.appspot.com
VITE_GOOGLE_DRIVE_CLIENT_ID=your-client-id
```

---

## 📚 API Endpoints

### Authentication (`/api/auth`)
- `POST /login` — User login with Firebase
- `POST /register` — New user registration
- `POST /logout` — User logout
- `GET /profile` — Get current user profile

### Folders (`/api/folders`)
- `GET /` — List watched folders
- `POST /` — Create new watched folder
- `DELETE /{id}` — Remove watched folder
- `POST /{id}/watch` — Start monitoring folder
- `POST /{id}/stop` — Stop monitoring folder

### Uploads (`/api/uploads`)
- `GET /` — List all uploads
- `POST /` — Upload new files
- `GET /stream/{id}` — Stream file preview
- `GET /{id}/details` — Get upload details
- `DELETE /{id}` — Delete upload

### Face Search (`/api/face-search`)
- `POST /search` — Search by face similarity
- `GET /clusters` — Get face clusters
- `GET /embeddings` — Get all face embeddings
- `POST /compare` — Compare two faces

### Google Drive (`/api/drive`)
- `GET /status` — Check Drive connection status
- `POST /authorize` — Initiate OAuth flow
- `POST /upload/{upload_id}` — Upload to Google Drive
- `GET /files` — List Drive files

### WebSocket (`/ws/live/{user_id}`)
- Real-time notifications for file uploads
- Live presentation updates
- Face detection results streaming

---

## 🔧 Development

### Project Commands

#### Backend
```bash
# Run with auto-reload
uvicorn app.main:app --reload

# Run with specific port
uvicorn app.main:app --port 8001

# Reset database
python clear_db.py

# Compare faces (utility)
python compare_faces.py
```

#### Frontend
```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type checking
npm run type-check
```

---

## 🔐 Security Features

- ✅ **Firebase Authentication** — Industry-standard auth
- ✅ **OAuth 2.0** — Secure Google Drive integration
- ✅ **JWT Tokens** — API authentication
- ✅ **CORS Protection** — Cross-origin request handling
- ✅ **Environment Secrets** — No hardcoded credentials
- ✅ **Input Validation** — Pydantic schema validation
- ✅ **Password Hashing** — bcrypt for password security

---

## 📊 Key Technologies

| Category | Technology | Purpose |
|----------|-----------|---------|
| **Backend Framework** | FastAPI | Modern async Python web framework |
| **Database** | SQLAlchemy | ORM with async support |
| **AI/ML** | InsightFace + ONNX | Face detection & recognition |
| **Vector DB** | Qdrant | Semantic search for faces |
| **Real-time** | WebSocket | Live updates & notifications |
| **Cloud** | Firebase + Google APIs | Auth & cloud storage |
| **Frontend** | Vue 3 + Vite | Modern reactive UI |
| **State** | Pinia | Vue state management |
| **HTTP** | Axios | API communication |

---

## 🐛 Troubleshooting

### Backend Issues

**"No module named 'app'"**
- Ensure you're running from the backend directory
- Try: `python -m uvicorn app.main:app --reload`

**Face detection model fails to load**
- Requires sufficient RAM (see config for thresholds)
- Try: `FACE_MODEL_PREFERENCE=small uvicorn app.main:app --reload`

**Database errors**
- Reset database: `python clear_db.py`
- Check DATABASE_URL in .env

### Frontend Issues

**"Cannot find module '@vueuse/core'"**
- Run: `npm install`
- Clear node_modules: `rm -rf node_modules && npm install`

**API calls failing**
- Check VITE_API_URL in .env
- Ensure backend is running on configured port
- Check browser console for CORS errors

---

## 📈 Performance Optimization

- **Async Operations** — All I/O operations are non-blocking
- **Vector Indexing** — Qdrant indexes for fast face search
- **Model Selection** — Auto-selects optimal face model
- **Connection Pooling** — Efficient database connections
- **WebSocket Caching** — Reduced redundant updates
- **Image Processing** — OpenCV for efficient image handling

---

## 📝 License

This project is licensed under the MIT License — see LICENSE file for details.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📞 Support

For issues, questions, or suggestions, please open an issue on [GitHub](https://github.com/abhishekpythoninmakes/AK_Lumora/issues).

---

## 🎯 Roadmap

- [ ] Machine learning model improvements
- [ ] Advanced analytics dashboard
- [ ] Mobile app (React Native)
- [ ] Batch processing optimization
- [ ] Advanced face clustering algorithms
- [ ] Multi-language support
- [ ] API rate limiting & quota management

---

## 👨‍💻 Author

**Abhishek** — AI & Full-Stack Developer

---

<div align="center">

**[Star us on GitHub](https://github.com/abhishekpythoninmakes/AK_Lumora) if you find this project helpful!** ⭐

Built with ❤️ for photography studios

</div>
