from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
import json
import sys
import os

# Function provided by user context for proper pathing if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

try:
    from src.graph.state import AgentState
except ImportError:
    # Fallback for type hinting
    AgentState = Dict[str, Any]

class ConsensusAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="models/gemini-flash-lite-latest", 
            temperature=0, 
            convert_system_message_to_human=True,
            google_api_key=os.environ["GOOGLE_API_KEY"]
        )

    def synthesize(self, state: AgentState) -> str:
        """
        Synthesizes reports from Technical, Fundamental, and Sentiment agents.
        Returns the final Investment Committee Report as a string.
        """
        
        ticker = state.get("ticker", "Unknown Ticker")
        technical = state.get("technical_data", {})
        fundamental = state.get("fundamental_data", {})
        sentiment = state.get("sentiment_data", {})
        quant = state.get("quant_data", {})

        # Prepare context for the LLM
        context_str = f"""
        TICKER: {ticker}

        --- TECHNICAL ANALYSIS ---
        Signal: {technical.get('signal', 'N/A')}
        Score: {technical.get('score', 'N/A')}
        Details: {technical.get('analysis', 'N/A')}
        Metrics: {technical.get('metrics', 'N/A')}

        --- FUNDAMENTAL ANALYSIS ---
        Signal: {fundamental.get('signal', 'N/A')}
        Reason: {fundamental.get('reason', 'N/A')}
        Metrics: {json.dumps(fundamental.get('metrics', {}), indent=2)}

        --- SENTIMENT ANALYSIS ---
        Signal: {sentiment.get('signal', 'N/A')}
        Score: {sentiment.get('sentiment_score', 'N/A')}
        Summary: {sentiment.get('news_summary', 'N/A')}

        --- QUANT RISK ANALYSIS ---
        Signal: {quant.get('signal', 'N/A')}
        Stop Loss: {quant.get('stop_loss', 'N/A')}
        Take Profit: {quant.get('take_profit', 'N/A')}
        Max Allocation: {quant.get('max_portfolio_allocation', 'N/A')}
        Metrics: {json.dumps(quant, indent=2)}
        """
        
        system_prompt = """You are managing a High-Risk/High-Reward 'Alpha Fund'. Your goal is to find the next 10x stock. Tolerate volatility. If Technicals show a volume breakout and Fundamentals show a growth story, recommend a BUY with a 'High Risk' tag. Do not recommend 'Safe/Boring' stocks.

Aşağıdaki analist raporlarını (Teknik, Temel, Duygu, Kantitatif) incele.
Bunları sentezleyerek Nihai Yatırım Raporunu TÜRKÇE olarak oluştur.

Rapor şu bölümlerden oluşmalıdır:
1. **YATIRIM KOMİTESİ KARARI**: Nihai karar (GÜÇLÜ AL, AL, TUT, SAT, GÜÇLÜ SAT) ve bir cümlelik gerekçe.
2. **Analiz Özeti**: Teknik, Temel, Duygu ve Kantitatif verilerin nasıl hizalandığı.
3. **Ticaret Planı**:
   - Giriş Seviyesi (Mevcut fiyat veya uygun bir seviye)
   - Stop-Loss (Kantitatif veriden al)
   - Kar Al (Take-Profit) (Kantitatif veriden al)
   - Önerilen Pozisyon Büyüklüğü (Maksimum portföy payı)
4. **Riskler**: Dikkate alınması gereken temel risk faktörleri.

Çıktıyı temiz Markdown formatında ver.
"""

        user_message = f"Here is the data for {ticker}:\n{context_str}\n\nGenerate the Investment Committee Report."

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]

        try:
            response = self.llm.invoke(messages)
            content = response.content
            if isinstance(content, list):
                content = "".join([str(x) for x in content])
            return content
        except Exception as e:
            return f"Error generating report: {str(e)}"

# --- Test Block ---
if __name__ == "__main__":
    # Mock data for testing
    mock_state = {
        "ticker": "TEST",
        "technical_data": {
            "signal": "BUY",
            "score": 4,
            "analysis": ["RSI is low", "Golden Cross"],
            "metrics": {"RSI": 35}
        },
        "fundamental_data": {
            "signal": "HOLD",
            "reason": "Stable but slow growth.",
            "metrics": {"PE": 15}
        },
        "sentiment_data": {
            "signal": "POSITIVE",
            "sentiment_score": 0.8,
            "news_summary": "CEO just bought shares."
        },
        "quant_data": {
            "signal": "Safe",
            "stop_loss": 145.50,
            "take_profit": 165.00,
            "max_portfolio_allocation": "High (max 15%)"
        }
    }
    
    try:
        agent = ConsensusAgent()
        print("Running Consensus Agent...")
        report = agent.synthesize(mock_state)
        print("\n" + "="*40)
        print(report)
        print("="*40)
    except Exception as e:
        print(f"Test failed: {e}")
