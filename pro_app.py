import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="BOAT AI（無料版）", layout="wide")

# ------------------
# Google Sheets 接続
# ------------------
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope,
)

gc = gspread.authorize(credentials)

SPREADSHEET_KEY = st.secrets["spreadsheet_key"]
sh = gc.open_by_key(SPREADSHEET_KEY)

st.title("🚤 BOAT AI（無料版）")

tab1, tab2, tab3 = st.tabs([
    "📊 基本予想",
    "🌊 条件補正",
    "🗂 データ状況"
])

with tab3:

    st.subheader("🗂 データ読み込み状況")

    try:
        ws = sh.worksheet("管理用_NEW")
        df = pd.DataFrame(ws.get_all_records())

        st.write("総レコード数：", len(df))
        st.dataframe(df.head(20))

    except Exception as e:
        st.error("シートが読み込めません")
        st.exception(e)

