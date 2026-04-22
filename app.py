import streamlit as st
import datetime

# ページ設定
st.set_page_config(page_title="Birthstones新聞 生成App", layout="wide")

# 日付
today = datetime.date.today()
formatted_date = today.strftime("%Y年%m月%d日")

# --- 1. サイドバー：入力（全員分） ---
st.sidebar.header("📝 記者全員、集合！")

with st.sidebar.expander("🚩 一果の精密判定（左エリア）", expanded=True):
    i_place = st.text_input("レース場", value="住之江")
    i_race = st.text_input("レース番号", value="11R")
    i_avg = st.slider("場平均逃げ率 (%)", 30, 70, 52)
    i_exp = st.slider("今回の逃げ期待値 (%)", 30, 100, 74)
    i_text = st.text_area("一果のつぶやき", value="平均よりかなり高いよ！ここは一果にお任せ！")

with st.sidebar.expander("📝 初音の分析（右エリア上）", expanded=True):
    h_bet = st.text_input("推奨買い目", value="1-4-全")
    h_data = st.text_area("データメモ", value="・補正タイム1位\n・当地勝率No.1")

with st.sidebar.expander("⚡️ キイナの穴狙い（右エリア下）", expanded=True):
    k_eval = st.selectbox("穴判定", ["見（ケン）", "GO", "買わなきゃ損！"], index=2)
    k_nobi = st.slider("伸び足上昇率 (%)", -10, 30, 15)
    k_text = st.text_area("キイナの予感", value="4が凹めば5のまくり差し炸裂っしょ！")

