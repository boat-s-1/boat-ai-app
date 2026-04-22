import streamlit as st
import datetime

# ページ設定
st.set_page_config(page_title="Birthstones新聞 生成App", layout="wide")

# 日付
today = datetime.date.today()
formatted_date = today.strftime("%Y年%m月%d日")

# --- 1. サイドバー：入力 ---
st.sidebar.header("📊 新聞記事のデータ入力")

with st.sidebar.expander("⏱ 左エリア：展示タイム入力", expanded=True):
    i_place = st.text_input("レース場", value="住之江")
    i_race = st.text_input("レース番号", value="12R")
    
    st.write("各艇の【生展示タイム】")
    t_cols = st.columns(3)
    raw_times = []
    for i in range(6):
        raw_times.append(t_cols[i % 3].number_input(f"{i+1}号艇", value=6.50 + (i*0.02), step=0.01, format="%.2f"))
    
    st.write("独自補正値（イン補正・場補正など）")
    h_cols = st.columns(3)
    offsets = []
    for i in range(6):
        # デフォルトで1号艇だけマイナス補正がかかるように設定
        default_off = -0.03 if i == 0 else 0.00
        offsets.append(h_cols[i % 3].number_input(f"{i+1}補正", value=default_off, step=0.01, format="%.2f"))

# 3人の判定入力
with st.sidebar.expander("💎 右エリア：3人の個別判定", expanded=False):
    i_exp = st.slider("逃げ期待値 (%)", 30, 100, 78)
    i_text = st.text_area("一果の判定", value="1号艇の補正タイムが抜群です！")
    h_eval = st.text_input("初音の格付け", value="1=◯, 4=△, 5=✖️")
    h_text = st.text_area("初音の分析", value="タイム通り1号艇が軸。")
    k_eval = st.selectbox("穴判定", ["見", "GO", "買わなきゃ損！"], index=2)
    k_text = st.text_area("キイナの予感", value="4が凹めば5が突き抜ける！")

# --- 2. 補正タイム計算ロジック ---
final_times = []
for i in range(6):
    final_times.append(round(raw_times[i] + offsets[i], 2))

# 順位判定（1位と2位を特定）
sorted_times = sorted(list(set(final_times))) # 重複を除いて昇順ソート
best_time = sorted_times[0]
second_best = sorted_times[1] if len(sorted_times) > 1 else None

def get_bg_color(t):
    if t == best_time: return "#ef4444; color: white;" # 1位は赤
    if t == second_best: return "#fef08a; color: #854d0e;" # 2位は黄
    return "white; color: #334155;"

