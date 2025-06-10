# main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import io
import re
from typing import List, Dict

# Import Whisper
from faster_whisper import WhisperModel

# --- Whisper Model Loading (Global or in a lifespan context for FastAPI) ---
# Choose a model size: 'tiny', 'base', 'small', 'medium', 'large-v2', 'large-v3'
# 'medium' or 'large-v2/v3' are good for Arabic accuracy but require more resources.
# 'compute_type' can be 'int8', 'int8_float16', 'float16', 'float32'
# 'cuda' is for NVIDIA GPUs, 'cpu' for CPU. If no GPU, use 'cpu'.
# Ensure you have the appropriate PyTorch/CUDA drivers if using GPU.
model_size = "medium"  # Or "medium" for less VRAM/RAM
compute_type = "int8"  # Use "float16" if you have a modern GPU, "float32" or "int8" for CPU
device = "cpu"  # Change to "cuda" if you have an NVIDIA GPU

try:
    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    print(f"Whisper model '{model_size}' loaded successfully on {device} with {compute_type} compute type.")
except Exception as e:
    print(f"Error loading Whisper model: {e}")
    print("Please ensure you have sufficient RAM/VRAM for the chosen model size and the correct compute_type/device.")
    # Exit or handle gracefully, perhaps fall back to a smaller model or CPU
    raise

app = FastAPI(
    title="Quran Recitation Grader API",
    description="API for transcribing Quranic recitations using Whisper and grading them.",
    version="1.0.0",
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

    # Normalize similar letters
    text = re.sub(r'[أإآا]', 'ا', text)
    text = re.sub(r'[يى]', 'ي', text)
    text = re.sub(r'[ةت]', 'ت',
                  text)  # Be careful with this for recitation - 'ة' (taa marbuta) vs 'ت' (taa) are distinct sounds

    # Remove non-Arabic characters except spaces
    # Note: Arabic numbers (e.g., ٠-٩) are kept by default if they are within \u0600-\u06FF range
    text = re.sub(r'[^\u0600-\u06FF\s]', '', text)

    # ArabicNumbers library is for Flutter/Dart. In Python, we can convert if needed,
    # but Whisper usually handles numbers well if they are spoken.
    # If `text` contains English digits, you might want to convert them to Arabic digits
    # or just let them be, depending on expected input.
    # For now, we assume spoken Arabic will produce Arabic script numbers or words.
    # text = ''.join([arabic_digits.get(c, c) for c in text]) # Example for digit conversion

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

    matched_words = 0
    total_words = len(reference_words)

    for i in range(total_words):
        if i < len(recited_words):
            if is_single_arabic_letter(reference_words[i]):
                letter_similarity = compare_single_letter(recited_words[i], reference_words[i])
                if letter_similarity > 0.7:
                    matched_words += 1
            else:
                word_similarity = compare_words(recited_words[i], reference_words[i])
                if word_similarity > 0.8:
                    matched_words += 1

    return matched_words / total_words


# --- FastAPI Endpoints ---

@app.post("/grade_recitation/")
async def grade_recitation(
        audio_file: UploadFile = File(...),
        compared_letters: str = ""  # This will be the reference Quranic text
):
    if not compared_letters:
        raise HTTPException(status_code=400, detail="Reference Quranic text (compared_letters) is required.")

    if not audio_file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an audio file.")

    try:
        # Read audio file into a BytesIO object for Whisper
        audio_bytes = await audio_file.read()
        audio_stream = io.BytesIO(audio_bytes)

        # Transcribe audio using Whisper
        # You might need to specify the language if not auto-detected well
        segments, info = model.transcribe(audio_stream, language="ar", beam_size=5)  # 'ar' for Arabic

        spoken_text = " ".join([segment.text for segment in segments])

        # Perform grading
        similarity = compare_quranic_arabic(spoken_text, compared_letters)
        grade = round(similarity * 100, 2)
        is_passed = grade >= 70

        return JSONResponse(content={
            "transcribed_text": spoken_text,
            "grade": grade,
            "is_passed": is_passed,
            "reference_text": compared_letters,
            "similarity_score": similarity
        })
    except Exception as e:
        print(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@app.get("/")
async def root():
    return {"message": "Quran Recitation Grader API is running!"}

# You can add more endpoints if needed, e.g., for model status, health checks etc.