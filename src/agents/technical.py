import pandas as pd
import pandas_ta as ta  # TA-Lib yerine pandas-ta kullanıyoruz, kurulumu daha kolay
from typing import Dict, Any

class TechnicalAgent:
    def __init__(self):
        pass

    def analyze(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Fiyat verisini alır, indikatörleri hesaplar ve teknik bir görüş bildirir.
        """
        if df.empty:
            return {"signal": "NEUTRAL", "reason": "Yetersiz veri."}

        # 1. İndikatör Hesaplamaları
        # RSI (14 periyot)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        # SMA 50 ve SMA 200
        df['SMA_50'] = ta.sma(df['Close'], length=50)
        df['SMA_200'] = ta.sma(df['Close'], length=200)

        # Son satırı (güncel durumu) alalım
        latest = df.iloc[-1]
        prev = df.iloc[-2] # Trend değişimi kontrolü için bir önceki gün

        signal = "NEUTRAL"
        reasons = []
        score = 0  # -5 (Güçlü Sat) ile +5 (Güçlü Al) arası puanlama

        # --- Mantık Katmanı ---

        # RSI Analizi
        rsi_val = latest['RSI']
        reasons.append(f"RSI Değeri: {rsi_val:.2f}")
        
        if rsi_val < 30:
            score += 2
            reasons.append("RSI aşırı satım bölgesinde (Dip tepkisi ihtimali).")
        elif rsi_val > 70:
            score -= 2
            reasons.append("RSI aşırı alım bölgesinde (Düzeltme riski).")

        # SMA Analizi (Trend)
        if latest['Close'] > latest['SMA_50']:
            score += 1
            reasons.append("Fiyat 50 günlük ortalamanın üzerinde (Kısa vade pozitif).")
        else:
            score -= 1
            reasons.append("Fiyat 50 günlük ortalamanın altında (Kısa vade negatif).")

        # Golden Cross / Death Cross Kontrolü
        if latest['SMA_50'] > latest['SMA_200']:
            score += 2
            reasons.append("Golden Cross mevcut (50 > 200 - Uzun vade Boğa).")
        elif latest['SMA_50'] < latest['SMA_200']:
            score -= 2
            reasons.append("Death Cross mevcut (50 < 200 - Uzun vade Ayı).")

        # Karar Mekanizması
        if score >= 3:
            signal = "BUY"
        elif score <= -3:
            signal = "SELL"
        else:
            signal = "HOLD"

        return {
            "agent": "Technical Analyst",
            "signal": signal,
            "score": score,
            "analysis": reasons,
            "metrics": {
                "RSI": rsi_val,
                "SMA_50": latest['SMA_50'],
                "SMA_200": latest['SMA_200'],
                "Last_Price": latest['Close']
            }
        }

# --- Test Bloğu ---
if __name__ == "__main__":
    # Test için sahte veri üretelim veya market_data'yı çağıralım
    # Basitlik olsun diye market_data'yı import edip gerçek veriyle deneyelim
    import sys
    import os
    
    # Üst dizini path'e ekle (Test amaçlı)
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    from src.tools.market_data import MarketDataLoader

    loader = MarketDataLoader()
    df = loader.get_stock_price_history("THYAO.IS", period="1y")
    
    agent = TechnicalAgent()
    result = agent.analyze(df)
    
    print("\n--- TEKNİK ANALİST RAPORU ---")
    print(f"Sinyal: {result['signal']}")
    print(f"Skor: {result['score']}")
    print("Gerekçeler:")
    for r in result['analysis']:
        print(f"- {r}")
    