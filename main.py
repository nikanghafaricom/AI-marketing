import os
import json
import asyncio
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import aiohttp
from edge_tts import Communicate

# تنظیمات لاگر برای ردیابی دقیق وضعیت در پنل رندر
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# دریافت کلیدهای محیطی از تنظیمات رندر
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# --- بخش برنده: سرور سلامت جانبی مخصوص هاست رندر ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"OK")
    def log_message(self, format, *args):
        return

def run_health_server():
    port = int(os.getenv("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    logger.info(f"Health check server started on port {port}")
    server.serve_forever()
# ---------------------------------------------------

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
        "لینک بیو": "لینکِ بیو",
    }
    processed_text = text
    for word, corrected in replacements.items():
        processed_text = processed_text.replace(word, corrected)
    return processed_text

# ۱. ماژول تولید سناریو تبلیغاتی با Groq (Llama-3)
async def generate_marketing_scenario(product_or_topic: str) -> str:
    """
    ارسال درخواست به Groq برای تولید یک سناریوی ویدیویی کوتاه، پرانرژی و جذاب تبلیغاتی به زبان فارسی.
    """
    if not GROQ_API_KEY:
        logger.error("خطا: کلید GROQ_API_KEY در تنظیمات رندر تعریف نشده است!")
        return "لطفاً ابتدا کلید ای‌پی‌آی خود را در بخش Environment Variables رندر ست کنید."

    logger.info(f"🧠 در حال تولید سناریو برای: '{product_or_topic}' با هوش مصنوعی...")
    
    # پرامپت مهندسی‌شده مخصوص ویدیوهای کوتاه تبلیغاتی
    prompt = f"""
    تو یک بازاریاب دیجیتال نابغه و کپی‌رایتر حرفه‌ای اینستاگرام و یوتیوب هستی.
    یک سناریوی ویدیویی کوتاه (حداکثر ۵۰ کلمه) برای موضوع یا محصول زیر بنویس:
    موضوع/محصول: {product_or_topic}
    
    قوانین سخت‌گیرانه:
    ۱. متن کاملاً پرانرژی، هیجانی، صمیمی و ترغیب‌کننده برای نسل جوان باشد.
    ۲. با یک قلاب (Hook) شدیداً جذاب شروع شود که کاربر اسکرول نکند.
    ۳. در انتها یک دعوت به اقدام (Call to Action) واضح مثل "روی لینک بیو کلیک کن" داشته باشد.
    ۴. فقط و فقط متن گوینده (نریشن) را بنویس. هیچ توضیح اضافه مانند "(موزیک پخش می‌شود)" یا "بخش اول:" در خروجی قرار نده.
    """
    
    payload = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.75,
        "max_tokens": 150
    }
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers, timeout=30) as response:
            if response.status == 200:
                resp_json = await response.json()
                scenario = resp_json["choices"][0]["message"]["content"].strip()
                logger.info("✅ سناریو با موفقیت تولید شد.")
                return scenario
            else:
                error_text = await response.text()
                logger.error(f"خطای Groq API: {error_text}")
                return "خطا در تولید متن تبلیغاتی."

# ۲. ماژول تولید صدای تبلیغاتی پرانرژی با edge-tts
async def generate_voice(text: str, output_filename: str = "advertising_voice.mp3", voice: str = "fa-IR-FaridNeural"):
    """
    تبدیل متن سناریو به فایل صوتی MP3 با سرعت بالا و انرژی زیاد.
    """
    clean_text = preprocess_persian_text(text)
    rate = "+15%"  # سرعت تند و پرانرژی برای ویدیوهای کوتاه
    
    logger.info(f"🎙️ در حال تبدیل سناریو به صدا با گوینده {voice}...")
    try:
        communicate = Communicate(clean_text, voice, rate=rate)
        await communicate.save(output_filename)
        logger.info(f"✅ فایل صوتی نهایی با موفقیت ذخیره شد: {output_filename}")
    except Exception as e:
        logger.error(f"خطا در تبدیل متن به صدا: {e}")

# ۳. بخش همگام‌ساز و هماهنگ‌کننده کل فرآیند
async def run_automation_pipeline(topic: str):
    # مرحله اول: تولید سناریو از Groq
    scenario = await generate_marketing_scenario(topic)
    print(f"\n📝 سناریوی تولید شده:\n{scenario}\n")
    
    # مرحله دوم: تولید هم‌زمان فایل صوتی از روی سناریو
    await generate_voice(scenario, output_filename="final_ad.mp3")

# تابع اصلی برای اجرای موازی سرور سلامت و فرآیند پلتفرم
def main():
    # ۱. روشن کردن سرور سلامت در پس‌زمینه (برای بیدار ماندن در رندر)
    threading.Thread(target=run_health_server, daemon=True).start()

    # ۲. نمونه تست اتوماتیک برای اطمینان از صحت کارکرد در اولین دپلوی
    test_topic = "کفش ورزشی فوق‌العاده راحت با ۵۰ درصد تخفیف ویژه برای خرید آنلاین امروز"
    
    # اجرای فرآیند ناهمگام در حلقه رویدادها
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_automation_pipeline(test_topic))

    # زنده نگه داشتن برنامه اصلی برای سرویس‌دهی سرور سلامت
    import time
    while True:
        time.sleep(3600)

if __name__ == "__main__":
    main()
