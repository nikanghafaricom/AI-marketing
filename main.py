import os
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from gtts import gTTS

# تنظیمات لاگر مشابه پروژه قبلی شما
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    }
    processed_text = text
    for word, corrected in replacements.items():
        processed_text = processed_text.replace(word, corrected)
    return processed_text

# تابع اصلی تولید فایل صوتی
def generate_voice(text: str, output_filename: str = "advertising_voice.mp3"):
    if not text.strip():
        logger.error("متن ورودی خالی است.")
        return
    
    clean_text = preprocess_persian_text(text)
    try:
        logger.info("🎙️ در حال تولید فایل صوتی با موتور گوگل...")
        tts = gTTS(text=clean_text, lang='fa', slow=False)
        tts.save(output_filename)
        logger.info(f"✅ فایل صوتی با موفقیت ذخیره شد: {output_filename}")
    except Exception as e:
        logger.error(f"خطا در تولید صدا: {e}")

def main():
    # ۱. روشن کردن سرور سلامت در یک Thread جداگانه (دقیقاً مثل رژیم پلاس)
    threading.Thread(target=run_health_server, daemon=True).start()

    # ۲. اجرای تست اولیه تولید صدا
    sample_text = "به پلتفرم اتوماسیون محتوای تبلیغاتی ما خوش آمدید. تخفیف ویژه برای خرید آنلاین کسب و کار شما."
    generate_voice(sample_text)

    # زنده نگه داشتن اسکریپت اصلی تا سرور سلامت قطع نشود
    import time
    while True:
        time.sleep(3600)

if __name__ == "__main__":
    main()
