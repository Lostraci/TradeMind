import yfinance as yf
import pandas_ta as ta
import pandas as pd
from typing import List

class MarketScanner:
    def __init__(self):
        # BIST 30 Majors + Growth/Tech/Energy Stocks
        self.tickers = [
            "THYAO.IS", "ASELS.IS", "GARAN.IS", "AKBNK.IS", "TUPRS.IS", 
            "KCHOL.IS", "SAHOL.IS", "EREGL.IS", "ISCTR.IS", "BIMAS.IS", 
            "SISE.IS", "PETKM.IS", "FROTO.IS", "YKBNK.IS", "HALKB.IS", 
            "EKGYO.IS", "TOASO.IS", "ARCLK.IS", "PGSUS.IS", "DOHOL.IS",
            # Growth / Volatile / Tech / Energy
            "MIAAT.IS", "REEDR.IS", "ASTOR.IS", "SMRTG.IS", "ALFAS.IS", 
            "KONTR.IS", "GESAN.IS", "EUPWR.IS", "YEOTK.IS", "CANTE.IS", 
            "QUAGR.IS", "HEKTS.IS", "SASA.IS", "ODAS.IS", "ZOREN.IS", 
            "BIOEN.IS", "PENTA.IS", "SDTTR.IS", "ONCSM.IS", "VBTYZ.IS", 
            "KMPUR.IS", "SMART.IS"
        ]

    def scan_market(self) -> List[str]:
        """
        Scans the market for Growth/Breakout opportunities.
        """
        scores = []
        print(f"Scanning {len(self.tickers)} stocks for Growth Opportunities...")
        
        for ticker in self.tickers:
            try:
                # Download last 1 month for speed (Breakout focus)
                # Need enough for RSI(14) and Vol MA(20). 1mo is ~22 days, barely enough.
                # Let's use "3mo" to be safe for 20-day MA and RSI calc stability.
                df = yf.download(ticker, period="3mo", progress=False)
                
                if df.empty or len(df) < 25:
                    continue

                # Flatten MultiIndex
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)

                # Indicators
                # RSI 14
                df['RSI'] = ta.rsi(df['Close'], length=14)
                # Volume MA 20
                df['Vol_MA20'] = ta.sma(df['Volume'], length=20)
                # ATR 14
                df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)
                
                # Check for NaNs in last row
                if df.iloc[-1][['RSI', 'Vol_MA20', 'ATR']].isnull().any():
                    continue

                last_close = df['Close'].iloc[-1]
                last_rsi = df['RSI'].iloc[-1]
                last_vol = df['Volume'].iloc[-1]
                last_vol_ma = df['Vol_MA20'].iloc[-1]
                last_atr = df['ATR'].iloc[-1]
                
                # Price Performance (5 days)
                # Check if we have enough data for 5 days ago
                if len(df) >= 6:
                    price_5d_ago = df['Close'].iloc[-6]
                    perf_5d = ((last_close - price_5d_ago) / price_5d_ago) * 100
                else:
                    perf_5d = 0

                # --- GROWTH SCORING LOGIC ---
                score = 0
                
                # 1. Volume Breakout (+3)
                # Today's volume > 1.5x Average Volume
                if last_vol > (1.5 * last_vol_ma):
                    score += 3
                
                # 2. Momentum (+2)
                # RSI between 50 and 70 (Strong but not Overbought)
                if 50 < last_rsi < 70:
                    score += 2
                    
                # 3. Price Performance (+1)
                # Up > 3% in last 5 days
                if perf_5d > 3.0:
                    score += 1
                    
                # 4. Volatility / ATR (+1)
                # Normalized ATR (ATR/Price) > 2% implies good volatility for trading
                atr_pct = (last_atr / last_close) * 100
                if atr_pct > 2.0:
                    score += 1

                scores.append({
                    "ticker": ticker,
                    "score": score,
                    "rsi": last_rsi,
                    "vol_ratio": round(last_vol / last_vol_ma, 1) if last_vol_ma > 0 else 0,
                    "perf_5d": round(perf_5d, 1)
                })

            except Exception as e:
                pass # Skip errors silently for speed

        # Sort by Score (Descending)
        scores.sort(key=lambda x: x["score"], reverse=True)
        
        print("\n--- TOP GROWTH PICKS ---")
        for s in scores[:5]:
            print(f"{s['ticker']}: Score {s['score']} (RSI: {s['rsi']:.1f}, Vol Ratio: {s['vol_ratio']}x)")

        # Return top 3 tickers
        top_3 = [s["ticker"] for s in scores[:3]]
        return top_3

if __name__ == "__main__":
    scanner = MarketScanner()
    top_stocks = scanner.scan_market()
    print(f"\nRecommended Stocks: {top_stocks}")
