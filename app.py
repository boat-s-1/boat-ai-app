import streamlit as st

# ページ設定
st.set_page_config(page_title="BOAT STRIKE 新聞生成App", layout="wide")

# --- 1. サイドバー：データ入力 ---
st.sidebar.header("🏆 専門紙データ入力")

with st.sidebar.expander("一果 (本命)", expanded=True):
    i_bet = st.text_input("本線買い目", value="1-2-34", key="ichika_b")
    i_msg = st.text_input("短評", value="イン信頼度S。場平均を大きく上回る足色。逃げ鉄板。", key="ichika_m")

with st.sidebar.expander("初音 (客観)", expanded=True):
    h_bet = st.text_input("推奨買い目", value="1-4-全", key="hatsune_b")
    h_msg = st.text_input("短評", value="データ上は1-4が本線。オッズ乖離から期待値高い。", key="hatsune_m")

with st.sidebar.expander("キイナ (穴)", expanded=True):
    k_bet = st.text_input("爆穴買い目", value="5-全-全", key="kiina_b")
    k_msg = st.text_input("短評", value="4凹みなら5のまくり差し一閃。万舟への最短距離。", key="kiina_m")

# --- 2. メイン画面：新聞生成 ---
st.title("📰 BOAT STRIKE 専門紙・最終見解")

css_style = """
<style>
    .newspaper-board {
        background-color: #f4f1ea; /* 新聞紙のような少し黄色味のある白 */
        border: 4px double #333;
        padding: 0;
        font-family: "MS PMincho", "MS Mincho", serif; /* 新聞らしい明朝体風 */
        color: #1a1a1a;
    }
    .newspaper-header {
        background-color: #1a1a1a;
        color: #fff;
        text-align: center;
        padding: 5px 0;
        font-weight: bold;
        letter-spacing: 10px;
        font-size: 18px;
        border-bottom: 2px solid #1a1a1a;
    }
    .newspaper-container {
        display: flex !important;
        justify-content: space-between !important;
    }
    .char-card {
        flex: 1 !important;
        padding: 20px 10px;
        text-align: center !important;
        border-right: 1px dashed #666; /* 新聞の区切り線（点線） */
    }
    .char-card:last-child {
        border-right: none;
    }
    
    .yoso-mark {
        font-size: 50px;
        font-weight: 900;
        line-height: 1;
        margin-bottom: 5px;
        display: block;
    }
    .ichika-color { color: #d32f2f; }
    .hatsune-color { color: #1976d2; }
    .kiina-color { color: #f57c00; }
    
    .title-label { 
        font-size: 14px; 
        font-weight: bold; 
        border: 1px solid #1a1a1a;
        display: inline-block;
        padding: 2px 8px;
        margin-bottom: 15px;
    }
    
    .bet-display {
        background: transparent;
        color: #000;
        border: 3px solid #000;
        padding: 10px 0;
        font-size: 32px;
        font-weight: 900;
        margin: 10px 5px;
        font-family: "Arial Black", sans-serif;
    }
    
    .comment-box {
        font-size: 13px;
        text-align: left;
        padding: 0 10px;
        line-height: 1.6;
        height: 4.8em;
        overflow: hidden;
        border-top: 1px solid #ccc;
        padding-top: 10px;
    }
    .char-name-footer {
        font-size: 12px;
        font-weight: bold;
        margin-top: 10px;
        display: block;
        text-align: right;
    }
</style>
"""

content_html = f"""
<div class="newspaper-board">
    <div class="newspaper-header">最終ジャッジ</div>
    <div class="newspaper-container">
        <div class="char-card">
            <span class="yoso-mark ichika-color">◎</span>
            <div class="title-label">本命・一果</div>
            <div class="bet-display">{i_bet}</div>
            <div class="comment-box">
                {i_msg}
                <span class="char-name-footer">― 記者・一果</span>
            </div>
        </div>

        <div class="char-card">
            <span class="yoso-mark hatsune-color">○</span>
            <div class="title-label">対抗・初音</div>
            <div class="bet-display">{h_bet}</div>
            <div class="comment-box">
                {h_msg}
                <span class="char-name-footer">― 記者・初音</span>
            </div>
        </div>

        <div class="char-card">
            <span class="yoso-mark kiina-color">穴</span>
            <div class="title-label">特注・キイナ</div>
            <div class="bet-display">{k_bet}</div>
            <div class="comment-box">
                {k_msg}
                <span class="char-name-footer">― 記者・キイナ</span>
            </div>
        </div>
    </div>
</div>
"""

st.markdown(css_style, unsafe_allow_html=True)
st.markdown(content_html, unsafe_allow_html=True)

st.divider()
st.caption("※このセクションは画像保存してSNS投稿に使用することを想定しています。")
