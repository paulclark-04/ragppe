import fitz  # PyMuPDF
import whisper
import os
import ssl

# Initialize Whisper model (lazy loading recommended in production, but global for now)
# using "base" for speed in dev, "medium" recommended for prod
whisper_model = None

def get_whisper_model():
    global whisper_model
    if whisper_model is None:
        # Bypass SSL verification for model download (common issue on Mac)
        ssl._create_default_https_context = ssl._create_unverified_context
        whisper_model = whisper.load_model("base")
    return whisper_model

async def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF using PyMuPDF."""
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

async def extract_text_from_audio_video(file_path: str) -> str:
    """Extract text from Audio/Video using Whisper."""
    print(f"Entered extract_text_from_audio_video for {file_path}")
    print("Loading Whisper model... (this may take a while if downloading)")
    model = get_whisper_model()
    print(f"Model loaded. Starting transcription for {file_path}...")
    result = model.transcribe(file_path)
    text = result["text"]
    print(f"Transcription complete. Length: {len(text)} chars. Preview: {text[:100]}...")
    return text

async def extract_content(file_path: str, file_type: str) -> str:
    """Route to appropriate extraction method."""
    print(f"Entered extract_content with type: {file_type}")
    # Fallback to extension if content-type is generic
    if file_type == "application/octet-stream" or not file_type:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            file_type = "application/pdf"
        elif ext in [".mp3", ".wav", ".m4a", ".mp4", ".mov", ".avi"]:
            file_type = "audio/mpeg" # Treat as audio/video
        elif ext == ".txt":
            file_type = "text/plain"

    if file_type == "application/pdf":
        return await extract_text_from_pdf(file_path)
    elif file_type.startswith("audio/") or file_type.startswith("video/"):
        return await extract_text_from_audio_video(file_path)
    elif file_type == "text/plain":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
