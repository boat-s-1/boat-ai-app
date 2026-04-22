import streamlit as st
import datetime

# ページ設定
st.set_page_config(page_title="Birthstones新聞 生成App", layout="wide")

# 日付
today = datetime.date.today()
formatted_date = today.strftime("%Y年%m月%d日")

# --- 1. サイドバー：入力 ---
st.sidebar.header("📝 記事の内容を書こう！")

with st.sidebar.expander("一果の「特集」", expanded=True):
    i_place = st.text_input("レース場", value="住之江")
    i_race = st.text_input("レース番号", value="11R")
    i_avg = st.number_input("場平均(%)", 0, 100, 52)
    i_exp = st.number_input("期待値(%)", 0, 100, 74)
    i_text = st.text_area("メッセージ", value="平均より高いよ！ここは一果にお任せ！")

with st.sidebar.expander("初音の「データ」", expanded=True):
    h_bet = st.text_input("推奨買い目", value="1-4-全")
    h_data = st.text_area("データ箇条書き", value="・補正タイム1位\n・当地勝率No.1")

with st.sidebar.expander("キイナの「穴」", expanded=True):
    k_eval = st.selectbox("判定", ["買わなきゃ損！", "GO", "見（ケン）"])
    k_text = st.text_area("メッセージ ", value="4が凹めば5のまくり差し炸裂！")

# --- 2. CSSスタイル定義 ---
# レンダリングバグを防ぐため、!importantを多用し、CSSを分離して先に読み込ませます
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Kosugi+Maru&display=swap');
    .stApp { font-family: 'Kosugi Maru', sans-serif; background-color: #f0f4f8; }
    
    /* 新聞の台紙 */
    .paper-frame {
        background-color: white !important;
        width: 850px !important;
        margin: 0 auto !important;
        padding: 30px !important;
        border: 2px solid #333 !important;
        box-shadow: 10px 10px 0px #cbd5e0 !important;
    }
    
    /* ヘッダー */
    .news-header {
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        border-bottom: 3px double #333 !important;
        margin-bottom: 25px !important;
        padding-bottom: 10px !important;
    }
    .main-banner {
        background: linear-gradient(to right, #ffecd2, #fcb69f) !important;
        padding: 8px 50px !important;
        border: 2px solid #333 !important;
        border-radius: 50px !important;
        font-size: 30px !important;
        font-weight: bold !important;
        color: #1a1a1a !important;
    }
    
    /* 左右レイアウト */
    .news-grid { display: flex !important; gap: 20px !important; }
    .tokushu-side { flex: 2 !important; }
    .corner-side { flex: 1 !important; }
    
    /* 各コーナーの箱 */
    .info-box {
        border: 2px solid #4a5568 !important;
        border-radius: 15px !important;
        padding: 15px !important;
        margin-bottom: 15px !important;
        background: #fff !important;
    }
    .info-title {
        background: #edf2f7 !important;
        border: 1px solid #333 !important;
        display: inline-block !important;
        padding: 2px 12px !important;
        font-weight: bold !important;
        margin-bottom: 15px !important;
        border-radius: 5px !important;
    }
    
    /* 吹き出しとアイコン */
    .speech-bubble {
        display: flex !important;
        align-items: center !important;
        gap: 10px !important;
        background: #fefcbf !important;
        border-radius: 10px !important;
        padding: 10px !important;
        font-size: 13px !important;
    }
    .icon-circle {
        width: 50px !important;
        height: 50px !important;
        background: #fff !important;
        border: 1px solid #333 !important;
        border-radius: 50% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 10px !important;
        flex-shrink: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. HTMLコンテンツ構築 ---
diff = i_exp - i_avg
diff_str = f"+{diff}%" if diff >= 0 else f"{diff}%"

# HTML部分。ここには波括弧を一切含めず、f-stringだけで変数を展開します。
news_html = f"""
<div class="paper-frame">
    <div class="news-header">
        <div style="font-size: 24px;">✨💎✨</div>
        <div class="main-banner">Birthstones新聞</div>
        <div style="text-align: right; font-size: 12px; color: #4a5568;">
            {formatted_date} 第15号<br>🧭 3年1組 きずな班
        </div>
    </div>

    <div class="news-grid">
        <div class="tokushu-side">
            <div class="info-box" style="border-color: #f6ad55; background: #fffaf0;">
                <div class="info-title">🚩 特集：一果のイン逃げ判定</div>
                <p style="font-size: 13px; margin-bottom: 15px;">場所：ボートレース{i_place} ({i_race}) / 天気：晴れ☀️</p>
                
                <div style="display: flex; justify-content: space-around; align-items: center;">
                    <div style="border: 2px dashed #f6ad55; border-radius: 50%; width: 120px; height: 120px; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                        <span style="font-size: 11px;">場平均より</span>
                        <span style="font-size: 30px; font-weight: bold; color: #e53e3e;">{diff_str}</span>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 14px; margin-bottom: 5px;">期待値：{i_exp}%</div>
                        <div style="border: 2px solid red; color: red; padding: 5px; font-weight: bold; transform: rotate(-5deg); font-size: 14px;">鬼絞り確定！</div>
                    </div>
                </div>

                <div class="speech-bubble" style="margin-top: 20px;">
                    <div class="icon-circle">一果</div>
                    <div>「{i_text}」</div>
                </div>
            </div>
        </div>

        <div class="corner-side">
            <div class="info-box" style="border-color: #4299e1;">
                <div class="info-title" style="background: #ebf8ff;">📝 初音のデータメモ</div>
                <div style="background: #2d3748; color: white; padding: 5px; text-align: center; border-radius: 5px; margin-bottom: 10px; font-weight: bold;">
                    {h_bet}
                </div>
                <div style="font-size: 12px; line-height: 1.5;">
                    {h_data.replace('\\n', '<br>')}
                </div>
            </div>

            <div class="info-box" style="border-color: #f6e05e;">
                <div class="info-title" style="background: #fffff0;">⚡️ キイナの一撃！</div>
                <p style="text-align: center; font-weight: bold; color: #d69e2e; margin-bottom: 10px;">
                    判定：{k_eval}
                </p>
                <div class="speech-bubble" style="background: #fffaf0;">
                    <div class="icon-circle">キイナ</div>
                    <div>「{k_text}」</div>
                </div>
            </div>
        </div>
    </div>
</div>
"""

st.markdown(news_html, unsafe_allow_html=True)
