# main.py
from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, Field
import uvicorn
import io
import re
import logging
import os
import time
from typing import List, Dict, Optional
from contextlib import asynccontextmanager

# Import Whisper
from faster_whisper import WhisperModel


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration - Optimized for Render with sensible defaults
class Config:
    # Use small model by default for faster startup and lower memory usage
    # Can be overridden with environment variable if needed
    MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "medium")
    
    # CPU optimized settings for Render
    COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE_TYPE", "int8")
    DEVICE = os.getenv("WHISPER_DEVICE", "cpu")
    
    # Balanced file size limit for quality vs performance
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "30")) * 1024 * 1024  # 30MB default
    
    # Standard passing threshold
    PASS_THRESHOLD = float(os.getenv("PASS_THRESHOLD", "70.0"))
    
    # Allow all origins by default for easy Flutter integration
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    
    # Render's standard port
    PORT = int(os.getenv("PORT", "10000"))

config = Config()

# Pydantic models for request/response
class GradingResponse(BaseModel):
    transcribed_text: str
    grade: float = Field(..., ge=0, le=100)
    is_passed: bool
    reference_text: str
    similarity_score: float = Field(..., ge=0, le=1)
    processing_time_ms: int

class ErrorResponse(BaseModel):
    error: str
    detail: str
    timestamp: str

# Global model variable
model: Optional[WhisperModel] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global model
    try:
        logger.info(f"Loading Whisper model '{config.MODEL_SIZE}' on {config.DEVICE}")
        model = WhisperModel(config.MODEL_SIZE, device=config.DEVICE, compute_type=config.COMPUTE_TYPE)
        logger.info(f"Whisper model loaded successfully")
    except Exception as e:
        logger.error(f"Error loading Whisper model: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")

app = FastAPI(
    title="Quran Recitation Grader API",
    description="API for transcribing Quranic recitations using Whisper and grading them.",
    version="1.0.0",
    lifespan=lifespan,
    responses={
        500: {"model": ErrorResponse},
        400: {"model": ErrorResponse},
    }
)

# Add CORS middleware for Flutter apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if "*" in config.ALLOWED_ORIGINS else config.ALLOWED_ORIGINS
)


# --- Helper Functions (Python equivalents of your Dart functions) ---

def get_arabic_letter_phonetics() -> Dict[str, List[str]]:
    return {
        'ا': ['الف', 'ألف', 'اليف', 'الیف', 'alif', 'alef'],
        'ب': ['باء', 'بآء', 'با', 'بائ', 'baa', 'ba'],
        'ت': ['تاء', 'تآء', 'تا', 'تائ', 'taa', 'ta'],
        'ث': ['ثاء', 'ثآء', 'ثا', 'ثائ', 'thaa', 'tha'],
        'ج': ['جيم', 'جیم', 'جم', 'jim', 'jeem'],
        'ح': ['حاء', 'حآء', 'حا', 'حائ', 'haa', 'ha'],
        'خ': ['خاء', 'خآء', 'خا', 'خائ', 'khaa', 'kha'],
        'د': ['دال', 'دآل', 'دل', 'dal', 'daal'],
        'ذ': ['ذال', 'ذآل', 'ذل', 'zal', 'thaal'],
        'ر': ['راء', 'رآء', 'را', 'رائ', 'raa', 'ra'],
        'ز': ['زاي', 'زای', 'زي', 'زی', 'zay', 'zaay'],
        'س': ['سين', 'سین', 'سن', 'seen', 'sin'],
        'ش': ['شين', 'شین', 'شن', 'sheen', 'shin'],
        'ص': ['صاد', 'صآد', 'صد', 'saad', 'sad'],
        'ض': ['ضاد', 'ضآد', 'ضد', 'daad', 'dhad'],
        'ط': ['طاء', 'طآء', 'طا', 'طائ', 'taa', 'ta'],
        'ظ': ['ظاء', 'ظآء', 'ظا', 'ظائ', 'zaa', 'za'],
        'ع': ['عين', 'عین', 'عن', 'ayn', 'ain'],
        'غ': ['غين', 'غین', 'غن', 'ghayn', 'ghain'],
        'ف': ['فاء', 'فآء', 'فا', 'فائ', 'faa', 'fa'],
        'ق': ['قاف', 'قآف', 'قف', 'qaaf', 'qaf'],
        'ك': ['كاف', 'كآف', 'كف', 'kaaf', 'kaf'],
        'ل': ['لام', 'لآم', 'لم', 'laam', 'lam'],
        'م': ['ميم', 'میم', 'مم', 'meem', 'mim'],
        'ن': ['نون', 'نون', 'نن', 'noon', 'nun'],
        'ه': ['هاء', 'هآء', 'ها', 'هائ', 'haa', 'ha'],
        'و': ['واو', 'وآو', 'وو', 'waaw', 'waw'],
        'ي': ['ياء', 'یاء', 'یآء', 'يائ', 'یائ', 'yaa', 'ya'],
        'ى': ['ياء', 'یaء', 'یآء', 'يائ', 'یائ', 'yaa', 'ya'],
    }


