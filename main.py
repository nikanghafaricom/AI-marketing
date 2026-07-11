import asyncio
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from edge_tts import Communicate

app = FastAPI(title="AI Marketing Voice Automation Platform")

# مدل داده‌ای برای ورودی متن
class TextRequest(BaseModel):
    text: str
    voice: str = "fa-IR-FaridNeural"  # پیش‌فرض صدای مرد

# تابع اعراب‌گذاری خودکار کلمات تبلیغاتی
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

# ۱. مسیر ریشه (بسیار مهم برای رندر تا متوجه شود سایت روشن و سالم است)
@app.get("/")
def home():
    return {"status": "healthy", "message": "پلتفرم اتوماسیون محتوا با موفقیت روی رندر فعال است."}

# ۲. مسیر تولید صدا (API Endpoint)
@app.post("/generate-voice/")
async def generate_voice_api(request: TextRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="متن ورودی نمی‌تواند خالی باشد.")
    
    clean_text = preprocess_persian_text(request.text)
    output_filename = "output_voice.mp3"
    
    # تنظیمات سرعت تبلیغاتی
    rate = "+15%"
    volume = "+0%"
    
    try:
        communicate = Communicate(clean_text, request.voice, rate=rate, volume=volume)
        await communicate.save(output_filename)
        
        # بازگرداندن فایل صوتی ساخته شده به کاربر
        if os.path.exists(output_filename):
            return FileResponse(output_filename, media_type="audio/mpeg", filename=output_filename)
        else:
            raise HTTPException(status_code=500, detail="فایل صوتی ایجاد نشد.")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطا در پردازش صدا: {str(e)}")

# اجرای سرور محلی (در صورت نیاز به تست روی کامپیوتر خودت)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main.py:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), reload=True)
