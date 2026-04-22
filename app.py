import streamlit as st
import datetime

# ページ設定
st.set_page_config(page_title="Birthstones新聞 生成App", layout="wide")

# 日付
today = datetime.date.today()
formatted_date = today.strftime("%Y年%m月%d日")

# --- 1. サイドバー：入力 ---
st.sidebar.header("📝 編集長！記事を書きましょう")

with st.sidebar.expander("💎 特集（一果）", expanded=True):
    i_place = st.text_input("レース場", value="住之江")
    i_race = st.text_input("レース番号", value="11R")
    i_avg = st.number_input("場平均(%)", 0, 100, 52)
    i_exp = st.number_input("期待値(%)", 0, 100, 74)
    i_text = st.text_area("一果のつぶやき", value="平均よりかなり高いよ！壁役も安定してるし、ここは一果にお任せ！")

with st.sidebar.expander("📚 学習（初音）", expanded=True):
    h_bet = st.text_input("推奨買い目", value="1-4-全")
    h_data = st.text_area("データメモ", value="・補正タイム1位\n・当地勝率No.1")

with st.sidebar.expander("🎾 遊び（キイナ）", expanded=True):
    k_eval = st.selectbox("穴判定", ["買わなきゃ損！", "GO", "見（ケン）"])
    k_text = st.text_area("キイナの予感 ", value="4が凹めば5のまくり差し炸裂！買わなきゃ損だよ！")

# --- 2. CSSスタイル定義（学級新聞の質感を追求） ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Kosugi+Maru&family=Yomogi&display=swap');
    
    .stApp { font-family: 'Kosugi Maru', sans-serif; background-color: #fdfcf0; }
    
    /* 新聞の紙質 */
    .newspaper-base {
        background-color: #ffffff !important;
        width: 880px !important;
        margin: 0 auto !important;
        padding: 40px !important;
        border: 1px solid #d1d5db !important;
        border-radius: 2px !important;
        box-shadow: 2px 2px 0px #e2e8f0, 8px 8px 15px rgba(0,0,0,0.05) !important;
        background-image: radial-gradient(#f1f1f1 1px, transparent 1px) !important;
        background-size: 20px 20px !important;
    }
    
    /* ヘッダー：マステ風の装飾 */
    .header-tape {
        background: #ffecd2;
        display: inline-block;
        padding: 5px 30px;
        transform: rotate(-1deg);
        border-radius: 3px;
        box-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 30px;
    }
    .newspaper-title {
        font-size: 38px !important;
        font-weight: bold !important;
        color: #334155 !important;
        letter-spacing: 3px !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    /* 2カラムレイアウト */
    .news-grid { display: flex !important; gap: 30px !important; }
    .col-left { flex: 1.8 !important; }
    .col-right { flex: 1.2 !important; }
    
    /* コーナーボックス：付箋・クリップ風 */
    .memo-box {
        position: relative;
        border: 2px solid #57534e;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 25px;
        background: #fff;
    }
    .memo-box::before { /* クリップ風装飾 */
        content: '📎';
        position: absolute;
        top: -15px;
        left: 20px;
        font-size: 24px;
    }
    
    .box-heading {
        font-size: 20px;
        font-weight: bold;
        border-bottom: 2px dashed #57534e;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* スコア表示 */
    .score-wrap {
        background: #fff7ed;
        border-radius: 50%;
        width: 140px; height: 140px;
        display: flex; flex-direction: column;
        align-items: center; justify-content: center;
        border: 2px solid #fb923c;
        margin: 10px auto;
    }
    
    /* 吹き出し（手書き風） */
    .char-voice {
        display: flex;
        gap: 12px;
        align-items: flex-start;
        background: #fefce8;
        padding: 12px;
        border-radius: 15px;
        border: 1px solid #fde047;
        font-family: 'Yomogi', cursive; /* より手書きに近いフォント */
        font-size: 15px;
    }
    .face-icon {
        width: 50px; height: 50px;
        background: #fff;
        border: 1.5px solid #57534e;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 10px; flex-shrink: 0;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. HTML構築 ---
diff = i_exp - i_avg
diff_val = f"+{diff}%" if diff >= 0 else f"{diff}%"

# レイアウト崩れを完全に防ぐための連結型HTML
html_view = (
    '<div class="newspaper-base">'
    '  <div style="display: flex; justify-content: space-between; align-items: flex-start;">'
    '    <div class="header-tape">'
    '      <span class="newspaper-title">💎 Birthstones新聞</span>'
    '    </div>'
    f'    <div style="text-align: right; font-size: 13px; padding-top: 10px;">{formatted_date}<br>第15号 / 3年1組 きずな班</div>'
    '  </div>'
    
    '  <div class="news-grid">'
    '    <div class="col-left">'
    '      <div class="memo-box" style="background: #fffcf5; border-color: #f59e0b;">'
    '        <div class="box-heading">🚩 今日の大注目！イン逃げ調査隊</div>'
    f'        <p style="font-size: 14px;">本日の舞台：<b>ボートレース{i_place}</b> ({i_race})</p>'
    '        <div style="display: flex; justify-content: space-around; align-items: center; margin: 20px 0;">'
    '          <div class="score-wrap">'
    '            <span style="font-size: 11px;">場平均より</span>'
    f'            <span style="font-size: 32px; font-weight: bold; color: #ea580c;">{diff_val}</span>'
    '          </div>'
    '          <div style="text-align: center;">'
    f'            <div style="font-size: 15px;">逃げる確率：<b>{i_exp}%</b></div>'
    '            <div style="margin-top: 10px; color: #dc2626; border: 2px solid #dc2626; padding: 4px 10px; font-weight: bold; transform: rotate(-5deg);">◎ はなまる！</div>'
    '          </div>'
    '        </div>'
    '        <div class="char-voice">'
    '          <div class="face-icon">一果</div>'
    f'          <div>「{i_text}」</div>'
    '        </div>'
    '      </div>'
    '    </div>'
    
    '    <div class="col-right">'
    '      <div class="memo-box" style="background: #f0f9ff; border-color: #3b82f6;">'
    '        <div class="box-heading">📖 初音のまじめな分析</div>'
    f'        <div style="background: #1e293b; color: white; padding: 6px; text-align: center; border-radius: 4px; font-weight: bold; margin-bottom: 12px;">狙い：{h_bet}</div>'
    f'        <div style="font-size: 13px; line-height: 1.6;">{h_data.replace("\\n", "<br>")}</div>'
    '      </div>'
    
    '      <div class="memo-box" style="background: #fffcf0; border-color: #eab308;">'
    '        <div class="box-header" style="font-weight: bold; font-size: 16px; margin-bottom: 10px;">⚡ キイナの直感メモ</div>'
    f'        <p style="text-align: center; font-weight: bold; color: #854d0e; margin-bottom: 10px;">判定：{k_eval}</p>'
    '        <div class="char-voice" style="background: #fff;">'
    '          <div class="face-icon">キイナ</div>'
    f'          <div>「{k_text}」</div>'
    '        </div>'
    '      </div>'
    '    </div>'
    '  </div>'
    '  <div style="text-align: center; margin-top: 20px; font-size: 12px; color: #94a3b8;">(c) BOAT STRIKE - 学級新聞係</div>'
    '</div>'
)

st.markdown(html_view, unsafe_allow_html=True)