# --- 3. CSSスタイル ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Kosugi+Maru&family=Yomogi&display=swap');
    .stApp { font-family: 'Kosugi Maru', sans-serif; background-color: #fdfcf0; }
    .newspaper-base {
        background-color: #ffffff !important; width: 920px !important; margin: 0 auto !important;
        padding: 40px !important; border: 1.5px solid #d1d5db !important;
        box-shadow: 10px 10px 25px rgba(0,0,0,0.06) !important;
    }
    .data-table { width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 13px; }
    .data-table th { background: #f1f5f9; border: 1px solid #94a3b8; padding: 6px; }
    .data-table td { border: 1px solid #94a3b8; padding: 8px; text-align: center; font-weight: bold; font-size: 15px; }
    .memo-box { position: relative; border: 2px solid #57534e; border-radius: 10px; padding: 12px; background: #fff; margin-bottom: 15px; }
    .box-title { font-weight: bold; border-bottom: 2px dashed #57534e; margin-bottom: 8px; display: flex; align-items: center; gap: 5px; font-size: 15px; }
    .voice-mini { display: flex; gap: 8px; background: #fefce8; padding: 6px; border-radius: 8px; font-family: 'Yomogi', cursive; font-size: 12px; }
    .char-circle { width: 35px; height: 35px; background: #fff; border: 1px solid #57534e; border-radius: 50%; flex-shrink: 0; display: flex; align-items: center; justify-content: center; font-size: 8px; }
</style>
""", unsafe_allow_html=True)

# --- 4. HTML構築 ---
needle_angle = (i_exp - 50) * 1.8 

# テーブルの行を生成
raw_tds = "".join([f"<td>{t:.2f}</td>" for t in raw_times])
final_tds = "".join([f'<td style="background: {get_bg_color(t)}">{t:.2f}</td>' for t in final_times])

html_content = (
    f'<div class="newspaper-base">'
    '  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; border-bottom: 4px double #57534e; padding-bottom: 10px;">'
    '    <div style="font-size: 11px;">【号外】3年1組<br>BOAT STRIKE!</div>'
    '    <div style="font-size: 36px; font-weight: bold; letter-spacing: 4px;">💎 Birthstones新聞</div>'
    f'    <div style="text-align: right; font-size: 11px;">{formatted_date}<br>第19号 / タイム解析係</div>'
    '  </div>'
    
    '  <div style="display: flex; gap: 20px;">'
    '    '
    '    <div style="flex: 1.7;">'
    '      <div class="memo-box" style="background: #f8fafc; border-color: #64748b; min-height: 520px;">'
    '        <div class="box-title">📊 公式発表：展示タイム</div>'
    f'        <p style="font-size: 12px; margin: 0 0 5px 5px;">会場：{i_place} {i_race}（生データ）</p>'
    '        <table class="data-table">'
    '          <tr style="font-size:11px;"><th>1号</th><th>2号</th><th>3号</th><th>4号</th><th>5号</th><th>6号</th></tr>'
    f'         <tr>{raw_tds}</tr>'
    '        </table>'
    
    '        <div style="margin-top: 25px;" class="box-title">🔍 独自解析：補正展示タイム</div>'
    '        <div style="background: #fff; border: 2px solid #57534e; border-radius: 8px; padding: 12px;">'
    '          <p style="font-size: 11px; margin-bottom: 8px;">※場補正・イン有利度を加味した実戦タイム</p>'
    '          <table class="data-table">'
    '            <tr style="font-size:11px;"><th>1号</th><th>2号</th><th>3号</th><th>4号</th><th>5号</th><th>6号</th></tr>'
    f'           <tr>{final_tds}</tr>'
    '          </table>'
    '          <div style="margin-top: 10px; display: flex; gap: 15px; font-size: 11px;">'
    '            <span><b style="color:#ef4444;">■</b> 1番時計</span>'
    '            <span><b style="color:#eab308;">■</b> 2番時計</span>'
    '          </div>'
    '        </div>'
    '        <p style="font-size: 11px; color: #64748b; margin-top: 15px; font-style: italic;">※補正タイムは過去3年の気象条件データと連動しています。</p>'
    '      </div>'
    '    </div>'

    '    '
    '    <div style="flex: 1.3;">'
    '      <div class="memo-box" style="border-color: #f59e0b; background: #fffcf5;">'
    '        <div style="font-weight: bold; color: #f59e0b; font-size: 14px; margin-bottom: 5px;">🚩 一果のイン判定</div>'
    '        <div style="display: flex; align-items: center; gap: 10px;">'
    '          <div style="position: relative; width: 100px; height: 55px; border-bottom: 2px solid #57534e; overflow: hidden;">'
    '            <div style="width: 100px; height: 100px; border-radius: 50%; border: 8px solid #e2e8f0; border-bottom-color: transparent; border-left-color: #f87171; transform: rotate(45deg);"></div>'
    f'            <div style="position: absolute; bottom: 0; left: 50%; width: 2px; height: 45px; background: #1e293b; transform-origin: bottom center; transform: translateX(-50%) rotate({needle_angle}deg);"></div>'
    '          </div>'
    f'          <div style="font-size: 18px; font-weight: bold; color: #ef4444;">{i_exp}%</div>'
    '        </div>'
    '        <div class="voice-mini">'
    '          <div class="char-circle" style="background:#fff7ed">一果</div>'
    f'          <div>「{i_text}」</div>'
    '        </div>'
    '      </div>'

    '      <div class="memo-box" style="border-color: #3b82f6; background: #f0f9ff;">'
    '        <div style="font-weight: bold; color: #3b82f6; font-size: 14px; margin-bottom: 5px;">📚 初音の精密分析</div>'
    f'        <div style="background:#1e293b; color:white; padding:2px; text-align:center; border-radius:4px; font-size:12px; margin-bottom:5px;">{h_eval}</div>'
    '        <div class="voice-mini" style="background:#f8fafc; border:1px solid #cbd5e0;">'
    '          <div class="char-circle" style="background:#f0f9ff">初音</div>'
    f'          <div>「{h_text}」</div>'
    '        </div>'
    '      </div>'

    '      <div class="memo-box" style="border-color: #eab308; background: #fffdf0;">'
    '        <div style="font-weight: bold; color: #854d0e; font-size: 14px; margin-bottom: 5px;">⚡ キイナの穴予感</div>'
    f'        <div style="text-align:center; background:#ef4444; color:white; padding:2px; border-radius:4px; font-size:11px; font-weight:bold; margin-bottom:5px;">{k_eval}</div>'
    '        <div class="voice-mini" style="background:#fff; border:1px solid #fef08a;">'
    '          <div class="char-circle" style="background:#fffdf0">キイナ</div>'
    f'          <div>「{k_text}」</div>'
    '        </div>'
    '      </div>'
    '    </div>'
    '  </div>'
    '</div>'
)

st.markdown(html_content, unsafe_allow_html=True)
