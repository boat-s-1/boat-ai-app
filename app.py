import streamlit as st

# 1. ページ設定
st.set_page_config(page_title="BOAT STRIKE 専門紙生成", layout="wide")

# 2. サイドバー：入力（専門紙らしい「短評」スタイル）
st.sidebar.header("📝 記者・最終ジャッジ")

with st.sidebar.expander("◎ 一果 (本命)", expanded=True):
    i_bet = st.text_input("本線", value="1-2-34", key="ichika_b")
    i_msg = st.text_area("短評", value="場平均+22%の期待値。機力・気配ともに他を圧倒。逃げ鉄板とみる。", key="ichika_m")

with st.sidebar.expander("○ 初音 (対抗)", expanded=True):
    h_bet = st.text_input("推奨", value="1-4-全", key="hatsune_b")
    h_msg = st.text_area("短評", value="データ上は1-4。オッズ乖離を考慮すれば、ここが最大の回収ポイント。", key="hatsune_m")

with st.sidebar.expander("穴 キイナ (穴)", expanded=True):
    k_bet = st.text_input("一撃", value="5-全-全", key="kiina_b")
    k_msg = st.text_area("短評", value="4凹みなら5のまくり差しが炸裂。配当妙味は十分。万舟の最短距離。", key="kiina_m")

# 3. メイン画面：新聞プレビュー
st.title("📰 BOAT STRIKE 専門紙・最終見解")

# 【重要】CSSをf-stringの外に出すことで波括弧のバグを完全に防ぎます
css_style = """
<style>
    .newspaper-board {
        background-color: #f4f1ea; /* 新聞紙特有の色味 */
        border: 4px double #333;
        font-family: serif;
        color: #1a1a1a;
        width: 100%;
    }
    .newspaper-header {
        background-color: #1a1a1a;
        color: #fff;
        text-align: center;
        padding: 8px 0;
        font-weight: bold;
        letter-spacing: 12px;
        font-size: 20px;
    }
    .newspaper-container {
        display: flex !important;
        width: 100%;
    }
    .char-card {
        flex: 1 !important;
        padding: 25px 15px;
        text-align: center !important;
        border-right: 1px dashed #666; /* 新聞の点線区切り */
    }
    .char-card:last-child { border-right: none; }
    
    .yoso-mark {
        font-size: 55px;
        font-weight: 900;
        line-height: 1;
        margin-bottom: 8px;
        display: block;
    }
    .ichika-c { color: #d32f2f; }
    .hatsune-c { color: #1976d2; }
    .kiina-c { color: #f57c00; }
    
    .title-label { 
        font-size: 15px; font-weight: bold; 
        border: 1px solid #1a1a1a;
        padding: 2px 10px; margin-bottom: 20px;
        display: inline-block;
    }
    .bet-display {
        border: 4px solid #000;
        padding: 12px 0;
        font-size: 36px;
        font-weight: 900;
        margin: 15px 5px;
        background: #fff;
    }
    .comment-box {
        font-size: 14px; text-align: left;
        line-height: 1.6; padding-top: 15px;
        border-top: 1px solid #999;
    }
    .reporter-name {
        display: block; text-align: right;
        font-weight: bold; margin-top: 10px;
        font-size: 13px;
    }
</style>
"""

# HTML構築
content_html = f"""
<div class="newspaper-board">
    <div class="newspaper-header">最終ジャッジ</div>
    <div class="newspaper-container">
        <div class="char-card">
            <span class="yoso-mark ichika-c">◎</span>
            <div class="title-label">本命・一果</div>
            <div class="bet-display">{i_bet}</div>
            <div class="comment-box">{i_msg}<span class="reporter-name">― 記者・一果</span></div>
        </div>
        <div class="char-card">
            <span class="yoso-mark hatsune-c">○</span>
            <div class="title-label">対抗・初音</div>
            <div class="bet-display">{h_bet}</div>
            <div class="comment-box">{h_msg}<span class="reporter-name">― 記者・初音</span></div>
        </div>
        <div class="char-card">
            <span class="yoso-mark kiina-c">穴</span>
            <div class="title-label">特注・キイナ</div>
            <div class="bet-display">{k_bet}</div>
            <div class="comment-box">{k_msg}<span class="reporter-name">― 記者・キイナ</span></div>
        </div>
    </div>
</div>
"""

# スタイルとコンテンツを個別に描画
st.markdown(css_style, unsafe_allow_html=True)
st.markdown(content_html, unsafe_allow_html=True)

st.divider()
st.info("💡 このプレビューを画像保存して、noteやXに投稿できます。")
