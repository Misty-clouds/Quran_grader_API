# Quran Recitation Grader API

A production-ready FastAPI service for transcribing and grading Quranic recitations using OpenAI's Whisper model.

## ✨ Production Features

- 🔒 **Security**: CORS configuration, input validation, file size limits
- 📊 **Monitoring**: Health checks, structured logging, error tracking
- 🚀 **Performance**: Async processing, resource cleanup, connection pooling
- 🐳 **Deployment**: Docker support with multi-stage builds
- 📱 **Mobile Ready**: Flutter client example included
- 🛡️ **Robust**: Comprehensive error handling and validation

## Recent Improvements

### Fixed Issues:
1. **Arabic Text Normalization**: Enhanced handling of Unicode variants, diacritics, and special characters
2. **Word Comparison Logic**: Improved fuzzy matching with better threshold handling
3. **Content-Type Validation**: Fixed None pointer exception in file type validation
4. **Bismillah Grading**: Now correctly handles text with diacritics vs. without (improved from 50% to 91%+)

### Test Results:
- **Bismillah Test**: `بِسْمِ ٱللّٰهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ` vs `بسم الله الرحمن الرحيم` → **91.43%** (was 50%)
- **Single Letter Test**: `ا` vs `ألف` → **95%** (maintained)
- **Perfect Match**: `بسم الله الرحمن الرحيم` vs `بسم الله الرحمن الرحيم` → **100%**

## Features

- 🎵 Audio transcription using Whisper (Arabic language support)
- 📝 Advanced Arabic text comparison with phonetic matching
- 🎯 Intelligent grading system with similarity scoring
- 🔤 Single letter recognition with phonetic alternatives
- 📊 Detailed grading results with pass/fail indication

## Project Structure

```
quran_grader_api/
├── main.py                    # Main FastAPI application
├── requirements.txt           # Python dependencies
├── runtime.txt               # Python version for Render
├── .env.example              # Environment configuration template
├── .gitignore                # Git ignore rules
├── README.md                 # This file
├── RENDER_DEPLOYMENT.md      # Detailed deployment guide
├── flutter_client.dart      # Flutter/Dart client example
├── test_production.py        # Local API testing
└── test_render.py           # Render deployment testing
```

## Quick Start

### Using Docker (Recommended for Production)

```bash
# Clone the repository
git clone <repository-url>
cd quran_grader_api

# Build and run with Docker Compose
docker-compose up --build

# API will be available at http://localhost:8000
```

### Manual Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd quran_grader_api
```

2. **Set up virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment (optional)**
```bash
cp .env.example .env
# Edit .env file with your settings
```

5. **Run the server**
```bash
python main.py
```

## Configuration

Environment variables can be set in `.env` file or passed directly:

| Variable | Default | Description |
|----------|---------|-------------|
| `WHISPER_MODEL_SIZE` | `medium` | Whisper model size (tiny, base, small, medium, large) |
| `WHISPER_DEVICE` | `cpu` | Device to run on (cpu, cuda) |
| `WHISPER_COMPUTE_TYPE` | `int8` | Compute precision (int8, float16, float32) |
| `MAX_FILE_SIZE` | `50` | Maximum audio file size in MB |
| `PASS_THRESHOLD` | `70.0` | Minimum grade percentage to pass |
| `ALLOWED_ORIGINS` | `*` | CORS allowed origins (comma-separated) |
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8000` | Server port |

## API Endpoints

### POST `/grade_recitation/`
Grade a Quranic recitation by comparing audio transcription with reference text.

**Parameters:**
- `audio_file`: Audio file (WAV, MP3, M4A, etc.)
- `compared_letters`: Reference Quranic text

**Response:**
```json
{
  "transcribed_text": "بسم الله الرحمن الرحيم",
  "grade": 95.5,
  "is_passed": true,
  "reference_text": "بسم الله الرحمن الرحيم",
  "similarity_score": 0.955,
  "processing_time_ms": 1250
}
```

### GET `/health`
Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "model_status": "loaded",
  "timestamp": 1692179400.123,
  "configuration": {
    "model_size": "medium",
    "device": "cpu",
    "pass_threshold": 70.0
  }
}
```

## Flutter Integration

A complete Flutter client example is provided in `flutter_client.dart`.

**Basic usage:**
```dart
final client = QuranGraderClient(baseUrl: 'http://your-api-url:8000');

try {
  final result = await client.gradeRecitation(
    audioBytes: audioFileBytes,
    referenceText: 'بسم الله الرحمن الرحيم',
  );
  
  print('Grade: ${result.grade}%');
  print('Passed: ${result.isPassed}');
} catch (e) {
  print('Error: $e');
} finally {
  client.dispose();
}
```

## Production Deployment

### Render.com Deployment (Recommended)

Render provides easy deployment with automatic SSL and scaling:

1. **Push to GitHub:** Ensure your code is in a GitHub repository
2. **Connect to Render:** 
   - Go to [render.com](https://render.com)
   - Create new Web Service
   - Connect your GitHub repo
3. **Configure Service:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python main.py`
   - **Environment Variables:** See `RENDER_DEPLOYMENT.md`
4. **Deploy:** Render will automatically build and deploy

**Render URL Example:** `https://your-service-name.onrender.com`

📋 **Detailed Guide:** See [RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md)

### Docker Deployment
### Docker Deployment (Alternative)

If you prefer Docker over Render:

```bash
# Create a simple Dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y ffmpeg
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 10000
CMD ["python", "main.py"]

# Build and run
docker build -t quran-grader-api .
docker run -p 10000:10000 -e ALLOWED_ORIGINS=https://yourdomain.com quran-grader-api
```

### Security Considerations
1. **CORS**: Configure `ALLOWED_ORIGINS` for your domain
2. **HTTPS**: Use reverse proxy (nginx/cloudflare) for TLS
3. **Rate Limiting**: Implement rate limiting for production
4. **File Validation**: Built-in file size and type validation
5. **Logging**: Structured logging for monitoring

### Performance Optimization
1. **Model Size**: Use `tiny` or `small` for faster processing
2. **GPU**: Set `WHISPER_DEVICE=cuda` if GPU available
3. **Resource Limits**: Configure Docker memory/CPU limits
4. **Caching**: Consider caching for repeated requests

## Testing

### Local Testing
Run the production test suite:
```bash
python test_production.py
```

### Render Deployment Testing
Test your Render deployment:
```bash
python test_render.py
```

This tests:
- Health endpoints
- API documentation availability
- CORS configuration  
- Service responsiveness

### Legacy Testing
```bash
# Run local production tests (optional)
python test_production.py
```

## Monitoring

The API includes:
- Health check endpoints (`/health`)
- Structured logging to files and console
- Processing time metrics
- Error tracking with stack traces

## Production Checklist

✅ **Security**
- CORS properly configured
- Input validation and sanitization
- File size and type restrictions
- No sensitive data in error messages

✅ **Performance**
- Async request handling
- Resource cleanup
- Model caching
- Processing time monitoring

✅ **Reliability**
- Comprehensive error handling
- Health check endpoints
- Structured logging
- Graceful shutdown

✅ **Documentation**
- OpenAPI/Swagger docs at `/docs`
- Flutter client example
- Production deployment guide
- Configuration reference
