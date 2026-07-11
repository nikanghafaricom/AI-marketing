import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from edge_tts import Communicate

app = FastAPI(title="AI Marketing Voice Automation Platform")

class TextRequest(BaseModel):
    text: str
    voice: str = "fa-IR-FaridNeural"

def preprocess_persian_text(text: str) -> str:
    replacements = {
        "خرید آنلاین": "خریدِ آنلاین",
        "کسب و کار": "کسب و کار",
        "تخفیف ویژه": "تخفیفِ ویژه",
        "صفحه فروش": "صفحهٔ فروش",
        "شبکه‌های اجتماعی": "شبکه‌هایِ اجتماعی",
        "دیجیتال مارکتینگ": "دیجیتال مارکتینگ",
        "اینستاگرام": "اینستاگرام",
        "یوتیوب": "یوتیوب",
        "رایگان": "رایگان",
        "پلتفرم": "پلتفرم",
        "اتوماسیون": "اتوماسیون",
    }
    processed_text = text
    for word, corrected in replacements.items():
        processed_text = processed_text.replace(word, corrected)
    return processed_text

@app.get("/")
def home():
    return {"status": "healthy", "message": "پلتفرم با موفقیت فعال است."}

@app.post("/generate-voice/")
async def generate_voice_api(request: TextRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="متن ورودی نمی‌تواند خالی باشد.")
    
    clean_text = preprocess_persian_text(request.text)
    # استفاده از مسیر /tmp که در رندر همیشه قابل نوشتن است
    output_filename = "/tmp/output_voice.mp3"
    
    rate = "+15%"
    volume = "+0%"
    
    try:
        communicate = Communicate(clean_text, request.voice, rate=rate, volume=volume)
        await communicate.save(output_filename)
        
        if os.path.exists(output_filename):
            return FileResponse(output_filename, media_type="audio/mpeg", filename="output_voice.mp3")
        else:
            raise HTTPException(status_code=500, detail="فایل صوتی ایجاد نشد.")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطا در پردازش صدا: {str(e)}")

# بخش بسیار مهم برای Render:
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