def normalize_arabic_text(text: str) -> str:
    # Remove diacritics
    text = re.sub(r'[\u064B-\u0652]', '', text)
    
    # Remove tatweel (kashida)
    text = re.sub(r'\u0640', '', text)

    # Normalize similar letters
    text = re.sub(r'[أإآا]', 'ا', text)
    text = re.sub(r'[يى]', 'ي', text)
    text = re.sub(r'[ةت]', 'ت', text)  # Be careful with this for recitation
    
    # Normalize special Unicode variants
    text = re.sub(r'ٱ', 'ا', text)  # Arabic Letter Alef Wasla
    text = re.sub(r'ﷲ', 'الله', text)  # Allah ligature
    text = re.sub(r'ﷺ', '', text)  # Remove Islamic symbols
    text = re.sub(r'ﷻ', '', text)  # Remove Islamic symbols

    # Remove non-Arabic characters except spaces
    text = re.sub(r'[^\u0600-\u06FF\s]', '', text)
    
    # Clean up extra spaces
    text = re.sub(r'\s+', ' ', text)

    return text.strip().lower()


def is_single_arabic_letter(text: str) -> bool:
    normalized = normalize_arabic_text(text)
    return len(normalized) == 1 and bool(re.match(r'[\u0600-\u06FF]', normalized))


def levenshtein_distance(s1: str, s2: str) -> int:
    m, n = len(s1), len(s2)
    d = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        d[i][0] = i
    for j in range(n + 1):
        d[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + cost)
    return d[m][n]


def compare_words(word1: str, word2: str) -> float:
    max_length = max(len(word1), len(word2))
    if max_length == 0:
        return 1.0

    distance = levenshtein_distance(word1, word2)
    return 1 - (distance / max_length)


def calculate_phonetic_similarity(spoken: str, target: str, alternatives: List[str]) -> float:
    max_similarity = 0.0

    for alt in alternatives:
        normalized_alt = normalize_arabic_text(alt)
        similarity = compare_words(spoken, normalized_alt)
        max_similarity = max(max_similarity, similarity)

    if max_similarity < 0.3:
        if len(spoken) <= 3 and target in spoken:  # Check if target char is in short spoken text
            return 0.6

    return max_similarity * 0.8


def compare_single_letter(spoken: str, target_letter: str) -> float:
    normalized_spoken = normalize_arabic_text(spoken)
    normalized_target = normalize_arabic_text(target_letter)

    if normalized_spoken == normalized_target:
        return 1.0

    phonetics = get_arabic_letter_phonetics()

    if normalized_target in phonetics:
        alternatives = phonetics[normalized_target]

        for alternative in alternatives:
            normalized_alt = normalize_arabic_text(alternative)

            if normalized_spoken == normalized_alt:
                return 0.95

            if normalized_alt in normalized_spoken or normalized_spoken in normalized_alt:
                similarity = compare_words(normalized_spoken, normalized_alt)
                if similarity > 0.7:
                    return similarity * 0.9

        if normalized_target in normalized_spoken:
            return 0.8

        return calculate_phonetic_similarity(normalized_spoken, normalized_target, alternatives)

    return 0.0


def compare_quranic_arabic(recited: str, reference: str) -> float:
    recited = normalize_arabic_text(recited)
    reference = normalize_arabic_text(reference)

    if is_single_arabic_letter(reference):
        return compare_single_letter(recited, reference)

    recited_words = [w for w in recited.split(' ') if w]
    reference_words = [w for w in reference.split(' ') if w]

    if not reference_words:
        return 0.0
    
    if not recited_words:
        return 0.0

    total_similarity = 0.0
    total_words = len(reference_words)

    for i in range(total_words):
        word_similarity = 0.0
        
        if i < len(recited_words):
            if is_single_arabic_letter(reference_words[i]):
                word_similarity = compare_single_letter(recited_words[i], reference_words[i])
            else:
                # Try exact match first
                if recited_words[i] == reference_words[i]:
                    word_similarity = 1.0
                else:
                    # Try fuzzy matching with lower threshold
                    base_similarity = compare_words(recited_words[i], reference_words[i])
                    
                    # Also check if the recited word contains the reference word or vice versa
                    if reference_words[i] in recited_words[i] or recited_words[i] in reference_words[i]:
                        containment_bonus = 0.3
                    else:
                        containment_bonus = 0.0
                    
                    word_similarity = min(1.0, base_similarity + containment_bonus)
        
        # If word similarity is below threshold, try to find the word elsewhere in the recited text
        if word_similarity < 0.6:
            for j, recited_word in enumerate(recited_words):
                if j != i:  # Don't check the same position again
                    alt_similarity = compare_words(recited_word, reference_words[i])
                    if alt_similarity > word_similarity:
                        word_similarity = alt_similarity * 0.8  # Penalty for wrong position
        
        total_similarity += word_similarity

    # Calculate average similarity
    average_similarity = total_similarity / total_words
    
    # Apply length penalty if recited text is significantly different in length
    length_ratio = len(recited_words) / len(reference_words)
    if length_ratio < 0.8 or length_ratio > 1.2:
        length_penalty = 0.9
    else:
        length_penalty = 1.0
    
    return average_similarity * length_penalty


