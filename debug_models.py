import google.generativeai as genai
import os
from dotenv import load_dotenv

# .env'den key'i çek
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("HATA: GOOGLE_API_KEY bulunamadı!")
else:
    print(f"Key bulundu: {api_key[:5]}...*****")
    genai.configure(api_key=api_key)

    print("\n--- SENİN KEY İLE ERİŞİLEBİLEN MODELLER ---")
    try:
        for m in genai.list_models():
            # Sadece içerik üretebilen (chat) modelleri listele
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
    except Exception as e:
        print(f"Bağlantı Hatası: {e}")