import asyncio
import os
from edge_tts import Communicate

# ۱. تابع اعراب‌گذاری خودکار کلمات کلیدی و مضاف/مضاف‌الیه تبلیغاتی
def preprocess_persian_text(text: str) -> str:
    """
    این تابع کلمات کلیدی تبلیغاتی را برای تلفظ صحیح‌تر در edge-tts بهینه‌سازی می‌کند.
    می‌توانی کلمات جدید و نحوه تلفظ صحیح آن‌ها را به این دیکشنری اضافه کنی.
    """
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

# ۲. تابع اصلی تولید صدا
async def generate_voice(text: str, output_filename: str = "output.mp3", voice: str = "fa-IR-FaridNeural"):
    """
    تولید فایل صوتی از متن با سرعت بالا و انرژی مناسب ویدیوهای تبلیغاتی
    تنظیمات صدای مرد: fa-IR-FaridNeural
    تنظیمات صدای زن: fa-IR-DilaraNeural
    """
    # پردازش متن قبل از ارسال به سرویس
    clean_text = preprocess_persian_text(text)
    
    # تنظیم سرعت روی +15% برای لحن سریع و تبلیغاتی
    # همچنین ولوم صدا کمی تقویت شده تا انرژی بالاتری داشته باشد (+0%)
    rate = "+15%"
    volume = "+0%"
    
    print(f"🎙️ در حال تولید صدا با گوینده: {voice}...")
    
    try:
        communicate = Communicate(clean_text, voice, rate=rate, volume=volume)
        await communicate.save(output_filename)
        print(f"✅ فایل صوتی با موفقیت در مسیر روبرو ذخیره شد: {os.path.abspath(output_filename)}")
    except Exception as e:
        print(f"❌ خطایی در تولید صدا رخ داد: {e}")

# ۳. بخش تست اسکریپت (مخصوص اجرای محلی و تست اوليه)
if __name__ == "__main__":
    # متن نمونه تبلیغاتی برای تست
    sample_text = (
        "اگر به دنبال رشد کسب و کار خود هستید، این پلتفرم اتوماسیون محتوا "
        "به شما کمک می‌کند تا با تخفیف ویژه، بهترین ویدیوهای اینستاگرام و یوتیوب را بسازید. "
        "همین حالا خرید آنلاین خود را شروع کنید!"
    )
    
    # انتخاب گوینده: fa-IR-FaridNeural (مرد) یا fa-IR-DilaraNeural (زن)
    selected_voice = "fa-IR-FaridNeural"
    output_file = "advertising_voice.mp3"
    
    # اجرای تابع ناهمگام
    asyncio.run(generate_voice(sample_text, output_file, selected_voice))
