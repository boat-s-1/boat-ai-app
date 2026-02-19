import streamlit as st
import pandas as pd
import numpy as np
import os
import base64
import gspread
import plotly.express as px
from google.oauth2.service_account import Credentials
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def encode_image(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""

# --- 1. 認証 & 接続設定 ---
def get_gsheet_client():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
        return gspread.authorize(credentials)
    except: return None

# --- 2. ログイン機能 ---
if "pwd_ok" not in st.session_state: st.session_state["pwd_ok"] = False
if not st.session_state["pwd_ok"]:
    st.title("🔐 競艇 Pro 解析ログイン")
    pwd = st.text_input("アクセスコード", type="password")
    if st.button("ログイン"):
        if pwd == "boat-pro-777":
            st.session_state["pwd_ok"] = True
            st.rerun()
    st.stop()

# --- 3. データ読み込み ---
st.set_page_config(page_title="競艇 Pro 解析パネル", layout="wide")

df = pd.DataFrame()
gc = get_gsheet_client()

if gc:
    try:
        sh = gc.open("競艇予想学習データ")
        ws = sh.get_worksheet(0)
        raw_data = ws.get_all_values()
        if len(raw_data) > 1:
            df = pd.DataFrame(raw_data[1:], columns=raw_data[0])
    except: pass

st.title("🚤 競艇 Pro ハイブリッド解析システム")

# タブ構成
tab_pre, tab_stat, tab_log, tab_memo, tab5 = st.tabs(["⭐ 事前簡易予想", "📊 統計解析", "📜 過去ログ", "📝 攻略メモ","スタート予想"])

# --- タブ1：事前簡易予想 ---
with tab_pre:
    st.subheader("各艇の4項目・記号評価")
    SYMBOL_VALUES = {"◎": 100, "○": 80, "▲": 60, "△": 40, "×": 20, "無": 0}
    WEIGHTS = {"モーター": 0.25, "当地勝率": 0.2, "枠番勝率": 0.3, "枠番スタート": 0.25}

    with st.form("pre_eval_form"):
        boat_evals = {}
        for row in range(3):
            cols = st.columns(2)
            for col in range(2):
                i = row * 2 + col + 1
                with cols[col]:
                    st.markdown(f"#### {i}号艇")
                    m = st.selectbox("モーター", ["◎", "○", "▲", "△", "×", "無"], index=5, key=f"m_{i}")
                    t = st.selectbox("当地勝率", ["◎", "○", "▲", "△", "×", "無"], index=5, key=f"t_{i}")
                    w = st.selectbox("枠番勝率", ["◎", "○", "▲", "△", "×", "無"], index=5, key=f"w_{i}")
                    s = st.selectbox("枠番ST", ["◎", "○", "▲", "△", "×", "無"], index=5, key=f"s_{i}")
                    score = (SYMBOL_VALUES[m] * WEIGHTS["モーター"] + SYMBOL_VALUES[t] * WEIGHTS["当地勝率"] +
                             SYMBOL_VALUES[w] * WEIGHTS["枠番勝率"] + SYMBOL_VALUES[s] * WEIGHTS["枠番スタート"])
                    boat_evals[i] = round(score, 1)
        submitted = st.form_submit_button("予想カード生成", use_container_width=True, type="primary")

    if submitted:
        sorted_boats = sorted(boat_evals.items(), key=lambda x: x[1], reverse=True)
        res_cols = st.columns(3)
        for idx, (boat_num, score) in enumerate(sorted_boats[:6]):
            with res_cols[idx % 3]:
                st.metric(f"{boat_num}号艇", f"{score}%")

# --- タブ2：統計解析 ---
with tab_stat:
    st.subheader("会場別 補正・総合順位")
    if not df.empty:
        place_list = sorted(df["会場"].dropna().unique())
        place = st.selectbox("会場を選択", place_list, key="stat_place_select")
        df_view = df[df["会場"] == place].copy()

        # 数値化
        for b in range(1, 7):
            for c in ["展示", "直線", "一周", "回り足"]:
                col = f"{c}{b}"
                if col in df_view.columns:
                    df_view[col] = pd.to_numeric(df_view[col], errors="coerce")

        # 平均計算 & 入力
        mean_each_boat = {}
        cols = st.columns(6)
        input_data = {}
        for b in range(1, 7):
            mean_each_boat[b] = {c: df_view[f"{c}{b}"].mean() if f"{c}{b}" in df_view.columns else 0 for c in ["展示", "直線", "一周", "回り足"]}
            with cols[b - 1]:
                st.markdown(f"**{b}号艇**")
                tenji = st.number_input("展示", value=6.50, step=0.01, key=f"stat_tenji_{b}")
                input_data[b] = {"展示": tenji, "直線": 6.90, "一周": 37.0, "回り足": 5.0} # 簡易化

        # スコア計算表示
        st.write("補正計算結果を表示します...")
    else:
        st.warning("データが読み込めていません")

# --- タブ3：過去ログ ---
with tab_log:
    st.dataframe(df)

# --- タブ4：攻略メモ ---
with tab_memo:
    st.write("攻略メモ機能")

# --- タブ5：スタート予想 ---
with tab5:
    st.subheader("🚀 スタート予想")
    try:
        ws_new = sh.worksheet("管理用_NEW")
        data_new = ws_new.get_all_records()
        df_new = pd.DataFrame(data_new)

        if not df_new.empty:
            latest = df_new.sort_values("登録日時").tail(6)
            st.write("直近のスタート傾向")
            st.table(latest[["艇番", "ST", "スタート評価"]])
        else:
            st.info("管理用データがありません")
    except:
        st.error("管理用_NEW シートが見つかりません")