# --- FastAPI Endpoints ---

@app.post("/grade_recitation/", response_model=GradingResponse)
async def grade_recitation(
        request: Request,
        audio_file: UploadFile = File(..., description="Audio file containing Quranic recitation"),
        compared_letters: str = Form(..., description="Reference Quranic text to compare against")
):
    """
    Grade a Quranic recitation by comparing the transcribed audio with reference text.
    
    - **audio_file**: Audio file (WAV, MP3, M4A, etc.) containing the recitation
    - **compared_letters**: The reference Quranic text to compare against
    
    Returns detailed grading information including similarity score and pass/fail status.
    """
    start_time = time.time()
    client_ip = request.client.host if request.client else "unknown"
    
    logger.info(f"Grading request from {client_ip} - Reference: '{compared_letters[:50]}...'")
    
    # Validation
    if not compared_letters or not compared_letters.strip():
        logger.warning(f"Empty reference text from {client_ip}")
        raise HTTPException(
            status_code=400, 
            detail="Reference Quranic text (compared_letters) is required and cannot be empty."
        )

    if not audio_file.filename:
        raise HTTPException(status_code=400, detail="No file provided.")
    
    # Check file size
    if audio_file.size and audio_file.size > config.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400, 
            detail=f"File too large. Maximum size allowed: {config.MAX_FILE_SIZE // (1024*1024)}MB"
        )

    # Validate file type
    if not audio_file.content_type or not audio_file.content_type.startswith("audio/"):
        raise HTTPException(
            status_code=400, 
            detail="Invalid file type. Please upload an audio file (WAV, MP3, M4A, etc.)."
        )

    audio_stream = None
    try:
        # Ensure model is loaded
        global model
        if model is None:
            raise HTTPException(status_code=500, detail="Speech recognition model not available")
        
        # Read audio file into a BytesIO object for Whisper
        audio_bytes = await audio_file.read()
        
        if len(audio_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file")
        
        audio_stream = io.BytesIO(audio_bytes)

        # Transcribe audio using Whisper
        logger.info(f"Transcribing audio from {client_ip} - File: {audio_file.filename}")
        segments, info = model.transcribe(audio_stream, language="ar", beam_size=5)
        
        spoken_text = " ".join([segment.text for segment in segments])
        logger.info(f"Transcription result: '{spoken_text}'")

        # Perform grading
        similarity = compare_quranic_arabic(spoken_text, compared_letters)
        grade = round(similarity * 100, 2)
        is_passed = grade >= config.PASS_THRESHOLD
        
        processing_time = int((time.time() - start_time) * 1000)
        
        logger.info(f"Grading complete - Grade: {grade}%, Passed: {is_passed}, Time: {processing_time}ms")

        return GradingResponse(
            transcribed_text=spoken_text,
            grade=grade,
            is_passed=is_passed,
            reference_text=compared_letters,
            similarity_score=similarity,
            processing_time_ms=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing request from {client_ip}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail="An error occurred while processing your request. Please try again."
        )
    finally:
        # Clean up audio stream if it was created
        try:
            if audio_stream is not None:
                audio_stream.close()
        except:
            pass


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Quran Recitation Grader API is running!",
        "status": "healthy",
        "model_loaded": model is not None,
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check for monitoring"""
    return {
        "status": "healthy",
        "model_status": "loaded" if model is not None else "not_loaded",
        "timestamp": time.time(),
        "configuration": {
            "model_size": config.MODEL_SIZE,
            "device": config.DEVICE,
            "pass_threshold": config.PASS_THRESHOLD
        }
    }


# --- Run the server ---
if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "10000"))  # Render's default port
    
    logger.info(f"Starting Quran Grader API on {host}:{port}")
    uvicorn.run(
        app, 
        host=host, 
        port=port,
        log_level="info",
        access_log=True
    )

