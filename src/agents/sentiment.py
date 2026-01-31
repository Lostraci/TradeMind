from typing import Dict, Any, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_community.tools import DuckDuckGoSearchRun, TavilySearchResults
import json
import os

class SentimentAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="models/gemini-flash-lite-latest", 
            temperature=0, 
            convert_system_message_to_human=True,
            google_api_key=os.environ["GOOGLE_API_KEY"]
        )
        
        # Check for Tavily API Key
        if os.environ.get("TAVILY_API_KEY"):
            self.search_tool = TavilySearchResults(max_results=5)
            self.using_tavily = True
        else:
            self.search_tool = DuckDuckGoSearchRun()
            self.using_tavily = False

    def get_news(self, ticker: str) -> List[str]:
        """
        Fetches recent news using Tavily or DuckDuckGo.
        """
        query = f"{ticker} stock news analysis financial"
        try:
            if self.using_tavily:
                results = self.search_tool.invoke({"query": query})
                # Tavily returns list of dicts with 'content'
                return [r.get("content", "") for r in results if r.get("content")]
            else:
                # DuckDuckGo returns a single string of results usually
                results = self.search_tool.invoke(query)
                return [results] # Wrap in list for consistency
        except Exception as e:
            print(f"Error fetching news for {ticker}: {e}")
            return []

    def analyze(self, ticker: str) -> Dict[str, Any]:
        """
        Analyzes the sentiment of recent news.
        Returns:
            {
                "signal": "POSITIVE" | "NEGATIVE" | "NEUTRAL",
                "sentiment_score": float (0.0 to 1.0),
                "news_summary": "..."
            }
        """
        news_items = self.get_news(ticker)
        
        if not news_items or (len(news_items) == 1 and not news_items[0]):
            return {
                "signal": "NEUTRAL",
                "sentiment_score": 0.5,
                "news_summary": "No recent news found."
            }

        news_text = "\n---\n".join(news_items)
        
        system_prompt = """Sen bir Finansal Duygu Analizi Uzmanısın (Financial Sentiment Analyst).
Hisse senedi için verilen haberleri analiz et.
Genel duygu durumunu ve güven skorunu belirle.
Önemli haber noktalarının kısa bir özetini yap.

Çıktı MUTLAKA şu formatta geçerli bir JSON olmalıdır:
- "signal": "POZİTİF", "NEGATİF" veya "NÖTR"
- "sentiment_score": 0.0 (Çok Negatif) ile 1.0 (Çok Pozitif) arasında bir sayı. 0.5 Nötrdür.
- "news_summary": Haberlerin Türkçe kısa bir özeti.
"""
        
        user_message = f"News for {ticker}:\n{news_text}"

        try:
            response = self.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_message)
            ])
            
            content = response.content
            if isinstance(content, list):
                content = "".join([str(x) for x in content])
            
            # Clean
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
                
            try:
                parsed = json.loads(content)
            except json.JSONDecodeError:
                import ast
                try:
                    parsed = ast.literal_eval(content)
                except:
                    print(f"Sentiment JSON Parse Error. Raw: {content}")
                    parsed = {}

            return {
                "signal": parsed.get("signal", "NÖTR").upper(),
                "sentiment_score": float(parsed.get("sentiment_score", 0.5)),
                "news_summary": parsed.get("news_summary", "Hata: Özet alınamadı.")
            }
            
        except Exception as e:
            return {
                "signal": "NÖTR",
                "sentiment_score": 0.5,
                "news_summary": f"Analiz hatası: {str(e)}"
            }

if __name__ == "__main__":
    try:
        agent = SentimentAgent()
        print("Running Sentiment Analysis for AAPL...")
        result = agent.analyze("AAPL")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(e)
