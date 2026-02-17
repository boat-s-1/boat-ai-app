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
st.set_page_config(page_title="競艇予想 Pro Cloud", page_icon="🚤", layout="wide")

# 定数
BOATS = [1, 2, 3, 4, 5, 6]
# 記号のリストと点数
MARK_LIST = ["⭐", "◎", "◯", "▪️", "△", "✖️"]
MARK_SCORE = {"⭐": 6, "◎": 5, "◯": 4, "▪️": 3, "△": 2, "✖️": 1}

# --- 2. カード表示関数 ---
def show_rank_card(rank, boat, percent, score):
    medal = ["🥇", "🥈", "🥉", "4位", "5位", "6位"]
    icon = medal[rank-1]
    
    if percent >= 22:
        bg = "linear-gradient(135deg, #fff1b8, #ffd700)"
        border = "2px solid #ffb700"
        badge = "💮 本命候補"
    elif percent >= 18:
        bg = "linear-gradient(135deg, #ffe6f2, #ffd1ea)"
        border = "1px solid #ffb0c4"
        badge = "✨ 対抗"
    else:
        bg = "#ffffff"
        border = "1px solid #ddd"
        badge = ""

    html = f"""
    <div style="border-radius:15px; padding:15px; margin-bottom:10px; background:{bg}; border:{border}; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <div style="font-size:18px; font-weight:bold; color:#333;">{icon} {boat}号艇</div>
        <div style="font-size:22px; font-weight:bold; color:#ff2f92; margin:5px 0;">期待度: {percent:.1f}%</div>
        <div style="font-size:12px; color:#666;">合計スコア: {score}点 <span style="float:right; font-weight:bold; color:#d63384;">{badge}</span></div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# データ読み込み（省略可）
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

st.title("🚤 競艇予想 Pro Cloud")

tab1, tab2, tab3 = st.tabs(["📋 簡易版（記号）", "📊 詳細版（数値）", "📈 クラウド登録"])

# ===============================
# 1. 簡易版（1号艇〜6号艇 順次入力）
# ===============================
with tab1:
    st.subheader("記号評価（基準：▪️）")
    simple_scores = {}
    
    # 1号艇から6号艇まで縦に並べる（1艇1行）
    for i in range(1, 7):
        with st.expander(f"🚤 {i}号艇 の評価入力", expanded=True):
            cols = st.columns(4)
            # index=3 は "▪️" (リストの4番目)
            m = cols[0].selectbox("モーター", MARK_LIST, index=3, key=f"sm_{i}")
            w = cols[1].selectbox("当地勝率", MARK_LIST, index=3, key=f"sw_{i}")
            s = cols[2].selectbox("スタート", MARK_LIST, index=3, key=f"ss_{i}")
            e = cols[3].selectbox("展示気配", MARK_LIST, index=3, key=f"se_{i}")
            simple_scores[i] = MARK_SCORE[m] + MARK_SCORE[w] + MARK_SCORE[s] + MARK_SCORE[e]

    st.divider()
    
    # ランキングカード表示（期待度順）
    total = sum(simple_scores.values())
    ranked = sorted(simple_scores.items(), key=lambda x: x[1], reverse=True)
    
    st.markdown("### 🏆 予想ランキング")
    card_cols = st.columns(6)
    for i, (boat, score) in enumerate(ranked, 1):
        with card_cols[i-1]:
            percent = (score / total * 100) if total > 0 else 0
            show_rank_card(i, boat, percent, score)

# ===============================
# 2. 詳細版（1号艇〜6号艇 順次入力）
# ===============================
with tab2:
    st.subheader("数値精密評価")
    
    # 重み設定
    with st.expander("⚖️ 重み調整（スライダー）"):
        w_cols = st.columns(4)
        wm = w_cols[0].slider("モーター重視", 0, 10, 5)
        ww = w_cols[1].slider("勝率重視", 0, 10, 5)
        ws = w_cols[2].slider("ST重視", 0, 10, 5)
        we = w_cols[3].slider("展示重視", 0, 10, 5)

    detail_scores = {}
    for i in range(1, 7):
        with st.expander(f"🚤 {i}号艇 の数値入力", expanded=True):
            cols = st.columns(4)
            m_v = cols[0].number_input("モーター点", 0.0, 10.0, 5.0, 0.1, key=f"dm_{i}")
            w_v = cols[1].number_input("勝率点", 0.0, 10.0, 5.0, 0.1, key=f"dw_{i}")
            s_v = cols[2].number_input("平均ST", 0.10, 0.30, 0.15, 0.01, key=f"ds_{i}")
            e_v = cols[3].number_input("展示タイム", 6.0, 7.5, 6.7, 0.01, key=f"de_{i}")
            
            # スコア計算
            detail_scores[i] = (m_v * wm) + (w_v * ww) + ((1/s_v) * ws) + ((1/e_v) * we)

    st.divider()
    
    total_d = sum(detail_scores.values())
    ranked_d = sorted(detail_scores.items(), key=lambda x: x[1], reverse=True)
    
    st.markdown("### 🏆 予想ランキング（詳細）")
    card_cols_d = st.columns(6)
    for i, (boat, score) in enumerate(ranked_d, 1):
        with card_cols_d[i-1]:
            percent_d = (score / total_d * 100) if total_d > 0 else 0
            show_rank_card(i, boat, percent_d, round(score, 1))

# ===============================
# 3. クラウド登録（変更なし）
# ===============================
with tab3:
    st.subheader("クラウド同期登録")
    if ws_obj is None:
        st.warning("スプレッドシートへの接続を確認中...")
    else:
        with st.form("reg_form", clear_on_submit=True):
            f_cols = st.columns(2)
            f_p = f_cols[0].selectbox("会場", ["桐生", "戸田", "江戸川", "平和島", "多摩川", "浜名湖", "蒲郡", "常滑", "津", "三国", "びわこ", "住之江", "尼崎", "鳴門", "丸亀", "児島", "宮島", "徳山", "下関", "若松", "芦屋", "福岡", "唐津", "大村"])
            f_r = f_cols[1].number_input("レースR", 1, 12, 1)
            
            st.write("各艇の「展示タイム差分」入力")
            d_cols = st.columns(6)
            f_ds = [d_cols[i].number_input(f"{i+1}差", -0.5, 0.5, 0.0, 0.01, key=f"diff_{i}") for i in range(6)]
            
            if st.form_submit_button("スプレッドシートへ保存", use_container_width=True):
                try:
                    new_row = [str(datetime.date.today()), f_p, int(f_r)] + [float(d) for d in f_ds]
                    ws_obj.append_rows([new_row])
                    st.success("✅ クラウドへ保存しました！")
                except Exception as e:
                    st.error(f"エラー: {e}")
