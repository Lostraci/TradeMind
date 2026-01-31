from langgraph.graph import StateGraph, END
from src.graph.state import AgentState

# Senin oluşturduğun ajanları import ediyoruz
# EĞER ANTIGRAVITY SINIF İSİMLERİNİ FARKLI YAPTIYSA BURAYI DÜZELT
from src.agents.technical import TechnicalAgent
from src.agents.quant import QuantAgent
from src.agents.fundamental import FundamentalAgent
from src.agents.sentiment import SentimentAgent
from src.agents.consensus import ConsensusAgent
from src.tools.market_data import MarketDataLoader

# --- Node Fonksiyonları (Ajanları Çalıştıran Tetikleyiciler) ---

def run_technical(state: AgentState):
    print("--- TEKNİK ANALİST ÇALIŞIYOR ---")
    ticker = state["ticker"]
    
    # Veriyi çek
    loader = MarketDataLoader()
    df = loader.get_stock_price_history(ticker)
    
    # Analiz et
    agent = TechnicalAgent()
    result = agent.analyze(df)
    
    # State'i güncelle
    return {"technical_data": result}

def run_quant(state: AgentState):
    print("--- QUANT ANALİST (RİSK) ÇALIŞIYOR ---")
    ticker = state["ticker"]
    
    # Veriyi çek (Technical ile aynı veriyi kullanır)
    loader = MarketDataLoader()
    df = loader.get_stock_price_history(ticker)
    
    # Analiz et
    agent = QuantAgent()
    result = agent.analyze(df)
    
    return {"quant_data": result}

def run_fundamental(state: AgentState):
    print("--- TEMEL ANALİST ÇALIŞIYOR ---")
    ticker = state["ticker"]
    
    agent = FundamentalAgent()
    result = agent.analyze(ticker)
    
    return {"fundamental_data": result}

def run_sentiment(state: AgentState):
    print("--- SENTIMENT AJANI ÇALIŞIYOR ---")
    ticker = state["ticker"]
    
    agent = SentimentAgent()
    result = agent.analyze(ticker)
    
    return {"sentiment_data": result}

def run_consensus(state: AgentState):
    print("--- KONSENSÜS (YATIRIM KOMİTESİ) TOPLANIYOR ---")
    
    agent = ConsensusAgent()
    # Tüm veriler zaten state'in içinde, ajana state'i veriyoruz
    final_report = agent.synthesize(state)
    
    return {"final_report": final_report}

# --- Graph Yapısını Kurma ---

def create_graph():
    workflow = StateGraph(AgentState)

    # 1. Node'ları Ekle
    workflow.add_node("technical_node", run_technical)
    workflow.add_node("quant_node", run_quant)
    workflow.add_node("fundamental_node", run_fundamental)
    workflow.add_node("sentiment_node", run_sentiment)
    workflow.add_node("consensus_node", run_consensus)

    # 2. Bağlantıları (Edges) Kur
    # Başlangıç noktasını belirliyoruz.
    # Burada PARALEL çalışma yapabiliriz ama şimdilik garanti olsun diye sıralı yapalım,
    # Hata ayıklaması daha kolay olur.
    # Start -> Technical -> Fundamental -> Sentiment -> Consensus -> End
    
    workflow.set_entry_point("technical_node")
    
    workflow.add_edge("technical_node", "quant_node")
    workflow.add_edge("quant_node", "fundamental_node")
    workflow.add_edge("fundamental_node", "sentiment_node")
    workflow.add_edge("sentiment_node", "consensus_node")
    workflow.add_edge("consensus_node", END)

    return workflow.compile()