import streamlit as st
import datetime

# ページ設定
st.set_page_config(page_title="Birthstones新聞 生成App", layout="wide")

# 日付
today = datetime.date.today()
formatted_date = today.strftime("%Y年%m月%d日")

# --- 1. サイドバー：全データ入力 ---
st.sidebar.header("📰 編集会議：全セクション入力")

with st.sidebar.expander("🚩 左エリア：一果 ＆ 補正タイム", expanded=True):
    i_place = st.text_input("レース場", value="住之江")
    i_race = st.text_input("レース番号", value="12R")
    st.write("--- 展示補正タイム ---")
    ori_time = st.text_input("オリ展タイム（秒）", value="6.52")
    hosei_time = st.text_input("イン逃げ補正タイム", value="-0.03")
    i_exp = st.slider("最終イン逃げ期待値 (%)", 30, 100, 78)
    i_text = st.text_area("一果の判定詳細", value="展示タイムが場平均を大きく上回っています！イン逃げ補正を含めても鉄板と言える数値です。")

with st.sidebar.expander("📊 右エリア：3人の個別コーナー", expanded=False):
    st.subheader("初音のデータ")
    h_eval = st.text_input("初音の格付け", value="1=◯, 4=△, 5=✖️")
    h_text = st.text_area("初音の分析", value="補正タイム1位。期待配当との乖離なし。")
    st.write("---")
    st.subheader("キイナの穴")
    k_eval = st.selectbox("穴判定", ["見", "GO", "買わなきゃ損！"], index=2)
    k_text = st.text_area("キイナの予感", value="4が凹めば5が突き抜ける！")

