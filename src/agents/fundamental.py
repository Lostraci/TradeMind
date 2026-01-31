from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
import json
import os
# MarketDataLoader importu senin klasör yapına göre:
from src.tools.market_data import MarketDataLoader

class FundamentalAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="models/gemini-flash-lite-latest", 
            temperature=0, 
            convert_system_message_to_human=True,
            google_api_key=os.environ["GOOGLE_API_KEY"]
        )
        self.loader = MarketDataLoader()

    def analyze(self, ticker: str) -> Dict[str, Any]:
        """
        Temel verileri çeker ve Gemini ile yorumlar.
        """
        # 1. Veriyi Çek
        raw_data = self.loader.get_fundamental_info(ticker)
        
        if not raw_data:
            return {"signal": "HOLD", "reason": "Veri çekilemedi.", "metrics": {}}

        # 2. Prompt Hazırla
        # 2. Prompt Hazırla
        system_msg = SystemMessage(content="You are a Venture Capitalist looking for aggressive growth stocks. Do not be scared of high P/E ratios if the growth story is strong. Focus on sector hype, future expectations, and aggressive expansion. If metrics are risky but potential is huge, signal BUY. Cevaplarını Türkçe ver.")
        
        user_prompt = f"""
        Şirket: {ticker}
        Veriler: {json.dumps(raw_data, indent=2)}
        
        Bu verileri analiz et. F/K oranı, marjlar ve büyüme potansiyeline odaklan.
        Çıktıyı SADECE geçerli bir JSON formatında ver:
        {{
            "signal": "AL" veya "TUT" veya "SAT",
            "reason": "Kısa ve öz bir açıklama (Türkçe, Max 2 cümle)",
            "metrics": {{ "PE": "...", "ROE": "..." }}
        }}
        """
        
        # 3. Modelden Cevap Al
        # 3. Modelden Cevap Al
        try:
            response = self.llm.invoke([system_msg, HumanMessage(content=user_prompt)])
            content = response.content
            if isinstance(content, list):
                content = "".join([str(x) for x in content])
            
            # Clean Markdown
            content = content.replace("```json", "").replace("```", "").strip()
            
            # Try parsing
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Fallback: Try ast.literal_eval for single quotes
                import ast
                try:
                    return ast.literal_eval(content)
                except:
                    print(f"JSON Parsing Failed. Raw: {content}")
                    return {
                        "signal": "TUT",
                        "reason": "Veri formatı hatası (JSON parse edilemedi).",
                        "metrics": raw_data
                    }
        except Exception as e:
            print(f"Fundamental Agent Error: {e}")
            return {
                "signal": "TUT",
                "reason": f"Analiz hatası: {str(e)}",
                "metrics": raw_data
            }

if __name__ == "__main__":
    # Test block
    try:
        agent = FundamentalAgent()
        print("Running Fundamental Analysis for THYAO.IS...")
        result = agent.analyze("THYAO.IS")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(e)
