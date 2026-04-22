import streamlit as st

# --- レイアウト設定 ---
st.set_page_config(layout="wide")

st.title("📄 BOAT STRIKE 予想新聞生成システム")

# --- サイドバー：データ入力 ---
with st.sidebar:
    st.header("📊 レースデータ入力")
    race_place = st.selectbox("開催場", ["住之江", "平和島", "戸田", "大村"])
    race_num = st.number_input("レース番号", 1, 12, 11)
    
    st.divider()
    st.subheader("💡 3人の買い目入力")
    ichika_bet = st.text_input("一果（本命）", "1-2-34")
    hatsune_bet = st.text_input("初音（効率）", "1-4-全")
    kiina_bet = st.text_input("キイナ（穴）", "5-全-全")

# --- メイン：新聞プレビュー ---
st.subheader("🖼 プレビュー（このまま画像出力）")

# HTML/CSSで3人並びのセクションを作成
newspaper_html = f"""
<style>
    .newspaper-footer {{
        display: flex;
        gap: 20px;
        background-color: #f8fafc;
        padding: 20px;
        border: 3px solid #1e293b;
        border-radius: 15px;
    }}
    .char-card {{
        flex: 1;
        background: white;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-top: 8px solid;
    }}
    .ichika-border {{ border-top-color: #ef4444; }}
    .hatsune-border {{ border-top-color: #3b82f6; }}
    .kiina-border {{ border-top-color: #f59e0b; }}
    
    .char-name {{ font-weight: bold; margin-bottom: 10px; font-size: 18px; }}
    .bet-display {{
        background: #1e293b;
        color: #fff;
        padding: 10px;
        font-size: 24px;
        font-weight: bold;
        border-radius: 5px;
        letter-spacing: 2px;
    }}
    .char-icon {{
        width: 80px; height: 80px;
        background: #eee; border-radius: 50%;
        margin: 0 auto 10px;
        display: flex; align-items: center; justify-content: center;
        font-size: 12px; color: #666;
    }}
</style>

<div class="newspaper-footer">
    <div class="char-card ichika-border">
        <div class="char-icon">一果<br>ICON</div>
        <div class="char-name" style="color:#ef4444;">一果のズバリ！</div>
        <div class="bet-display">{ichika_bet}</div>
        <p style="font-size:12px; margin-top:10px;">「ここは逃げ鉄板だよ！」</p>
    </div>
    
    <div class="char-card hatsune-border">
        <div class="char-icon">初音<br>ICON</div>
        <div class="char-name" style="color:#3b82f6;">初音の客観</div>
        <div class="bet-display">{hatsune_bet}</div>
        <p style="font-size:12px; margin-top:10px;">「期待値はこの目が最大です。」</p>
    </div>
    
    <div class="char-card kiina-border">
        <div class="char-icon">キイナ<br>ICON</div>
        <div class="char-name" style="color:#f59e0b;">キイナの穴</div>
        <div class="bet-display">{kiina_bet}</div>
        <p style="font-size:12px; margin-top:10px;">「一撃狙うならこれっしょ！」</p>
    </div>
</div>
"""

st.markdown(newspaper_html, unsafe_allow_html=True)

st.divider()
if st.button("📸 予想新聞を画像として保存"):
    st.info("ここにHTMLを画像に変換するロジック（playwright等）を組み込みます。")
