import streamlit as st
import pandas as pd
import datetime
import gspread
import numpy as np
from google.oauth2.service_account import Credentials

# --- 1. 認証設定 ---
def get_gsheet_client():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        if "gcp_service_account" not in st.secrets:
            return None
        credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
        return gspread.authorize(credentials)
    except:
        return None

# --- ページ基本設定 ---
st.set_page_config(page_title="競艇予想 Pro Cloud + Data", page_icon="🚤", layout="wide")

# 定数
BOATS = [1, 2, 3, 4, 5, 6]
MARK_LIST = ["⭐", "◎", "◯", "▪️", "△", "✖️"]
MARK_SCORE = {"⭐": 6, "◎": 5, "◯": 4, "▪️": 3, "△": 2, "✖️": 1}
PLACES = ["桐生", "戸田", "江戸川", "平和島", "多摩川", "浜名湖", "蒲郡", "常滑", "津", "三国", "びわこ", "住之江", "尼崎", "鳴門", "丸亀", "児島", "宮島", "徳山", "下関", "若松", "芦屋", "福岡", "唐津", "大村"]

# --- 2. カード表示関数 ---
def show_rank_card(rank, boat, percent, score):
    medal = ["🥇", "🥈", "🥉", "4位", "5位", "6位"]
    icon = medal[rank-1]
    bg = "linear-gradient(135deg, #fff1b8, #ffd700)" if percent >= 22 else "linear-gradient(135deg, #ffe6f2, #ffd1ea)" if percent >= 18 else "#ffffff"
    border = "2px solid #ffb700" if percent >= 22 else "1px solid #ffb0c4" if percent >= 18 else "1px solid #ddd"
    
    html = f"""
    <div style="border-radius:15px; padding:15px; margin-bottom:10px; background:{bg}; border:{border}; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <div style="font-size:18px; font-weight:bold; color:#333;">{icon} {boat}号艇</div>
        <div style="font-size:22px; font-weight:bold; color:#ff2f92; margin:5px 0;">期待度: {percent:.1f}%</div>
        <div style="font-size:12px; color:#666;">合計スコア: {score}点</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# --- 3. 色付け用関数 ---
def highlight_times(df):
    def styling(col):
        is_best = col == col.min()
        is_second = col == col.nsmallest(2).iloc[-1]
        styles = []
        for b, s in zip(is_best, is_second):
            if b: styles.append('background-color: #ff4b4b; color: white; font-weight: bold')
            elif s: styles.append('background-color: #f1c40f; color: black; font-weight: bold')
            else: styles.append('')
        return styles
    return df.style.apply(styling, subset=["展示", "直線", "1周", "回り足"])

# データ読み込み
all_rows, ws_obj = (None, None)
try:
    gc = get_gsheet_client()
    if gc:
        sh = gc.open("競艇予想学習データ")
        ws = sh.get_worksheet(0)
        all_rows = ws.get_all_values()
        ws_obj = ws
except:
    pass

st.title("🚤 競艇予想 Pro Cloud + Data")

tab1, tab2, tab3, tab4 = st.tabs(["📋 簡易版", "📊 詳細版", "🕒 補正比較", "📈 的中データ登録"])

# (Tab1, Tab2, Tab3 は前回の内容を維持)
with tab1:
    st.subheader("記号評価（基準：▪️）")
    simple_scores = {}
    for i in range(1, 7):
        with st.expander(f"🚤 {i}号艇 の評価", expanded=True):
            cols = st.columns(4)
            m = cols[0].selectbox("モーター", MARK_LIST, index=3, key=f"sm_{i}")
            w = cols[1].selectbox("当地勝率", MARK_LIST, index=3, key=f"sw_{i}")
            s = cols[2].selectbox("スタート", MARK_LIST, index=3, key=f"ss_{i}")
            e = cols[3].selectbox("展示気配", MARK_LIST, index=3, key=f"se_{i}")
            simple_scores[i] = MARK_SCORE[m] + MARK_SCORE[w] + MARK_SCORE[s] + MARK_SCORE[e]
    total = sum(simple_scores.values())
    ranked = sorted(simple_scores.items(), key=lambda x: x[1], reverse=True)
    card_cols = st.columns(6)
    for i, (boat, score) in enumerate(ranked, 1):
        with card_cols[i-1]:
            percent = (score / total * 100) if total > 0 else 0
            show_rank_card(i, boat, percent, score)

with tab2:
    st.subheader("数値精密評価")
    with st.expander("⚖️ 重み調整"):
        w_cols = st.columns(4)
        wm, ww, ws, we = [w_cols[i].slider(["モーター","勝率","ST","展示"][i], 0, 10, 5) for i in range(4)]
    detail_scores = {}
    for i in range(1, 7):
        with st.expander(f"🚤 {i}号艇 数値", expanded=True):
            cols = st.columns(4)
            m_v = cols[0].number_input("モーター点", 0.0, 10.0, 5.0, 0.1, key=f"dm_{i}")
            w_v = cols[1].number_input("勝率点", 0.0, 10.0, 5.0, 0.1, key=f"dw_{i}")
            s_v = cols[2].number_input("平均ST", 0.10, 0.30, 0.15, 0.01, key=f"ds_{i}")
            e_v = cols[3].number_input("展示タイム", 6.0, 7.5, 6.7, 0.01, key=f"de_{i}")
            detail_scores[i] = (m_v * wm) + (w_v * ww) + ((1/s_v) * ws) + ((1/e_v) * we)
    total_d = sum(detail_scores.values())
    ranked_d = sorted(detail_scores.items(), key=lambda x: x[1], reverse=True)
    card_cols_d = st.columns(6)
    for i, (boat, score) in enumerate(ranked_d, 1):
        with card_cols_d[i-1]:
            percent_d = (score / total_d * 100) if total_d > 0 else 0
            show_rank_card(i, boat, percent_d, round(score, 1))

with tab3:
    st.subheader("タイム比較（1位:赤 / 2位:黄）")
    time_data = []
    for i in range(1, 7):
        with st.expander(f"🚤 {i}号艇 タイム入力", expanded=True):
            t_cols = st.columns(4)
            t_ex = t_cols[0].number_input("展示", 6.0, 7.5, 6.7, 0.01, key=f"tex_{i}")
            t_st = t_cols[1].number_input("直線", 6.0, 10.0, 7.0, 0.01, key=f"tst_{i}")
            t_lp = t_cols[2].number_input("1周", 34.0, 45.0, 37.0, 0.01, key=f"tlp_{i}")
            t_tn = t_cols[3].number_input("回り足", 3.0, 10.0, 5.0, 0.01, key=f"ttn_{i}")
            time_data.append([f"{i}号艇", t_ex, t_st, t_lp, t_tn])
    df_times = pd.DataFrame(time_data, columns=["号艇", "展示", "直線", "1周", "回り足"])
    st.table(highlight_times(df_times))

# ===============================
# 4. 的中データ登録（収益化に向けた強化項目）
# ===============================
with tab4:
    st.subheader("📈 レース結果と気象の登録")
    if ws_obj is None:
        st.warning("クラウド接続中...")
    else:
        with st.form("result_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            f_p = c1.selectbox("会場", PLACES)
            f_r = c2.number_input("レースR", 1, 12, 1)
            f_win = c3.selectbox("1着の号艇", BOATS) # 勝率計算に必須
            
            st.divider()
            st.write("🏁 気象条件（勝率の重み付けに重要）")
            w1, w2, w3 = st.columns(3)
            f_wdir = w1.selectbox("風向き", ["向い風", "追い風", "左横風", "右横風", "無風"])
            f_wspd = w2.number_input("風速 (m)", 0, 15, 0)
            f_wave = w3.number_input("波高 (cm)", 0, 50, 0)
            
            st.divider()
            st.write("⏱ 展示タイムの偏差（展示 - 節間平均など）")
            d_cols = st.columns(6)
            f_ds = [d_cols[i].number_input(f"{i+1}号艇", -0.5, 0.5, 0.0, 0.01, key=f"bias_{i}") for i in range(6)]
            
            if st.form_submit_button("的中分析用データを保存", use_container_width=True):
                try:
                    # [日付, 会場, レース, 1着号艇, 風向き, 風速, 波高, 1号艇偏差, 2号艇偏差, 3号艇偏差, 4号艇偏差, 5号艇偏差, 6号艇偏差]
                    new_row = [
                        str(datetime.date.today()), f_p, int(f_r), int(f_win), 
                        f_wdir, int(f_wspd), int(f_wave)
                    ] + [float(d) for d in f_ds]
                    
                    ws_obj.append_rows([new_row])
                    st.success(f"✅ 保存完了！ {f_p}{f_r}R のデータを蓄積しました。")
                except Exception as e:
                    st.error(f"保存失敗: {e}")
