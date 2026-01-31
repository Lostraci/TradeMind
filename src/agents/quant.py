import pandas as pd
import numpy as np
from typing import Dict, Any

class QuantAgent:
    def __init__(self):
        pass

    def analyze(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Performs quantitative risk analysis using technical indicators.
        Expected columns in df: 'High', 'Low', 'Close'
        """
        if df is None or df.empty:
            return {
                "signal": "UNKNOWN",
                "error": "Empty or None DataFrame provided"
            }
        
        # Ensure sufficient data for 14-period ATR
        if len(df) < 15:
            return {
                "signal": "UNKNOWN",
                "reason": "Insufficient data for ATR calculation (need > 14 periods)"
            }

        # Work on a copy to avoid modifying original df
        data = df.copy()
        
        # --- 1. Calculate ATR (Average True Range) Period 14 ---
        # TR = max(High - Low, |High - PrevClose|, |Low - PrevClose|)
        data['H-L'] = data['High'] - data['Low']
        data['H-PC'] = abs(data['High'] - data['Close'].shift(1))
        data['L-PC'] = abs(data['Low'] - data['Close'].shift(1))
        
        data['TR'] = data[['H-L', 'H-PC', 'L-PC']].max(axis=1)
        
        # Simple Moving Average for ATR (common variation)
        # Note: Some implementations use Wilder's Smoothing, but SMA is specified as acceptable via "manual calculation" implying standard rolling.
        # We will use Wilder's smoothing method as it is standard for ATR.
        # ATR = (PrevATR * (n-1) + CurrentTR) / n
        # Or simply rolling mean for simplicity if not strictly specified. I will use simple rolling mean for robustness and simplicity.
        data['ATR'] = data['TR'].rolling(window=14).mean()
        
        current_atr = data['ATR'].iloc[-1]
        
        # --- 2. Calculate Volatility ---
        # Standard deviation of daily returns
        data['Returns'] = data['Close'].pct_change()
        # Using a rolling window for volatility (e.g., 20 days) or full series? 
        # Requirement says "Volatility (Standard Deviation of returns)". I will use the std of the last 20 periods to be relevant.
        volatility = data['Returns'].rolling(window=20).std().iloc[-1]
        
        # If NaN (e.g. not enough data), fallback to full series std
        if np.isnan(volatility):
            volatility = data['Returns'].std()
            
        # Convert to percentage for easy comparison
        volatility_pct = volatility * 100

        # --- 3. Determine Risk Levels ---
        current_price = data['Close'].iloc[-1]
        stop_loss = current_price - (2 * current_atr)
        take_profit = current_price + (4 * current_atr)
        
        # --- 4. Portfolio Allocation and Signal ---
        if volatility_pct > 3.0:
            allocation = "Low (max 5%)"
            signal = "Risky"
        elif volatility_pct < 1.5:
            allocation = "High (max 15%)"
            signal = "Safe"
        else:
            allocation = "Medium (max 10%)"
            signal = "Moderate"

        return {
            "signal": signal,
            "current_price": round(current_price, 2),
            "atr": round(current_atr, 4),
            "volatility_daily_pct": round(volatility_pct, 2),
            "stop_loss": round(stop_loss, 2),
            "take_profit": round(take_profit, 2),
            "max_portfolio_allocation": allocation
        }

if __name__ == "__main__":
    # Test Block with mock data
    print("Running QuantAgent Test...")
    
    # Create dummy data
    dates = pd.date_range(start="2023-01-01", periods=50)
    prices = [100 + i + (np.random.random() * 5) for i in range(50)] # Uptrend with noise
    
    df_mock = pd.DataFrame({
        "Date": dates,
        "Open": prices,
        "High": [p + 2 for p in prices],
        "Low": [p - 2 for p in prices],
        "Close": [p + 1 for p in prices],
        "Volume": [1000 for _ in range(50)]
    })
    
    agent = QuantAgent()
    result = agent.analyze(df_mock)
    
    import json
    print(json.dumps(result, indent=2))
