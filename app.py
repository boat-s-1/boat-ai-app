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
    st.write("各艇の展示タイム")
    t_cols = st.columns(3)
    times = [t_cols[i % 3].text_input(f"{i+1}号艇", value="6.52") for i in range(6)]
    
    st.write("独自補正データ")
    hosei_val = st.text_input("イン逃げ・場補正値", value="-0.03")
    final_time = st.text_input("補正後タイム（1号艇）", value="6.49")

with st.sidebar.expander("💎 右エリア：3人の個別判定", expanded=True):
    st.subheader("一果（右上）")
    i_exp = st.slider("逃げ期待値 (%)", 30, 100, 78)
    i_text = st.text_area("一果の判定", value="補正タイムが抜群！一果にお任せ！")
    
    st.subheader("初音（右中）")
    h_eval = st.text_input("格付け", value="1=◯, 4=△, 5=✖️")
    h_text = st.text_area("初音の分析", value="期待配当との乖離は軽微。")
    
    st.subheader("キイナ（右下）")
    k_eval = st.selectbox("穴判定", ["見", "GO", "買わなきゃ損！"], index=2)
    k_text = st.text_area("キイナの予感", value="4が凹めば5が突き抜ける！")

with st.sidebar.expander("🤝 最下部：トータル意見", expanded=False):
    total_verdict = st.text_input("最終結論タイトル", value="1頭固定の鉄板レース！")
    total_text = st.text_area("合議内容", value="3人の見解が「1頭」で一致。キイナの穴も5の連絡みまで。")

# --- 2. CSSスタイル定義 ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Kosugi+Maru&family=Yomogi&display=swap');
    .stApp { font-family: 'Kosugi Maru', sans-serif; background-color: #fdfcf0; }
    
    .newspaper-base {
        background-color: #ffffff !important;
        width: 920px !important; margin: 0 auto !important;
        padding: 40px !important; border: 1px solid #d1d5db !important;
        box-shadow: 10px 10px 25px rgba(0,0,0,0.06) !important;
        color: #334155 !important;
    }

    /* タイム表のデザイン */
    .data-table {
        width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 13px;
    }
    .data-table th { background: #f1f5f9; border: 1px solid #94a3b8; padding: 5px; }
    .data-table td { border: 1px solid #94a3b8; padding: 5px; text-align: center; font-weight: bold; }
    .hosei-highlight { background: #fee2e2; color: #ef4444; border: 2px solid #ef4444 !important; }

    /* ボックス装飾 */
    .memo-box {
        position: relative; border: 2px solid #57534e; border-radius: 10px;
        padding: 12px; background: #fff; margin-bottom: 15px;
    }
    .box-title {
        font-weight: bold; border-bottom: 2px dashed #57534e; margin-bottom: 8px;
        display: flex; align-items: center; gap: 5px; font-size: 15px;
    }
    .voice-mini {
        display: flex; gap: 8px; background: #fefce8; padding: 6px;
        border-radius: 8px; font-family: 'Yomogi', cursive; font-size: 12px;
    }
    .char-circle {
        width: 35px; height: 35px; background: #fff; border: 1px solid #57534e;
        border-radius: 50%; flex-shrink: 0; display: flex; align-items: center; justify-content: center; font-size: 8px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. HTML構築 ---
needle_angle = (i_exp - 50) * 1.8 

html_content = (
    '<div class="newspaper-base">'
    '  '
    '  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; border-bottom: 4px double #57534e; padding-bottom: 10px;">'
    '    <div style="font-size: 11px;">【秘】学級新聞<br>BOAT STRIKE!</div>'
    '    <div style="font-size: 36px; font-weight: bold; letter-spacing: 4px;">💎 Birthstones新聞</div>'
    f'    <div style="text-align: right; font-size: 11px;">{formatted_date}<br>第18号 / 編集係</div>'
    '  </div>'
    
    '  <div style="display: flex; gap: 20px;">'
    '    '
    '    <div style="flex: 1.7;">'
    '      <div class="memo-box" style="background: #f8fafc; border-color: #64748b; min-height: 500px;">'
    '        <div class="box-title">📊 公式発表：展示タイム表</div>'
    f'        <p style="font-size: 13px;">{i_place} {i_race} / 展示航走データ</p>'
    '        <table class="data-table">'
    '          <tr><th>1号艇</th><th>2号艇</th><th>3号艇</th><th>4号艇</th><th>5号艇</th><th>6号艇</th></tr>'
    f'         <tr><td>{times[0]}</td><td>{times[1]}</td><td>{times[2]}</td><td>{times[3]}</td><td>{times[4]}</td><td>{times[5]}</td></tr>'
    '        </table>'
    
    '        <div style="margin-top: 30px;" class="box-title">🔍 独自解析：補正展示タイム</div>'
    '        <div style="background: #fff; border: 2px solid #ef4444; border-radius: 8px; padding: 15px;">'
    '          <p style="font-size: 12px; margin-bottom: 10px;">過去の場別・風速データを加味したイン逃げ信頼度用タイム</p>'
    '          <table class="data-table">'
    '            <tr style="background:#fee2e2;"><th>1号艇 生タイム</th><th>イン補正</th><th>補正後タイム</th></tr>'
    f'           <tr><td>{times[0]}s</td><td>{hosei_val}s</td><td class="hosei-highlight">{final_time}s</td></tr>'
    '          </table>'
    '          <p style="font-size: 11px; color: #ef4444; margin-top: 5px;">※補正後タイムが{final_time}sを切るとイン逃げ成功率が急上昇します。</p>'
    '        </div>'
    '      </div>'
    '    </div>'

    '    '
    '    <div style="flex: 1.3;">'
    '      '
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

    '      '
    '      <div class="memo-box" style="border-color: #3b82f6; background: #f0f9ff;">'
    '        <div style="font-weight: bold; color: #3b82f6; font-size: 14px; margin-bottom: 5px;">📚 初音の精密分析</div>'
    f'        <div style="background:#1e293b; color:white; padding:2px; text-align:center; border-radius:4px; font-size:12px; margin-bottom:5px;">{h_eval}</div>'
    '        <div class="voice-mini" style="background:#f8fafc; border:1px solid #cbd5e0;">'
    '          <div class="char-circle" style="background:#f0f9ff">初音</div>'
    f'          <div>「{h_text}」</div>'
    '        </div>'
    '      </div>'

    '      '
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

    '  '
    '  <div class="memo-box" style="background: #f8fafc; border: 3px double #334155;">'
    '    <div style="font-weight: bold; font-size: 18px; display: flex; align-items: center; gap: 10px;">🤝 3人の放課後ミーティング</div>'
    '    <div style="margin-top: 10px; padding: 12px; background: white; border: 1.5px dashed #cbd5e0; border-radius: 8px;">'
    f'      <div style="font-weight: bold; color: #dc2626; margin-bottom: 5px;">{total_verdict}</div>'
    f'      <div style="font-size: 13px; font-family: \'Yomogi\', cursive;">{total_text}</div>'
    '    </div>'
    '  </div>'
    '  <div style="text-align: center; margin-top: 10px; font-size: 10px; color: #94a3b8;">(c) BOAT STRIKE - 学級新聞係</div>'
    '</div>'
)

st.markdown(html_content, unsafe_allow_html=True)