with st.sidebar.expander("🤝 最下部：トータル意見（3人の合議）", expanded=True):
    total_verdict = st.text_input("合議のタイトル", value="【結論】1号艇の独壇場。2、3着争い！")
    total_text = st.text_area("3人の合議内容", value="一果のイン逃げ鉄板判定と、初音のタイム分析が一致しました。キイナの穴狙いは今回抑え程度に留め、1頭固定で勝負できるレースです！")

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

    /* 補正タイムテーブル */
    .time-table {
        width: 100%; border-collapse: collapse; margin: 10px 0;
        font-size: 14px; background: #fff;
    }
    .time-table th { background: #fee2e2; border: 1px solid #f87171; padding: 6px; font-weight: bold; }
    .time-table td { border: 1px solid #f87171; padding: 6px; text-align: center; font-weight: bold; font-size: 16px; }

    /* ボックス装飾 */
    .memo-box {
        position: relative; border: 2px solid #57534e; border-radius: 12px;
        padding: 15px; background: #fff; margin-bottom: 18px;
    }
    .box-title {
        font-weight: bold; border-bottom: 2px dashed #57534e; margin-bottom: 10px;
        display: flex; align-items: center; gap: 6px; font-size: 16px;
    }
    .voice-bubble {
        display: flex; gap: 8px; background: #fefce8; padding: 8px;
        border-radius: 10px; font-family: 'Yomogi', cursive; font-size: 13px;
    }
    .char-icon {
        width: 38px; height: 38px; background: #fff; border: 1.5px solid #57534e;
        border-radius: 50%; flex-shrink: 0; display: flex; align-items: center; justify-content: center; font-size: 9px;
    }

    /* 最下部エリア */
    .total-box {
        background: #f8fafc !important; border: 3px double #334155 !important;
        margin-top: 10px; padding: 20px; border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. HTML構築 ---
needle_angle = (i_exp - 50) * 1.8 

html_content = (
    '<div class="newspaper-base">'
    '  '
    '  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; border-bottom: 4px double #57534e; padding-bottom: 10px;">'
    '    <div style="font-size: 12px;">【部外秘】3年1組<br>BOAT STRIKE新聞係</div>'
    '    <div style="font-size: 40px; font-weight: bold; letter-spacing: 5px;">💎 Birthstones新聞</div>'
    f'    <div style="text-align: right; font-size: 12px;">{formatted_date}<br>第17号 / 編集長 企画</div>'
    '  </div>'
    
    '  <div style="display: flex; gap: 20px;">'
    '    '
    '    <div style="flex: 1.8;">'
    '      <div class="memo-box" style="background: #fffcf5; border-color: #f59e0b; min-height: 480px;">'
    '        <div class="box-title">🚩 特集：一果の精密イン逃げ調査</div>'
    f'        <p style="font-size: 14px; margin-bottom: 15px;">対象：ボートレース<b>{i_place}</b> ({i_race})</p>'
    
    '        '
    '        <div style="background: #fff; border: 1px solid #f59e0b; padding: 10px; border-radius: 8px; margin-bottom: 20px;">'
    '          <span style="font-size: 12px; color: #b45309; font-weight: bold;">📊 展示補正タイム・データ</span>'
    '          <table class="time-table">'
    '            <tr><th>オリ展タイム</th><th>イン逃げ補正</th><th>最終評価</th></tr>'
    f'           <tr><td>{ori_time}s</td><td>{hosei_time}s</td><td style="color:red;">▲ {hosei_time}加速</td></tr>'
    '          </table>'
    '          <p style="font-size: 11px; color: #6b7280; margin-top: 5px;">※過去3年間の場別・風速別データから算出した独自補正値</p>'
    '        </div>'

    '        '
    '        <div style="display: flex; justify-content: space-around; align-items: center; margin-bottom: 20px;">'
    '          <div style="text-align: center;">'
    '            <div style="position: relative; width: 140px; height: 75px; border-bottom: 2px solid #57534e; overflow: hidden; margin: 0 auto;">'
    '              <div style="width: 140px; height: 140px; border-radius: 50%; border: 12px solid #e2e8f0; border-bottom-color: transparent; border-left-color: #f87171; border-top-color: #fca5a5; transform: rotate(45deg);"></div>'
    f'              <div style="position: absolute; bottom: 0; left: 50%; width: 3px; height: 60px; background: #1e293b; transform-origin: bottom center; transform: translateX(-50%) rotate({needle_angle}deg);"></div>'
    '            </div>'
    f'            <div style="font-size: 12px; margin-top: 5px;">逃げ信頼度: {i_exp}%</div>'
    '          </div>'
    '          <div style="text-align: center;">'
    '            <div style="border: 2px double #ef4444; color: #ef4444; font-weight: bold; padding: 10px; transform: rotate(-5deg);">'
    '              <span style="font-size: 12px;">一果ランク</span><br><span style="font-size: 24px;">S級：鬼絞り</span>'
    '            </div>'
    '          </div>'
    '        </div>'

    '        <div class="voice-bubble">'
    '          <div class="char-icon">一果</div>'
    f'          <div>「{i_text}」</div>'
    '        </div>'
    '      </div>'
    '    </div>'

    '    '
    '    <div style="flex: 1.2;">'
    '      '
    '      <div class="memo-box" style="border-color: #f59e0b; padding: 10px; background: #fffcf5;">'
    '        <div style="font-weight: bold; font-size: 14px; color: #f59e0b;">🧡 一果の守護</div>'
    '        <div style="font-size: 11px;">逃げ信頼度トップ。盤石の構えです。</div>'
    '      </div>'
    '      '
    '      <div class="memo-box" style="border-color: #3b82f6; background: #f0f9ff; padding: 10px;">'
    '        <div style="font-weight: bold; font-size: 14px; color: #3b82f6;">💙 初音の客観データ</div>'
    f'        <div style="background: #1e293b; color: white; padding: 3px; text-align: center; border-radius: 4px; font-size: 14px; margin: 5px 0;">{h_eval}</div>'
    f'        <div style="font-size: 11px; font-family: \'Yomogi\', cursive;">「{h_text}」</div>'
    '      </div>'
    '      '
    '      <div class="memo-box" style="border-color: #eab308; background: #fffdf0; padding: 10px;">'
    '        <div style="font-weight: bold; font-size: 14px; color: #854d0e;">💛 キイナの穴狙い</div>'
    f'        <div style="text-align: center; background:#ef4444; color:white; padding:2px; border-radius:4px; font-size:12px; font-weight:bold; margin:5px 0;">判定：{k_eval}</div>'
    f'        <div style="font-size: 11px; font-family: \'Yomogi\', cursive;">「{k_text}」</div>'
    '      </div>'
    '    </div>'
    '  </div>'

    '  '
    '  <div class="memo-box total-box">'
    '    <div style="display: flex; gap: 15px; align-items: center;">'
    '       <div style="display: flex; gap: -5px;">'
    '         <div class="char-icon" style="background:#fff7ed">一果</div>'
    '         <div class="char-icon" style="background:#f0f9ff">初音</div>'
    '         <div class="char-icon" style="background:#fffdf0">キイナ</div>'
    '       </div>'
    '       <div style="font-weight: bold; font-size: 18px; color: #1e293b;">🤝 3人の放課後ミーティング（トータル意見）</div>'
    '    </div>'
    '    <div style="margin-top: 15px; padding: 15px; background: white; border: 1.5px dashed #cbd5e0; border-radius: 8px;">'
    f'      <div style="font-weight: bold; font-size: 16px; color: #dc2626; margin-bottom: 8px;">{total_verdict}</div>'
    f'      <div style="font-size: 14px; line-height: 1.6; font-family: \'Yomogi\', cursive;">{total_text}</div>'
    '    </div>'
    '  </div>'
    
    '  <div style="text-align: center; margin-top: 15px; font-size: 11px; color: #94a3b8;">(c) BOAT STRIKE - Birthstones新聞係</div>'
    '</div>'
)

st.markdown(html_content, unsafe_allow_html=True)
