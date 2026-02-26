import streamlit as st
import pandas as pd
import numpy as np
import os
import base64
import gspread
import plotly.express as px
from google.oauth2.service_account import Credentials
import datetime

# ★必ず最初に
st.set_page_config(page_title="競艇Pro 蒲郡", layout="wide")

# -------------------------
# 会場固定
# -------------------------
PLACE_NAME = "蒲郡"

# 戻るボタン
if st.button("← 会場選択へ戻る"):
    st.switch_page("public_app.py")
def encode_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def encode_image(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""
def highlight_rank(df):

    def _highlight(col):

        s = pd.to_numeric(col, errors="coerce")

        order = s.rank(method="min", ascending=True)

        styles = []
        for r in order:
            if pd.isna(r):
                styles.append("")
            elif r == 1:
                styles.append("background-color:#ff6b6b;color:white;")
            elif r == 2:
                styles.append("background-color:#ffd93d;")
            else:
                styles.append("")
        return styles

    return df.style.apply(_highlight, axis=0).format("{:.2f}")
# --- 1. 認証 & 接続設定 ---
def get_gsheet_client():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
        return gspread.authorize(credentials)
    except: return None
# --- 3. データ読み込み ---
# ==============================
# 会場トップページ
# ==============================
if "selected_place" not in st.session_state:
    st.session_state.selected_place = None

if st.session_state.selected_place is None:

    st.title("🏁 レース種別を選択")

cols = st.columns(4)

# 使えるボタン
# レース番号などの変数（例: race_no）をkeyに混ぜると確実に重複を避けられます
if cols[0].button("混合戦", use_container_width=True, key=f"btn_mixed_{PLACE_NAME}"):
    st.session_state.selected_place = "蒲郡混合戦"
    st.rerun()

if cols[1].button("女子戦", key="gamagori_top_joshi", use_container_width=True):
    st.session_state.selected_place = "蒲郡女子戦"
    st.rerun()

# 準備中（押せない）
cols[2].button("G1競走（準備中）", disabled=True, use_container_width=True)
cols[3].button("SG競走（準備中）", disabled=True, use_container_width=True)
if gc:
    try:
        sh = gc.open_by_key("1lN794iGtyGV2jNwlYzUA8wEbhRwhPM7FxDAkMaoJss4")

        ws1_name = SHEET_MAP[place]["sheet1"]
        ws2_name = SHEET_MAP[place]["sheet2"]

        ws1 = sh.worksheet(ws1_name)
        ws2 = sh.worksheet(ws2_name)

        rows1 = ws1.get_all_records()
        rows2 = ws2.get_all_records()

        all_rows = rows1 + rows2

        if len(all_rows) > 0:
            df = pd.DataFrame(all_rows)

    except Exception as e:
        st.error(e)
# ▼ スリット表示用CSS（ここに貼る）
st.markdown("""
<style>
.slit-area{
    background:#dff3ff;
    padding:20px;
    border-radius:12px;
    position:relative;
}

/* スタート基準ライン */
.slit-line{
    position:absolute;
    top:0;
    bottom:0;
    left:120px;
    width:3px;
    background:#ff5c5c;
    opacity:0.9;
}

.slit-row{
    display:flex;
    align-items:center;
    height:70px;
    position:relative;
    z-index:2;
}

.slit-boat{
    transition: all 0.4s ease;
    display:flex;
    align-items:center;
}
</style>
""", unsafe_allow_html=True)

df = pd.DataFrame()
gc = get_gsheet_client()

if gc:
    try:
        sh = gc.open_by_key("1lN794iGtyGV2jNwlYzUA8wEbhRwhPM7FxDAkMaoJss4")

        ws1 = sh.worksheet("統計シート")
        ws2 = sh.worksheet("統計シート②")

        rows1 = ws1.get_all_records()
        rows2 = ws2.get_all_records()

        all_rows = rows1 + rows2

        if len(all_rows) > 0:
            df = pd.DataFrame(all_rows)

    except Exception as e:
        st.error(e)
st.title("予想ツール")
