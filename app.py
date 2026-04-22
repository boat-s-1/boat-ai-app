import streamlit as st

# ページ設定
st.set_page_config(page_title="BOAT STRIKE 新聞生成App", layout="wide")

# --- 1. サイドバー：データ入力 ---
st.sidebar.header("🏆 予想データ入力")

with st.sidebar.expander("一果 (本命)", expanded=True):
    i_bet = st.text_input("買い目", value="1-2-34", key="ichika_b")
    i_msg = st.text_input("一言", value="場平均より+22%も高いよ！ここは一果を信じて鬼絞りっ！", key="ichika_m")

with st.sidebar.expander("初音 (客観)", expanded=True):
    h_bet = st.text_input("買い目", value="1-4-全", key="hatsune_b")
    h_msg = st.text_input("一言", value="補正展示タイムから算出。オッズの歪みを含めるとこの目が合理的です。", key="hatsune_m")

with st.sidebar.expander("キイナ (穴)", expanded=True):
    k_bet = st.text_input("買い目", value="5-全-全", key="kiina_b")
    k_msg = st.text_input("一言", value="4が凹めば5のまくり差しが炸裂するっしょ！買わなきゃ損だよ！", key="kiina_m")

# --- 2. メイン画面：新聞生成 ---
st.title("📰 BOAT STRIKE 最終予想セクション")
st.write("プレビュー画面（このまま画像出力が可能です）")

# 全体のHTMLとCSSを一つの変数にまとめます
final_ui_html = f"""
<style>
    .newspaper-container {{
        display: flex;
        justify-content: space-between;
        gap: 15px;
        background-color: #f1f5f9;
        padding: 20px;
        border: 2px solid #1e293b;
        border-radius: 15px;
    }}
    .char-card {{
        flex: 1;
        background: white;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-top: 8px solid;
    }}
    .ichika-border {{ border-top-color: #ef4444; }}
    .hatsune-border {{ border-top-color: #3b82f6; }}
    .kiina-border {{ border-top-color: #f59e0b; }}
    
    .char-icon {{
        width: 70px; height: 70px;
        border: 2px solid #cbd5e1;
        border-radius: 50%;
        margin: 0 auto 10px;
        display: flex; align-items: center; justify-content: center;
        background: #f8fafc;
        font-weight: bold; font-size: 14px;
    }}
    .title-label {{ font-weight: bold; font-size: 16px; margin-bottom: 10px; }}
    .bet-display {{
        background: #1e293b;
        color: white;
        padding: 12px 5px;
        font-size: 24px;
        font-weight: bold;
        border-radius: 6px;
        margin: 10px 0;
        letter-spacing: 2px;
    }}
    .comment-text {{ font-size: 12px; color: #475569; line-height: 1.4; min-height: 3em; }}
</style>

<div class="newspaper-container">
    <div class="char-card ichika-border">
        <div class="char-icon" style="color:#ef4444; border-color:#ef4444;">一果</div>
        <div class="title-label" style="color:#ef4444;">一果のズバリ！</div>
        <div class="bet-display">{i_bet}</div>
        <div class="comment-text">「{i_m}」</div>
    </div>

    <div class="char-card hatsune-border">
        <div class="char-icon" style="color:#3b82f6; border-color:#3b82f6;">初音</div>
        <div class="title-label" style="color:#3b82f6;">初音の客観数値</div>
        <div class="bet-display">{h_bet}</div>
        <div class="comment-text">「{h_m}」</div>
    </div>

    <div class="char-card kiina-border">
        <div class="char-icon" style="color:#f59e0b; border-color:#f59e0b;">キイナ</div>
        <div class="title-label" style="color:#f59e0b;">キイナの穴狙い！</div>
        <div class="bet-display">{k_bet}</div>
        <div class="comment-text">「{k_m}」</div>
    </div>
</div>
"""

# unsafe_allow_html=True を指定して一気に描画
st.markdown(final_ui_html, unsafe_allow_html=True)

st.divider()
st.info("💡 サイドバーの値を書き換えると、上のプレビューがリアルタイムに更新されます。")
