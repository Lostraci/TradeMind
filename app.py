import streamlit as st
from dotenv import load_dotenv
import pandas as pd
import plotly.graph_objects as go
import pandas_ta as ta
import ast 
import time

# Kendi modüllerimiz
from src.tools.database import TradeMemory
from src.graph.workflow import create_graph
from src.tools.scanner import MarketScanner
from src.tools.market_data import MarketDataLoader

# .env yükle
load_dotenv()

# --- Sayfa Ayarları ---
st.set_page_config(
    page_title="TradeMind AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS (KOYU TEMA DOSTU TASARIM) ---
st.markdown("""
    <style>
    /* Metrik Kutularını Düzenle */
    div[data-testid="stMetric"] {
        background-color: rgba(28, 28, 28, 0.5); /* Yarı saydam koyu arka plan */
        border: 1px solid #333; /* İnce koyu kenarlık */
        padding: 15px;
        border-radius: 10px;
        color: #ffffff; /* Yazılar Beyaz */
    }
    
    /* Etiket Rengini (Giriş, Hedef vb.) Açık Gri Yap */
    div[data-testid="stMetricLabel"] {
        color: #b2b2b2 !important;
    }

    /* Değer Rengini (Fiyatlar) Parlak Beyaz Yap */
    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Grafik Fonksiyonu ---
def plot_chart(ticker, df, quant_data=None):
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Fiyat'))
    if 'SMA_50' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], line=dict(color='orange', width=1), name='SMA 50'))
    if 'SMA_200' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_200'], line=dict(color='red', width=2), name='SMA 200'))
    
    if quant_data:
        try:
            sl = quant_data.get("stop_loss")
            tp = quant_data.get("take_profit")
            if sl: fig.add_hline(y=sl, line_dash="dash", line_color="red", annotation_text=f"Stop Loss: {sl:.2f}")
            if tp: fig.add_hline(y=tp, line_dash="dash", line_color="green", annotation_text=f"Hedef: {tp:.2f}")
        except: pass

    fig.update_layout(title=f"{ticker} Teknik Grafik", yaxis_title="Fiyat (TL)", xaxis_rangeslider_visible=False, height=500, template="plotly_dark")
    return fig

# --- Rapor Temizleme ---
def render_report(final_rep):
    text_content = ""
    if isinstance(final_rep, list) and len(final_rep) > 0:
        first_item = final_rep[0]
        if isinstance(first_item, dict) and 'text' in first_item:
            text_content = first_item['text']
        else:
            text_content = str(first_item)
    else:
        text_content = str(final_rep)
    st.markdown(text_content)

# --- Veritabanı Kayıt Yardımcısı ---
def save_to_db(ticker, result):
    try:
        memory = TradeMemory()
        q_data = result.get("quant_data", {})
        signal = q_data.get("signal", "N/A")
        
        memory.save_analysis(
            ticker=ticker,
            signal=signal,
            entry=q_data.get("entry_price", 0),
            target=q_data.get("take_profit", 0),
            stop=q_data.get("stop_loss", 0),
            risk="Alpha/High Risk",
            full_report=result.get("final_report", "No Report")
        )
    except Exception as e:
        st.error(f"DB Kayıt Hatası: {e}")

# --- Yan Menü ---
st.sidebar.title("🧠 TradeMind AI")
st.sidebar.markdown("---")
mode = st.sidebar.radio("Mod Seçimi", ["Tek Hisse Analizi", "Otomatik Piyasa Tarama", "📊 Geçmiş Analizler"])
st.sidebar.markdown("---")
st.sidebar.info("Alpha Fonu Modu Aktif.\n(Yüksek Risk / Yüksek Getiri)")

# --- AKIŞ ---

# 1. MOD: TEK HİSSE
if mode == "Tek Hisse Analizi":
    st.title("🔎 Detaylı Hisse Analizi (Alpha Mode)")
    col1, col2 = st.columns([3, 1])
    with col1:
        ticker_input = st.text_input("Hisse Kodu (Örn: REEDR.IS, ASTOR.IS)", "THYAO.IS").upper()
    with col2:
        st.write("")
        st.write("")
        analyze_btn = st.button("Analiz Et 🚀", type="primary")

    if analyze_btn:
        with st.status("Yapay zeka analiz ediyor...", expanded=True) as status:
            try:
                app = create_graph()
                initial_state = {"ticker": ticker_input, "technical_data": {}, "fundamental_data": {}, "sentiment_data": {}, "quant_data": {}, "final_report": ""}
                
                st.write("📡 Veriler çekiliyor ve işleniyor...")
                result = app.invoke(initial_state)
                
                # --- KAYIT ---
                save_to_db(ticker_input, result)
                
                status.update(label="Analiz Tamamlandı!", state="complete", expanded=False)
                
                # --- GÖSTERİM ---
                q_data = result.get("quant_data", {})
                if q_data:
                    c1, c2, c3, c4 = st.columns(4)
                    entry = q_data.get('entry_price', 0)
                    tp = q_data.get('take_profit', 0)
                    sl = q_data.get('stop_loss', 0)
                    c1.metric("Giriş", f"{entry:.2f} TL" if entry else "-")
                    c2.metric("Hedef", f"{tp:.2f} TL" if tp else "-", delta_color="normal")
                    c3.metric("Stop", f"{sl:.2f} TL" if sl else "-", delta_color="inverse")
                    c4.metric("Risk", q_data.get("signal", "-"))

                tab1, tab2, tab3 = st.tabs(["📝 Rapor", "📈 Grafik", "🤖 Detaylar"])
                with tab1: render_report(result["final_report"])
                with tab2:
                    loader = MarketDataLoader()
                    df = loader.get_stock_price_history(ticker_input)
                    if not df.empty:
                        df['SMA_50'] = ta.sma(df['Close'], length=50)
                        df['SMA_200'] = ta.sma(df['Close'], length=200)
                        fig = plot_chart(ticker_input, df, q_data)
                        st.plotly_chart(fig)
                with tab3:
                    with st.expander("Teknik"): st.json(result.get("technical_data"))
                    with st.expander("Temel"): st.json(result.get("fundamental_data"))
                    with st.expander("Sentiment"): st.json(result.get("sentiment_data"))
            except Exception as e:
                st.error(f"Hata: {e}")

# 2. MOD: SCANNER
elif mode == "Otomatik Piyasa Tarama":
    st.title("🚀 Büyüme Hissesi Tarayıcısı (Growth Hunter)")
    st.write("Yüksek hacim, güçlü momentum ve büyüme hikayesi olan hisseleri tarar.")
    
    if st.button("Taramayı Başlat 🕵️‍♂️"):
        try:
            scanner = MarketScanner()
            with st.spinner("Piyasa taranıyor... (Bu işlem 1-2 dk sürebilir)"):
                top_picks = scanner.scan_market()
            
            if not top_picks:
                st.warning("Kriterlere uyan hisse bulunamadı.")
            else:
                st.success(f"Fırsat Adayları: {', '.join(top_picks)}")
                app = create_graph()
                
                for stock in top_picks:
                    st.divider()
                    st.subheader(f"Analiz: {stock}")
                    time.sleep(3) # Kota dostu bekleme
                    
                    with st.status(f"{stock} inceleniyor...", expanded=False) as status:
                        initial_state = {"ticker": stock, "technical_data": {}, "fundamental_data": {}, "sentiment_data": {}, "quant_data": {}, "final_report": ""}
                        try:
                            result = app.invoke(initial_state)
                            
                            # --- KAYIT ---
                            save_to_db(stock, result)
                            
                            status.update(label="Tamamlandı", state="complete")
                            with st.expander(f"📄 {stock} Raporunu Oku", expanded=True):
                                render_report(result["final_report"])
                        except Exception as e:
                            st.error(f"Hata ({stock}): {e}")
        except Exception as e:
            st.error(f"Tarayıcı Hatası: {e}")

# 3. MOD: GEÇMİŞ
elif mode == "📊 Geçmiş Analizler":
    st.title("📜 Analiz Hafızası")
    
    try:
        memory = TradeMemory()
        df_history = memory.get_history()
        
        if not df_history.empty:
            # Full Report'u ana tabloda gizle
            display_cols = [c for c in df_history.columns if c != "full_report"]
            
            event = st.dataframe(
                df_history[display_cols],
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row"
            )
            
            # Seçilen satırı yakala
            if len(event.selection.rows) > 0:
                selected_index = event.selection.rows[0]
                selected_row = df_history.iloc[selected_index]
                
                st.divider()
                st.subheader(f"🔍 Detay: {selected_row['ticker']} ({selected_row['date']})")
                
                # Metrikleri Göster
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Giriş", f"{selected_row['entry_price']:.2f}" if selected_row['entry_price'] else "-")
                c2.metric("Hedef", f"{selected_row['target_price']:.2f}" if selected_row['target_price'] else "-")
                c3.metric("Stop", f"{selected_row['stop_loss']:.2f}" if selected_row['stop_loss'] else "-")
                c4.metric("Risk", selected_row['risk_level'] if selected_row['risk_level'] else "-")
                
                # Raporu Göster
                st.markdown("### 📝 Analiz Raporu")
                with st.container(border=True):
                    render_report(selected_row['full_report'])
                
        else:
            st.info("Henüz veritabanında kayıtlı analiz yok. Bir analiz yapın!")
    except Exception as e:
        st.error(f"Veritabanı okuma hatası: {e}")