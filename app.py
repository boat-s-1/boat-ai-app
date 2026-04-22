import streamlit as st

# ページ設定
st.set_page_config(page_title="BOAT STRIKE 新聞生成App", layout="wide")

# --- 1. スタイル定義 (CSS) ---
# 3人のキャラカラーとカードデザインを定義します
st.markdown("""
<style>
    .newspaper-footer {
        display: flex;
        gap: 15px;
        background-color: #f1f5f9;
        padding: 25px;
        border: 3px solid #1e293b;
        border-radius: 15px;
        margin-top: 20px;
    }
    .char-card {
        flex: 1;
        background: white;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        border-top: 10px solid;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    /* キャラの個別の色設定 */
    .ichika-box { border-top-color: #ef4444; }
    .hatsune-box { border-top-color: #3b82f6; }
    .kiina-box { border-top-color: #f59e0b; }
    
    .char-name {
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 15px;
    }
    .bet-area {
        background: #1e293b;
        color: #ffffff;
        padding: 15px;
        font-size: 28px;
        font-weight: 900;
        border-radius: 8px;
        margin: 10px 0;
        font-family: 'Courier New', Courier, monospace;
        letter-spacing: 3px;
    }
    .comment {
        font-size: 14px;
        color: #475569;
        font-style: italic;
        margin-top: 10px;
        line-height: 1.4;
    }
    .char-icon-placeholder {
        width: 80px;
        height: 80px;
        background: #e2e8f0;
        border-radius: 50%;
        margin: 0 auto 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. サイドバー (データ入力) ---
st.sidebar.header("🏆 予想入力")
st.sidebar.write("各キャラクターの買い目とコメントを設定してください。")

# 一果の入力
with st.sidebar.expander("一果 (本命) の設定", expanded=True):
    ichika_bet = st.text_input("買い目", value="1-2-34", key="i_b")
    ichika_msg = st.text_area("コメント", value="場平均より+22%も高いよ！ここは一果を信じて鬼絞りっ！", key="i_m")

# 初音の入力
with st.sidebar.expander("初音 (客観) の設定", expanded=True):
    hatsune_bet = st.text_input("買い目", value="1-4-全", key="h_b")
    hatsune_msg = st.text_area("コメント", value="補正展示タイムから算出。オッズの歪みを含めるとこの目が合理的です。", key="h_m")

# キイナの入力
with st.sidebar.expander("キイナ (穴) の設定", expanded=True):
    kiina_bet = st.text_input("買い目", value="5-全-全", key="k_b")
    kiina_msg = st.text_area("コメント", value="4が凹めば5のまくり差しが炸裂するっしょ！買わなきゃ損だよ！", key="k_m")

# --- 3. メイン画面 (新聞生成) ---
st.title("📰 BOAT STRIKE 最終予想セクション")
st.write("サイドバーで入力した内容が、以下の新聞フォーマットにリアルタイムで反映されます。")

# 新聞のHTML組み立て
footer_html = f"""
<div class="newspaper-footer">
    <div class="char-card ichika-box">
        <div class="char-icon-placeholder" style="color:#ef4444; border: 2px solid #ef4444;">一果</div>
        <div class="char-name" style="color:#ef4444;">一果のズバリ！</div>
        <div class="bet-area">{ichika_bet}</div>
        <div class="comment">「{ichika_msg}」</div>
    </div>
    
    <div class="char-card hatsune-box">
        <div class="char-icon-placeholder" style="color:#3b82f6; border: 2px solid #3b82f6;">初音</div>
        <div class="char-name" style="color:#3b82f6;">初音の客観数値</div>
        <div class="bet-area">{hatsune_bet}</div>
        <div class="comment">「{hatsune_msg}」</div>
    </div>
    
    <div class="char-card kiina-box">
        <div class="char-icon-placeholder" style="color:#f59e0b; border: 2px solid #f59e0b;">キイナ</div>
        <div class="char-name" style="color:#f59e0b;">キイナの穴狙い！</div>
        <div class="bet-area">{kiina_bet}</div>
        <div class="comment">「{kiina_msg}」</div>
    </div>
</div>
"""

# HTMLを表示
st.markdown(footer_html, unsafe_allow_html=True)

# --- 4. 画像保存のアナウンス ---
st.divider()
st.info("💡 実際の運用では、このHTMLブロックを `html2image` などのライブラリで画像化して保存します。")
