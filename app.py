import streamlit as st
import datetime

# ページ設定
st.set_page_config(page_title="Birthstones新聞 生成App", layout="wide")

# 日付
today = datetime.date.today()
formatted_date = today.strftime("%Y年%m月%d日")

# --- 1. サイドバー：入力（一果の判定ロジック用） ---
st.sidebar.header("🚩 一果の調査報告")

with st.sidebar.expander("💎 イン逃げ精密判定", expanded=True):
    i_place = st.text_input("レース場", value="住之江")
    i_race = st.text_input("レース番号", value="11R")
    i_avg = st.slider("場平均逃げ率 (%)", 30, 70, 52)
    i_exp = st.slider("今回の逃げ期待値 (%)", 30, 100, 74)
    i_text = st.text_area("一果のつぶやき", value="平均よりかなり高いよ！壁役の2号艇も安定してるし、ここは一果にお任せ！")

# 2人目・3人目のデータ（簡易版）
h_bet = st.sidebar.text_input("初音の推奨買い目", value="1-4-全")
k_eval = st.sidebar.selectbox("キイナの穴判定", ["買わなきゃ損！", "GO", "見（ケン）"])

# --- 2. CSSスタイル定義 ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Kosugi+Maru&family=Yomogi&display=swap');
    .stApp { font-family: 'Kosugi Maru', sans-serif; background-color: #fdfcf0; }
    
    .newspaper-base {
        background-color: #ffffff !important;
        width: 900px !important;
        margin: 0 auto !important;
        padding: 40px !important;
        border: 1px solid #d1d5db !important;
        box-shadow: 2px 2px 0px #e2e8f0, 10px 10px 20px rgba(0,0,0,0.05) !important;
        color: #334155 !important;
    }

    /* メーターデザイン */
    .meter-container {
        position: relative;
        width: 160px; height: 85px;
        border-bottom: 2px solid #57534e;
        margin: 10px auto;
        overflow: hidden;
    }
    .meter-arc {
        width: 160px; height: 160px;
        border-radius: 50%;
        border: 15px solid #e2e8f0;
        border-bottom-color: transparent;
        border-left-color: #f87171; /* Danger/Hot zone */
        border-top-color: #fca5a5;
        transform: rotate(45deg);
    }
    .meter-needle {
        position: absolute;
        bottom: 0; left: 50%;
        width: 4px; height: 70px;
        background: #1e293b;
        transform-origin: bottom center;
        border-radius: 2px;
    }

    /* ランクスタンプ */
    .rank-stamp {
        display: inline-block;
        border: 4px double #ef4444;
        color: #ef4444;
        padding: 5px 15px;
        font-size: 24px;
        font-weight: bold;
        transform: rotate(-10deg);
        border-radius: 8px;
        background: rgba(239, 68, 68, 0.05);
    }

    /* 学級新聞デコレーション */
    .memo-box {
        position: relative;
        border: 2px solid #57534e;
        border-radius: 10px;
        padding: 20px;
        background: #fff;
    }
    .tape-deco {
        position: absolute;
        top: -15px; left: 30%;
        width: 100px; height: 30px;
        background: rgba(147, 197, 253, 0.5); /* 水色のマステ */
        transform: rotate(-2deg);
    }
</style>
""", unsafe_allow_html=True)

# --- 3. HTML構築 ---
diff = i_exp - i_avg
diff_val = f"+{diff}%" if diff >= 0 else f"{diff}%"

# 逃げランク判定
if diff >= 15: rank, status = "S", "鬼絞り"
elif diff >= 5: rank, status = "A", "有力"
else: rank, status = "B", "慎重に"

# メーターの角度計算 (0%~100% を -90度~90度に変換)
needle_angle = (i_exp - 50) * 1.8 

html_view = (
    '<div class="newspaper-base">'
    '  <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 30px;">'
    '    <div style="background: #ffecd2; padding: 5px 30px; border-radius: 3px; box-shadow: 2px 2px 4px rgba(0,0,0,0.1);">'
    '      <span style="font-size: 32px; font-weight: bold;">💎 Birthstones新聞</span>'
    '    </div>'
    f'    <div style="text-align: right; font-size: 13px;">{formatted_date}<br>第15号 / 3年1組 予想係</div>'
    '  </div>'
    
    '  <div style="display: flex; gap: 25px;">'
    '    '
    '    <div style="flex: 1.8;">'
    '      <div class="memo-box" style="background: #fffcf5; border-color: #f59e0b;">'
    '        <div class="tape-deco"></div>'
    '        <div style="font-size: 20px; font-weight: bold; border-bottom: 2px dashed #57534e; margin-bottom: 15px;">🚩 守護神・一果のイン逃げ精密判定</div>'
    f'        <p style="font-size: 14px;">本日の調査対象：<b>ボートレース{i_place}</b> ({i_race})</p>'
    
    '        <div style="display: flex; justify-content: space-around; align-items: center; margin: 20px 0;">'
    '          '
    '          <div style="text-align: center;">'
    '            <div class="meter-container">'
    '              <div class="meter-arc"></div>'
    f'              <div class="meter-needle" style="transform: translateX(-50%) rotate({needle_angle}deg);"></div>'
    '            </div>'
    f'            <div style="font-size: 12px; margin-top: 5px;">期待値: {i_exp}%</div>'
    '          </div>'
    
    '          <div style="text-align: center;">'
    f'            <div style="font-size: 14px; color: #64748b;">場平均より</div>'
    f'            <div style="font-size: 40px; font-weight: bold; color: #ef4444; line-height: 1;">{diff_val}</div>'
    f'            <div class="rank-stamp" style="margin-top: 15px;">ランク{rank}：{status}</div>'
    '          </div>'
    '        </div>'
    
    '        <div style="display: flex; gap: 12px; background: #fefce8; padding: 12px; border-radius: 15px; border: 1px solid #fde047; font-family: \'Yomogi\', cursive;">'
    '          <div style="width: 50px; height: 50px; background: #fff; border: 1.5px solid #57534e; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 10px; flex-shrink: 0;">一果</div>'
    f'          <div style="font-size: 15px;">「{i_text}」</div>'
    '        </div>'
    '      </div>'
    '    </div>'
    
    '    '
    '    <div style="flex: 1;">'
    '      <div class="memo-box" style="border-color: #3b82f6; padding: 15px;">'
    '        <div style="font-weight: bold; font-size: 16px; margin-bottom: 10px; color: #3b82f6;">📚 初音のデータ</div>'
    f'        <div style="background: #1e293b; color: white; padding: 5px; text-align: center; border-radius: 4px; font-size: 18px; font-weight: bold;">{h_bet}</div>'
    '      </div>'
    '      <div class="memo-box" style="border-color: #eab308; padding: 15px;">'
    '        <div style="font-weight: bold; font-size: 16px; margin-bottom: 10px; color: #eab308;">⚡ キイナの直感</div>'
    f'        <div style="text-align: center; font-weight: bold; font-size: 20px;">{k_eval}</div>'
    '      </div>'
    '    </div>'
    '  </div>'
    '  <div style="text-align: center; margin-top: 20px; font-size: 11px; color: #94a3b8;">(c) BOAT STRIKE - 3人の秘密基地</div>'
    '</div>'
)

st.markdown(html_view, unsafe_allow_html=True)
