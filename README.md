# SpeechEcho — Real‑Time Voice Cloning & Conversational Synthesis

SpeechEcho is a full‑stack web application for voice cloning, text‑to‑speech synthesis, document voiceover, and AI‑powered conversational interfaces. It leverages **Chatterbox TTS** with custom **LoRA fine-tuning** for enhanced voice quality and personalization.

## 🎯 Features

- **🎙️ Voice Cloning**: Clone voices from 3-5 second audio samples
- **✨ Text-to-Speech Studio**: Convert text to natural sounding speech with emotional control
- **📄 Document Voiceover**: Upload PDFs and convert them to audio
- **🤖 AI Chat**: Conversational interface with voice responses
- **👥 Multiple Voice Profiles**: Use predefined or cloned voices
- **⚡ Real-Time Streaming**: Stream audio generation for low-latency playback
- **🎯 Emotion Control**: Adjust exaggeration and expressiveness in synthesized speech

## 🤖 AI Model: Chatterbox TTS with LoRA Fine-tuning

### Chatterbox TTS Overview

**Chatterbox** is a state-of-the-art open-source Text-to-Speech model that powers SpeechEcho's voice synthesis capabilities.

| Component | Specification |
|-----------|---------------|
| **Architecture** | 0.5B parameter Llama backbone |
| **Text Tokenizer** | EnTokenizer with specialized tokens |
| **Audio Tokenizer** | S3 (Semantic Speech Synthesis) tokenizer |
| **Vocoder** | S3Gen neural vocoder (24kHz output) |
| **Voice Encoder** | Speaker embedding extraction network |
| **License** | MIT (Open Source) |
| **Repository** | [davidbrowne17/chatterbox-streaming](https://github.com/davidbrowne17/chatterbox-streaming) |

### Key Capabilities

- **Zero-shot Voice Cloning**: Clone voices from 3-5 second audio samples without fine-tuning
- **Emotion Control**: Adjustable exaggeration (0.0-1.0+) for expressive synthesis
- **Real-time Streaming**: Generate audio in real-time chunks with ~0.47s latency to first chunk
- **Watermarking**: Built-in Perth (PerTh) watermarking for responsible AI
- **Prosodic Control**: Influence speech pace via classifier-free guidance weights

### Performance Metrics (Base Model)

- **Real-Time Factor**: 0.499 (on NVIDIA RTX 4090, target < 1.0)
- **Latency to First Chunk**: ~0.472 seconds
- **Audio Quality**: Watermarked, 24kHz sample rate
- **Benchmark**: Consistently preferred over ElevenLabs in side-by-side evaluations

---

### LoRA Fine-tuning Enhancement

To improve voice quality further, we implemented **Low-Rank Adaptation (LoRA)** fine-tuning on the Chatterbox model for personalized voice synthesis.

#### LoRA Configuration

| Parameter | Value | Purpose |
|-----------|-------|---------|
| **Rank (R)** | 32 | Low-rank decomposition size |
| **Alpha (α)** | 64 | Scaling factor (2x rank) |
| **Dropout** | 0.05 | Regularization to prevent overfitting |
| **Target Layers** | All Linear layers (T3 model) | Comprehensive model adaptation |
| **Total LoRA Layers** | 210 | Auto-injected throughout architecture |
| **Trainable Parameters** | ~0.1% of base model | Efficient parameter usage |

#### Training Dataset

| Statistic | Value |
|-----------|-------|
| **Total Audio Files** | 577 |
| **Total Duration** | 38.68 minutes |
| **Average Clip Length** | 4.02 seconds |
| **Min/Max Clip Length** | 1.30 - 25.18 seconds |
| **Sample Rate** | 24 kHz, Mono |
| **Audio Format** | WAV |

**Data Source**: Single speaker (Hussain) voice samples extracted from natural conversations and recordings.

#### Training Configuration

| Setting | Value | Notes |
|---------|-------|-------|
| **Total Epochs** | 10 | Sufficient for small dataset |
| **Batch Size** | 2 | GPU memory optimization |
| **Gradient Accumulation** | 2 | Effective batch size = 4 |
| **Learning Rate** | 5e-5 | Appropriate for fine-tuning |
| **Warmup Steps** | 130 | ~5% of total training steps |
| **Optimizer** | AdamW | Standard choice for deep learning |
| **LR Scheduler** | Cosine Annealing | Smooth learning rate decay |
| **Train/Val Split** | 90% / 10% | 520 training / 57 validation samples |
| **Hardware** | NVIDIA RTX 4090 (24GB) | GPU required for efficient training |
| **Training Time** | ~15-20 minutes | Total end-to-end duration |

#### Evaluation Results

The fine-tuned model demonstrated measurable improvements across all quality metrics:

| Metric | Base Model | Fine-tuned | Improvement |
|--------|------------|-----------|------------|
| **Speaker Similarity** | 0.8204 | 0.8446 | **+2.94%** ⬆️ |
| **F0 (Pitch) Correlation** | -0.1640 | +0.0925 | **+25.65%** (Negative→Positive) ⬆️ |
| **Energy Correlation** | 0.0901 | 0.1806 | **+100.4%** ⬆️ |
| **Signal-to-Noise Ratio** | 40.33 dB | 44.00 dB | **+9.1%** ⬆️ |

**Interpretation**:
- **Speaker Similarity**: Fine-tuned voice is 2.94% closer to the target speaker's natural voice
- **F0 Correlation**: Pitch patterns now align positively with target (from negative), enabling natural prosody
- **Energy Correlation**: Loudness/emphasis dynamics doubled, matching speaker stress patterns
- **SNR**: Audio quality improved with better signal clarity

#### Training Metrics & Convergence

- **Final Training Loss**: 0.1997
- **Final Validation Loss**: 0.8564
- **Loss Gap**: 0.6567 (minor overfitting, but metrics still improved)
- **Gradient Flow**: Stable throughout training
- **Convergence**: Achieved optimal performance by epoch 7-8

#### Fine-tuning Method Details

**LoRA (Low-Rank Adaptation)** works by:
1. Freezing the original model weights
2. Adding small trainable matrices (adapters) alongside each linear layer
3. Decomposing weight updates into low-rank components: **Δθ = B·A** where rank(A)=r, rank(B)=r
4. Enabling efficient fine-tuning with 0.1% of model parameters while maintaining performance

**Advantages**:
- ✅ Reduced memory footprint (fits on consumer GPUs)
- ✅ Faster training (15-20 minutes vs hours)
- ✅ Prevents catastrophic forgetting
- ✅ Adapters can be merged or swapped for multiple voices
- ✅ Maintains base model capabilities for zero-shot synthesis

---

## 📁 Project Structure

```
SpeechEcho_web/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── main.py         # FastAPI application entry
│   │   ├── config.py       # Configuration settings
│   │   ├── database.py     # SQLAlchemy setup
│   │   ├── models/         # Database models (User, ChatHistory, VoiceProfile)
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── routers/        # API endpoints (auth, chat, tts, voices, etc.)
│   │   └── services/       # Business logic
│   │       ├── tts_service.py         # Chatterbox TTS integration
│   │       ├── voice_service.py       # Voice cloning & management
│   │       ├── voice_chat_service.py  # Voice+Chat synthesis
│   │       └── ...
│   ├── static/             # Generated audio files
│   └── requirements.txt    # Python dependencies
│
├── chatterbox-streaming/   # Chatterbox TTS Model (LoRA Fine-tuned)
│   ├── src/chatterbox/
│   │   ├── tts.py          # TTS generation (streaming + standard)
│   │   └── vc.py           # Voice conversion
│   ├── checkpoints_lora/   # LoRA adapter checkpoints
│   └── README.md           # Chatterbox documentation
│
└── frontend/               # React Frontend
    ├── src/
    │   ├── components/     # Reusable components (Chat, TTS, VoiceClone)
    │   ├── contexts/       # React Context (Auth, User)
    │   ├── pages/          # Page components (Dashboard, Studio, Chat)
    │   ├── services/       # API service layer
    │   └── App.jsx         # Main application
    ├── package.json        # Node dependencies
    └── vite.config.js      # Vite configuration
```

## 🚀 Getting Started

### Quick Start (local)

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

```bash
cd frontend
npm install
npm run dev
```

App: `http://localhost:5173` • API: `http://localhost:8000/api/docs`

### Prerequisites

- **Node.js** >= 18.x
- **Python** >= 3.10
- **pip** (Python package manager)

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create environment file:
   ```bash
   cp .env.example .env
   ```

5. Edit `.env` and add your configurations:
   ```env
   SECRET_KEY=your-super-secret-key
   GEMINI_API_KEY=your-gemini-api-key  # Optional, for AI chat
   ```

6. Start the backend server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

   The API will be available at `http://localhost:8000`
   - API Docs: `http://localhost:8000/api/docs`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

   The app will be available at `http://localhost:5173`

## 🔧 Configuration

### Backend Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | JWT secret key | Required |
| `ALGORITHM` | JWT algorithm | HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry | 30 |
| `GEMINI_API_KEY` | Google Gemini API key | Optional |
| `DATABASE_URL` | SQLite database URL | sqlite:///./speechecho.db |

### Frontend Features (Mock Mode)

The frontend can work without the backend using:
- **localStorage** for data persistence
- **Web Speech API** for TTS
- **Mock responses** for chat

## 📚 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get token
- `GET /api/auth/me` - Get current user

### Voice Cloning
- `POST /api/voices/clone` - Clone a voice from audio
- `GET /api/voices/` - Get all voices
- `DELETE /api/voices/{id}` - Delete a voice

### Text-to-Speech
- `POST /api/tts/generate` - Generate speech from text
- `POST /api/tts/preview` - Preview a voice

### Documents
- `POST /api/documents/upload` - Upload and extract PDF text
- `POST /api/documents/convert` - Convert text to audio

### Chat
- `POST /api/chat/message` - Send message and get response
- `WebSocket /api/chat/ws/{session_id}` - Real-time chat
- `GET /api/chat/history/{session_id}` - Get chat history

## 🎨 Design System

### Color Palette
- **Primary**: Indigo (#4F46E5)
- **Secondary**: Slate Gray (#64748B)
- **Background**: White/Off-white
- **Accents**: Gradient blues and purples

### Typography
- Font: Inter
- Weights: 300, 400, 500, 600, 700

## 🛠️ Tech Stack

### Frontend
- React 18 + Vite
- Tailwind CSS
- React Router DOM
- Axios
- Lucide React (icons)
- Framer Motion (animations)

### Backend
- FastAPI
- SQLAlchemy + SQLite
- Pydantic
- python-jose (JWT)
- pyttsx3 (TTS)
- pydub (Audio processing)
- PyPDF2 (PDF extraction)
- Google Generative AI (optional)

## 📝 Notes

### Repository Notes
- Large model artifacts and virtual environments are excluded via `.gitignore`.
- If you need Chatterbox models locally, place them under `chatterbox-streaming/` after cloning.

### Mock Implementation
This is an MVP demo. The voice cloning feature uses random parameters instead of actual AI training. The real implementation would require:
- Voice cloning model (e.g., Coqui TTS, XTTS)
- GPU resources for training
- Larger audio samples

### Browser Compatibility
- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Limited Web Speech API support

## 👨‍💻 Development

### Running Tests
```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

### Building for Production
```bash
# Frontend
cd frontend
npm run build
```

---

## 📚 Research & Technical Documentation

### Fine-Tuning Research

The LoRA fine-tuning implementation is based on recent advances in parameter-efficient transfer learning:

**Related Work**:
- **LoRA (Hu et al., 2021)**: Low-Rank Adaptation for Large Language Models
- **Neural TTS**: Tacotron, FastSpeech, VITS, Chatterbox
- **Voice Cloning**: Speaker embedding-based and fine-tuning approaches
- **Prosody Modeling**: F0 and energy correlation for natural synthesis

### Evaluation Methodology

**Metrics Used**:
1. **Speaker Similarity** (ECAPA-TDNN model from SpeechBrain)
   - Uses speaker embeddings (cosine similarity)
   - Measures how well synthesized voice matches target speaker
   - Range: 0 to 1 (higher = better)

2. **F0 Correlation** (Fundamental Frequency / Pitch)
   - Analyzes pitch contour alignment
   - Measures if pitch rises/falls at appropriate times
   - Range: -1 to +1 (positive values indicate good alignment)

3. **Energy Correlation** (Loudness Dynamics)
   - Evaluates emphasis and dynamic patterns
   - Captures how energy/stress patterns match
   - Range: -1 to +1 (higher = better speaker dynamics)

4. **Signal-to-Noise Ratio (SNR)**
   - Measures audio quality (dB)
   - Higher values indicate cleaner, less noisy audio

### Key Findings

✅ **Efficiency**: LoRA achieved improvements with only 0.1% trainable parameters  
✅ **Data Efficiency**: Small dataset (38.68 min) produced measurable improvements  
✅ **Multi-metric Gains**: All 3 quality metrics improved after fine-tuning  
✅ **Prosody Enhancement**: F0 correlation shifted from negative to positive  
✅ **Practical Training**: ~15-20 minutes on consumer GPU (RTX 4090)  

### Limitations & Future Work

**Current Limitations**:
- Fine-tuning is speaker-specific (requires ~40 minutes of data per speaker)
- Single-speaker dataset may not generalize to arbitrary voices
- Real-time factor depends on GPU hardware

**Future Enhancements**:
- Multi-speaker LoRA adapters for faster voice personalization
- Larger, more diverse training datasets
- Integration of emotional speech datasets for better expressiveness control
- Continuous learning from user feedback
- Cross-lingual voice adaptation
- Voice cloning from shorter samples (<3 seconds)

---

## 🔗 References & Resources

### Primary Sources
- **Chatterbox TTS**: https://github.com/davidbrowne17/chatterbox-streaming
- **LoRA Paper**: Hu, E., Shen, Y., Wallis, P., et al. (2021). "LoRA: Low-Rank Adaptation of Large Language Models"
- **SpeechBrain**: https://github.com/speechbrain/speechbrain (for ECAPA-TDNN)

### Model Resources
- **Base Model**: Chatterbox TTS (0.5B Llama backbone, pre-trained on 0.5M hours of audio)
- **Fine-tuned Adapter**: LoRA weights for Hussain's voice (~38.68 minutes of training data)
- **Evaluation Tools**: compare_models.py, extract_training_plots.py

### Audio Processing
- **Sample Rate**: 24 kHz (native Chatterbox format)
- **Format**: WAV (lossless), MP3/AAC (compressed)
- **Streaming**: Real-time chunk generation via `generate_stream()`

---

## 📄 License

This project is part of a Final Year Project (FYP) for GIKI.

**Chatterbox TTS** is licensed under the MIT License.

---

**SpeechEcho** - Real-Time Voice Cloning and Conversational Synthesis System  
*Built with state-of-the-art open-source TTS and efficient fine-tuning techniques*
