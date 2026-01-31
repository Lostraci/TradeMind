import os
from dotenv import load_dotenv
from src.graph.workflow import create_graph
from src.tools.scanner import MarketScanner

# .env dosyasındaki API anahtarlarını yükle
load_dotenv()

def run_analysis(app, ticker):
    print(f"\n🚀 {ticker} için analiz başlatılıyor...\n")
    initial_state = {
        "ticker": ticker,
        "technical_data": {},
        "fundamental_data": {},
        "sentiment_data": {},
        "quant_data": {},
        "final_report": ""
    }
    try:
        result = app.invoke(initial_state)
        print("\n" + "="*50)
        print(f"📊 YATIRIM KOMİTESİ KARARI ({ticker})")
        print("="*50)
        print(result["final_report"])
        print("="*50)
    except Exception as e:
        print(f"\n❌ {ticker} analiz edilirken hata: {e}")

def main():
    # Grafı oluştur
    app = create_graph()
    
    print("TradeMind AI - Yapay Zeka Borsa Asistanı")
    print("="*40)
    print("Mod Seçimi:")
    print("1. Tek Hisse Analizi (Manuel)")
    print("2. Piyasa Tarama ve En İyi 3 Hisse (Otomatik)")
    
    choice = input("Seçiminiz (1 veya 2): ")
    
    if choice == "2":
        print("\n🔍 Piyasa taranıyor... (Bu işlem biraz sürebilir)")
        scanner = MarketScanner()
        top_tickers = scanner.scan_market()
        print(f"\n🔍 Bulunan Fırsatlar: {top_tickers}")
        
        for ticker in top_tickers:
            print(f"\n{'*'*20} {ticker} Analiz Ediliyor {'*'*20}")
            run_analysis(app, ticker)
            
    else:
        # Default to option 1
        hisse = input("Analiz edilecek hisse kodu (örn: THYAO.IS): ")
        if not hisse:
            hisse = "THYAO.IS"
        run_analysis(app, hisse)

if __name__ == "__main__":
    main()