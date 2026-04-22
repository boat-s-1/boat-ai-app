import streamlit as st
import datetime

# ページ設定
st.set_page_config(page_title="Birthstones新聞 生成App", layout="wide")

# 日付
today = datetime.date.today()
formatted_date = today.strftime("%Y年%m月%d日")

# --- 1. サイドバー：入力（初音のロジック用を追加） ---
st.sidebar.header("📊 編集会議：データ入力")

with st.sidebar.expander("🚩 特集：一果（イン逃げ）", expanded=False):
    i_place = st.text_input("レース場", value="住之江")
    i_race = st.text_input("レース番号", value="11R")
    i_avg = st.slider("場平均逃げ率 (%)", 30, 70, 52)
    i_exp = st.slider("逃げ期待値 (%)", 30, 100, 74)
    i_text = st.text_area("一果のつぶやき", value="平均よりかなり高いよ！壁役も安定してるし、一果にお任せ！")

with st.sidebar.expander("📚 精密：初音（データ）", expanded=True):
    h_odds_diff = st.number_input("期待配当の歪み (円)", -5000, 5000, 2500)
    h_wind_msg = st.text_input("風/条件の指摘", value="風速5m：平均配当が上昇傾向")
    h_evals = []
    st.write("全艇格付け (1〜6号艇)")
    cols = st.columns(6)
    for i in range(6):
        h_evals.append(cols[i].selectbox(f"{i+1}号", ["◯", "△", "✖️"], index=0 if i==0 else 2))
    h_text = st.text_area("初音の分析", value="補正タイム1位は1号艇。期待配当の歪みから4-5の連絡みも。")

with st.sidebar.expander("⚡️ 破壊：キイナ（穴狙い）", expanded=False):
    k_eval = st.selectbox("穴判定", ["見（ケン）", "GO", "買わなきゃ損！"], index=2)
    k_nobi = st.slider("伸び足上昇率 (%)", -10, 30, 15)
    k_text = st.text_area("キイナの予感", value="4が凹めば5のまくり差し炸裂っしょ！")