# --- 2. CSSスタイル定義 ---
# レンダリングバグを回避しつつ、クオリティを維持するための設定
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Kosugi+Maru&family=Yomogi&display=swap');
    .stApp { font-family: 'Kosugi Maru', sans-serif; background-color: #fdfcf0; }
    
    .newspaper-base {
        background-color: #ffffff !important;
        width: 900px !important;
        margin: 0 auto !important;
        padding: 35px !important;
        border: 1.5px solid #d1d5db !important;
        box-shadow: 2px 2px 0px #e2e8f0, 10px 10px 20px rgba(0,0,0,0.05) !important;
        color: #334155 !important;
    }

    /* メーター */
    .meter-container {
        position: relative; width: 140px; height: 75px;
        border-bottom: 2px solid #57534e; margin: 10px auto; overflow: hidden;
    }
    .meter-arc {
        width: 140px; height: 140px; border-radius: 50%;
        border: 12px solid #e2e8f0; border-bottom-color: transparent;
        border-left-color: #f87171; border-top-color: #fca5a5; transform: rotate(45deg);
    }
    .meter-needle {
        position: absolute; bottom: 0; left: 50%; width: 3px; height: 60px;
        background: #1e293b; transform-origin: bottom center; border-radius: 2px;
    }

    /* スタンプ・アラート */
    .rank-stamp {
        border: 3px double #ef4444; color: #ef4444; padding: 3px 10px;
        font-size: 18px; font-weight: bold; transform: rotate(-8deg); display: inline-block;
    }
    .kiina-alert {
        background: #fffbeb; border: 2px dashed #f59e0b; animation: flash 1.5s infinite;
        padding: 8px; border-radius: 8px; text-align: center; font-size: 13px; margin-bottom: 10px;
    }
    @keyframes flash { 0%, 100% { opacity: 1; } 50% { opacity: 0.6; } }

    /* 判定ボタン */
    .status-son { background: #ef4444; color: white; padding: 4px 12px; border-radius: 5px; font-weight: bold; }

    /* 枠・デコレーション */
    .memo-box {
        position: relative; border: 2px solid #57534e; border-radius: 10px;
        padding: 15px; background: #fff; margin-bottom: 20px;
    }
    .box-title {
        font-weight: bold; border-bottom: 2px dashed #57534e; margin-bottom: 12px;
        display: flex; align-items: center; gap: 5px; font-size: 16px;
    }
    .clip-icon { position: absolute; top: -15px; left: 15px; font-size: 24px; }
</style>
""", unsafe_allow_html=True)

# --- 3. ロジック計算 ---
# 一果の計算
i_diff = i_exp - i_avg
i_diff_str = f"+{i_diff}%" if i_diff >= 0 else f"{i_diff}%"
needle_angle = (i_exp - 50) * 1.8 
if i_diff >= 15: i_status = "鬼絞り"
else: i_status = "有力"

# キイナの判定クラス
k_stamp = "status-son" if k_eval == "買わなきゃ損！" else ""

# --- 4. HTML構築 ---
html_content = (
    '<div class="newspaper-base">'
    '  '
    '  <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 25px;">'
    '    <div style="background: #ffecd2; padding: 5px 30px; border-radius: 3px; border: 1px solid #57534e;">'
    '      <span style="font-size: 30px; font-weight: bold;">💎 Birthstones新聞</span>'
    '    </div>'
    f'    <div style="text-align: right; font-size: 12px;">{formatted_date} 第15号<br>🧭 3年1組 きずな班</div>'
    '  </div>'
    
    '  <div style="display: flex; gap: 20px;">'
    '    '
    '    <div style="flex: 1.8;">'
    '      <div class="memo-box" style="background: #fffcf5; border-color: #f59e0b;">'
    '        <div class="clip-icon">📎</div>'
    '        <div class="box-title">🚩 特集：一果のイン逃げ精密判定</div>'
    f'        <p style="font-size: 13px;">場所：ボートレース<b>{i_place}</b> ({i_race})</p>'
    '        <div style="display: flex; justify-content: space-around; align-items: center; margin: 15px 0;">'
    '          <div style="text-align: center;">'
    '            <div class="meter-container">'
    '              <div class="meter-arc"></div>'
    f'              <div class="meter-needle" style="transform: translateX(-50%) rotate({needle_angle}deg);"></div>'
    '            </div>'
    f'            <div style="font-size: 11px;">期待値: {i_exp}%</div>'
    '          </div>'
    '          <div style="text-align: center;">'
    '            <span style="font-size: 11px; color: #64748b;">場平均より</span><br>'
    f'            <span style="font-size: 36px; font-weight: bold; color: #ef4444;">{i_diff_str}</span><br>'
    f'            <div class="rank-stamp" style="margin-top: 10px;">{i_status}確定！</div>'
    '          </div>'
    '        </div>'
    '        <div style="display: flex; gap: 10px; background: #fefce8; padding: 10px; border-radius: 10px; font-family: \'Yomogi\', cursive;">'
    '          <div style="width: 45px; height: 45px; background: #fff; border: 1px solid #57534e; border-radius: 50%; flex-shrink: 0; display: flex; align-items: center; justify-content: center; font-size: 10px;">一果</div>'
    f'          <div style="font-size: 14px;">「{i_text}」</div>'
    '        </div>'
    '      </div>'
    '    </div>'

    '    '
    '    <div style="flex: 1.2;">'
    '      '
    '      <div class="memo-box" style="border-color: #3b82f6; background: #f0f9ff;">'
    '        <div class="box-title" style="color: #3b82f6;">📚 初音のまじめな分析</div>'
    f'        <div style="background: #1e293b; color: white; padding: 5px; text-align: center; border-radius: 4px; font-weight: bold; margin-bottom: 10px;">{h_bet}</div>'
    f'        <div style="font-size: 12px; line-height: 1.5;">{h_data.replace("\\n", "<br>")}</div>'
    '      </div>'

    '      '
    '      <div class="memo-box" style="border-color: #eab308; background: #fffdf0;">'
    f'        <div class="box-title" style="color: #854d0e;">⚡ キイナの穴狙い！</div>'
    f'        {"<div class=\"kiina-alert\">⚠️ 伸び足 +"+str(k_nobi)+"% 突破！ ⚠️</div>" if k_nobi >= 10 else ""}'
    f'        <div style="text-align: center; margin-bottom: 10px;"><span class=\"{k_stamp}\" style=\"font-size: 18px;\">{k_eval}</span></div>'
    '        <div style="display: flex; gap: 8px; background: #fff; padding: 8px; border-radius: 8px; font-family: \'Yomogi\', cursive; border: 1px solid #fef08a;">'
    '          <div style="width: 40px; height: 40px; background: #fff; border: 1px solid #57534e; border-radius: 50%; flex-shrink: 0; display: flex; align-items: center; justify-content: center; font-size: 9px;">キイナ</div>'
    f'          <div style="font-size: 13px;">「{k_text}」</div>'
    '        </div>'
    '      </div>'
    '    </div>'
    '  </div>'
    '  <div style="text-align: center; margin-top: 15px; font-size: 11px; color: #94a3b8;">(c) BOAT STRIKE - 学級新聞係</div>'
    '</div>'
)

st.markdown(html_content, unsafe_allow_html=True)
