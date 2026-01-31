import yfinance as yf
import pandas as pd
from typing import Dict, Any, Optional

class MarketDataLoader:
    def __init__(self):
        """
        Borsa verilerini çekmek için wrapper sınıf.
        """
        pass

    def get_stock_price_history(self, ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """
        Geçmiş fiyat verilerini çeker (OHLCV).
        Teknik analiz ajanı bunu kullanacak.
        """
        print(f"DEBUG: {ticker} için fiyat verisi çekiliyor...")
        try:
            stock = yf.Ticker(ticker)
            # auto_adjust=True temettü/bölünme düzeltmelerini yapar, önemlidir.
            df = stock.history(period=period, interval=interval, auto_adjust=True)
            
            if df.empty:
                raise ValueError(f"{ticker} için veri bulunamadı.")
            
            return df
        except Exception as e:
            print(f"HATA: Fiyat verisi çekilemedi -> {e}")
            return pd.DataFrame()

    def get_fundamental_info(self, ticker: str) -> Dict[str, Any]:
        """
        Temel analiz verilerini (P/E, Market Cap, Sektör vb.) çeker.
        Fundamental ajanı bunu kullanacak.
        """
        print(f"DEBUG: {ticker} için temel veriler çekiliyor...")
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # LLM'e tüm info'yu (yüzlerce satır) verirsek token israfı olur.
            # Sadece kritik olanları filtreleyelim.
            key_metrics = {
                "symbol": info.get("symbol"),
                "shortName": info.get("shortName"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "marketCap": info.get("marketCap"),
                "trailingPE": info.get("trailingPE"),       # F/K Oranı
                "forwardPE": info.get("forwardPE"),         # Gelecek F/K
                "priceToBook": info.get("priceToBook"),     # PD/DD
                "profitMargins": info.get("profitMargins"),
                "revenueGrowth": info.get("revenueGrowth"),
                "returnOnEquity": info.get("returnOnEquity"), # Özsermaye Karlılığı
                "currentPrice": info.get("currentPrice"),
                "targetMeanPrice": info.get("targetMeanPrice"), # Analist hedef fiyat ortalaması
                "recommendationKey": info.get("recommendationKey") # 'buy', 'hold' vb.
            }
            return key_metrics
        except Exception as e:
            print(f"HATA: Temel veriler çekilemedi -> {e}")
            return {}

# Test Bloğu (Sadece bu dosyayı çalıştırırsan burası çalışır)
if __name__ == "__main__":
    loader = MarketDataLoader()
    
    # BIST hissesi denerken sonuna .IS eklemeyi unutma (yfinance kuralı)
    ticker_symbol = "THYAO.IS" 
    
    # 1. Fiyat Testi
    history = loader.get_stock_price_history(ticker_symbol, period="1mo")
    print(f"\n--- {ticker_symbol} Son 5 Günlük Fiyat ---")
    print(history.tail())

    # 2. Temel Analiz Testi
    fundamentals = loader.get_fundamental_info(ticker_symbol)
    print(f"\n--- {ticker_symbol} Temel Veriler ---")
    for k, v in fundamentals.items():
        print(f"{k}: {v}")