# --- 2. CSSスタイル定義 ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Kosugi+Maru&family=Yomogi&display=swap');
    .stApp { font-family: 'Kosugi Maru', sans-serif; background-color: #fdfcf0; }
    
    .newspaper-base {
        background-color: #ffffff !important;
        width: 900px !important; margin: 0 auto !important;
        padding: 35px !important; border: 1.5px solid #d1d5db !important;
        box-shadow: 10px 10px 20px rgba(0,0,0,0.05) !important;
        color: #334155 !important;
    }

    /* 一果のメーター */
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

    /* 初音の格付け表 */
    .hatsune-table {
        width: 100%; border-collapse: collapse; margin-top: 10px;
        font-size: 14px; text-align: center;
    }
    .hatsune-table th { background: #f1f5f9; border: 1px solid #cbd5e0; padding: 4px; }
    .hatsune-table td { border: 1px solid #cbd5e0; padding: 4px; font-weight: bold; }
    .mark-circle { color: #ef4444; }
    .mark-cross { color: #94a3b8; }

    /* 各種ボックス */
    .memo-box {
        position: relative; border: 2px solid #57534e; border-radius: 10px;
        padding: 15px; background: #fff; margin-bottom: 20px;
    }
    .box-title {
        font-weight: bold; border-bottom: 2px dashed #57534e; margin-bottom: 12px;
        display: flex; align-items: center; gap: 5px; font-size: 16px;
    }
    .voice-bubble {
        display: flex; gap: 10px; background: #fefce8; padding: 8px;
        border-radius: 10px; font-family: 'Yomogi', cursive; margin-top: 10px;
    }
    .char-icon {
        width: 40px; height: 40px; background: #fff; border: 1px solid #57534e;
        border-radius: 50%; flex-shrink: 0; display: flex; align-items: center; justify-content: center; font-size: 9px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. ロジック計算 ---
i_diff = i_exp - i_avg
i_diff_str = f"+{i_diff}%" if i_diff >= 0 else f"{i_diff}%"
needle_angle = (i_exp - 50) * 1.8 
i_rank = "S：鬼絞り" if i_diff >= 15 else "A：有力"

# 初音の配当カラー
odds_color = "#ef4444" if h_odds_diff > 0 else "#3b82f6"

# --- 4. HTML構築 ---
html_content = (
    '<div class="newspaper-base">'
    '  '
    '  <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 25px;">'
    '    <div style="background: #ffecd2; padding: 5px 30px; border-radius: 3px; border: 1px solid #57534e;">'
    '      <span style="font-size: 28px; font-weight: bold;">💎 Birthstones新聞</span>'
    '    </div>'
    f'    <div style="text-align: right; font-size: 11px;">{formatted_date} 第16号<br>🧭 3年1組 予想係</div>'
    '  </div>'
    
    '  <div style="display: flex; gap: 20px;">'
    '    '
    '    <div style="flex: 1.6;">'
    '      <div class="memo-box" style="background: #fffcf5; border-color: #f59e0b;">'
    '        <div class="box-title">🚩 特集：一果のイン逃げ精密判定</div>'
    f'        <p style="font-size: 12px; margin: 0;">場所：ボートレース<b>{i_place}</b> ({i_race})</p>'
    '        <div style="display: flex; justify-content: space-around; align-items: center; margin: 15px 0;">'
    '          <div style="text-align: center;">'
    '            <div class="meter-container">'
    '              <div class="meter-arc"></div>'
    f'              <div class="meter-needle" style="transform: translateX(-50%) rotate({needle_angle}deg);"></div>'
    '            </div>'
    f'            <div style="font-size: 11px;">逃げ期待値: {i_exp}%</div>'
    '          </div>'
    '          <div style="text-align: center;">'
    f'            <span style="font-size: 11px; color: #64748b;">場平均より</span><br>'
    f'            <span style="font-size: 32px; font-weight: bold; color: #ef4444;">{i_diff_str}</span><br>'
    f'            <div style="border: 2px double #ef4444; color: #ef4444; font-weight: bold; padding: 2px 8px; transform: rotate(-5deg); margin-top: 10px;">{i_rank}</div>'
    '          </div>'
    '        </div>'
    '        <div class="voice-bubble">'
    '          <div class="char-icon">一果</div>'
    f'          <div style="font-size: 13px;">「{i_text}」</div>'
    '        </div>'
    '      </div>'
    '    </div>'

    '    '
    '    <div style="flex: 1.4;">'
    '      '
    '      <div class="memo-box" style="border-color: #3b82f6; background: #f0f9ff; padding: 12px;">'
    '        <div class="box-title" style="color: #3b82f6; border-color: #3b82f6;">📚 初音の客観的分析</div>'
    '        <div style="font-size: 12px; margin-bottom: 8px;">'
    f'          ⚡️ <b>{h_wind_msg}</b><br>'
    f'          💰 期待配当の歪み：<span style="color:{odds_color}; font-weight:bold;">{"+ " if h_odds_diff > 0 else ""}{h_odds_diff}円</span>'
    '        </div>'
    '        <table class="hatsune-table">'
    '          <tr><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th></tr>'
    f'         <tr><td>{h_evals[0]}</td><td>{h_evals[1]}</td><td>{h_evals[2]}</td><td>{h_evals[3]}</td><td>{h_evals[4]}</td><td>{h_evals[5]}</td></tr>'
    '        </table>'
    '        <div class="voice-bubble" style="background: #f8fafc; border: 1px solid #cbd5e0; margin-top: 10px;">'
    '          <div class="char-icon">初音</div>'
    f'          <div style="font-size: 12px;">「{h_text}」</div>'
    '        </div>'
    '      </div>'

    '      '
    '      <div class="memo-box" style="border-color: #eab308; background: #fffdf0; padding: 12px;">'
    '        <div class="box-title" style="color: #854d0e;">⚡ キイナの展開破壊！</div>'
    f'        {"<div style=\"background:#fffbeb; border:2px dashed #f59e0b; animation:flash 1.5s infinite; padding:5px; text-align:center; font-size:11px; margin-bottom:8px;\">⚠️ 伸び足 +"+str(k_nobi)+"% 突破！ ⚠️</div>" if k_nobi >= 10 else ""}'
    f'        <div style="text-align: center; margin-bottom: 8px;"><span style=\"background:#ef4444; color:white; padding:3px 10px; border-radius:5px; font-weight:bold; font-size:16px;\">{k_eval}</span></div>'
    '        <div class="voice-bubble" style="background:#fff; border:1px solid #fef08a;">'
    '          <div class="char-icon">キイナ</div>'
    f'          <div style="font-size: 12px;">「{k_text}」</div>'
    '        </div>'
    '      </div>'
    '    </div>'
    '  </div>'
    '  <div style="text-align: center; margin-top: 15px; font-size: 10px; color: #94a3b8;">(c) BOAT STRIKE - 3人の秘密基地・学級新聞係</div>'
    '  <style>@keyframes flash { 0%, 100% { opacity: 1; } 50% { opacity: 0.6; } }</style>'
    '</div>'
)

st.markdown(html_content, unsafe_allow_html=True)
