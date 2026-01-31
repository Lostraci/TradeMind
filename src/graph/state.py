from typing import TypedDict, List, Annotated
import operator

# Ajanların ürettiği mesajların formatı
class AgentState(TypedDict):
    ticker: str                # Analiz edilen hisse (örn: THYAO.IS)
    
    # Her ajanın raporu buraya eklenecek.
    # operator.add kullanmamızın sebebi: Her ajan buraya kendi verisini "append" etsin, üzerine yazmasın.
    technical_data: Annotated[dict, "Teknik Analiz Verisi"]
    fundamental_data: Annotated[dict, "Temel Analiz Verisi"]
    sentiment_data: Annotated[dict, "Haber/Sentiment Verisi"]
    quant_data: Annotated[dict, "Risk ve Pozisyon Analizi"]
    
    final_report: str          # Consensus ajanının yazacağı son rapor
    
    # Ajanların sırasını yönetmek için (Opsiyonel ama iyi pratik)
    next_step: str