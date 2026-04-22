import streamlit as st
import datetime

# ページ設定
st.set_page_config(page_title="Birthstones新聞 生成App", layout="wide")

# 日付
today = datetime.date.today()
formatted_date = today.strftime("%Y年%m月%d日")

# --- 1. サイドバー：入力（キイナの穴ロジック用） ---
st.sidebar.header("⚡️ キイナの秘密報告")

with st.sidebar.expander("爆穴・展開予測", expanded=True):
    k_eval = st.sidebar.radio("キイナの判定", ["見（ケン）", "GO", "買わなきゃ損！"], index=1)
    k_nobi = st.sidebar.slider("伸び足の上昇率 (%)", -10, 30, 15)
    k_text = st.sidebar.text_area("キイナのつぶやき", value="4号艇が凹む予感！5号艇の伸び足なら一気に飲み込めるよ！買わなきゃ損っしょ！")

# 他のキャラのデータ（簡易）
i_diff = st.sidebar.text_input("一果の乖離率", value="+22%")
h_bet = st.sidebar.text_input("初音の推奨買い目", value="1-4-全")

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
        box-shadow: 10px 10px 20px rgba(0,0,0,0.05) !important;
    }

    /* キイナ・アラートの発動演出 */
    .kiina-alert {
        background: #fffbeb;
        border: 3px dashed #f59e0b;
        animation: flash 1.5s infinite;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 15px;
    }
    @keyframes flash {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }

    /* 3段階判定スタンプ */
    .judgement-stamp {
        display: inline-block;
        padding: 5px 15px;
        font-size: 24px;
        font-weight: bold;
        border-radius: 5px;
        transform: rotate(-3deg);
        box-shadow: 2px 2px 0px rgba(0,0,0,0.2);
    }
    .status-ken { background: #94a3b8; color: white; }
    .status-go { background: #3b82f6; color: white; }
    .status-son { background: #ef4444; color: white; border: 2px solid #fee2e2; }

    /* 学級新聞デコ */
    .memo-box {
        position: relative;
        border: 2px solid #57534e;
        border-radius: 10px;
        padding: 20px;
        background: #fff;
    }
    .clip-deco {
        position: absolute;
        top: -20px; right: 20px;
        font-size: 30px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. HTML構築 ---

# 判定に応じたクラスの決定
if k_eval == "見（ケン）": stamp_class = "status-ken"
elif k_eval == "GO": stamp_class = "status-go"
else: stamp_class = "status-son"

# アラート発動の判定（伸びが10%を超えたら）
alert_html = ""
if k_nobi >= 10:
    alert_html = f'<div class="kiina-alert">⚠️ キイナ・アラート発動中！伸び足：+{k_nobi}%突破！ ⚠️</div>'

html_view = (
    '<div class="newspaper-base">'
    '  <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 30px;">'
    '    <div style="background: #ffecd2; padding: 5px 30px; border-radius: 3px; box-shadow: 2px 2px 4px rgba(0,0,0,0.1);">'
    '      <span style="font-size: 32px; font-weight: bold;">💎 Birthstones新聞</span>'
    '    </div>'
    f'    <div style="text-align: right; font-size: 13px;">{formatted_date}<br>第15号 / 3年1組 穴狙い係</div>'
    '  </div>'
    
    '  <div style="display: flex; gap: 25px;">'
    '    '
    '    <div style="flex: 1;">'
    '      <div class="memo-box" style="border-color: #f59e0b; background: #fffcf5;">'
    '        <div style="font-weight: bold; border-bottom: 1px solid #57534e; margin-bottom: 10px;">🚩 一果のイン逃げ判定</div>'
    f'        <div style="font-size: 30px; font-weight: bold; color: #ef4444; text-align: center;">{i_diff}</div>'
    '      </div>'
    '      <div class="memo-box" style="border-color: #3b82f6; margin-top: 15px;">'
    '        <div style="font-weight: bold; color: #3b82f6;">📚 初音のデータ</div>'
    f'        <div style="font-size: 16px; font-weight: bold; text-align: center;">{h_bet}</div>'
    '      </div>'
    '    </div>'
    
    '    '
    '    <div style="flex: 1.8;">'
    '      <div class="memo-box" style="border-color: #eab308; background: #fffdf0;">'
    '        <div class="clip-deco">📎</div>'
    '        <div style="font-size: 20px; font-weight: bold; border-bottom: 2px dashed #57534e; margin-bottom: 15px;">⚡️ キイナの5アタマ穴狙い！</div>'
    
    f'        {alert_html}'
    
    '        <div style="display: flex; justify-content: space-around; align-items: center; margin: 20px 0;">'
    '          <div style="text-align: center;">'
    '            <p style="font-size: 12px; color: #854d0e;">今レースの破壊力判定</p>'
    f'            <div class="judgement-stamp {stamp_class}">{k_eval}</div>'
    '          </div>'
    '          <div style="text-align: center; background: #fff; padding: 10px; border-radius: 10px; border: 1px solid #eab308;">'
    f'            <div style="font-size: 11px;">伸び足突き抜け度</div>'
    f'            <div style="font-size: 28px; font-weight: bold; color: #d97706;">+{k_nobi}%</div>'
    '          </div>'
    '        </div>'
    
    '        <div style="display: flex; gap: 12px; background: #fff; padding: 12px; border-radius: 15px; border: 1.5px solid #fef08a; font-family: \'Yomogi\', cursive;">'
    '          <div style="width: 50px; height: 50px; background: #fff; border: 1.5px solid #57534e; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 10px; flex-shrink: 0;">キイナ</div>'
    f'          <div style="font-size: 15px;">「{k_text}」</div>'
    '        </div>'
    '      </div>'
    '    </div>'
    '  </div>'
    '  <div style="text-align: center; margin-top: 20px; font-size: 11px; color: #94a3b8;">(c) BOAT STRIKE - 展開の破壊者・参上！</div>'
    '</div>'
)

st.markdown(html_view, unsafe_allow_html=True)
