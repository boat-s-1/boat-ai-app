import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="競艇Pro 蒲郡", layout="wide")

PLACE_NAME = "蒲郡"

# 戻るボタン
if st.button("← 会場選択へ戻る", key="back_to_home_gamagori"):
    st.switch_page("public_app.py")

# -------------------------
# 認証
# -------------------------
def get_gsheet_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    try:
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=scopes
        )
        return gspread.authorize(credentials)
    except:
        return None


# ==============================
# レース種別選択
# ==============================
if "selected_place" not in st.session_state:
    st.session_state.selected_place = None

if st.session_state.selected_place is None:

    st.title("🏁 レース種別を選択")

    cols = st.columns(4)

    if cols[0].button("混合戦", use_container_width=True):
        st.session_state.selected_place = "蒲郡混合戦"
        st.rerun()

    if cols[1].button("女子戦", use_container_width=True):
        st.session_state.selected_place = "蒲郡女子戦"
        st.rerun()

    cols[2].button("G1競走（準備中）", disabled=True, use_container_width=True)
    cols[3].button("SG競走（準備中）", disabled=True, use_container_width=True)

    st.stop()


# ==============================
# ここから本体
# ==============================
place = st.session_state.selected_place
st.caption(f"選択中の会場：{place}")

SHEET_MAP = {
    "蒲郡混合戦": {
        "sheet1": "蒲郡_混合統計シート",
        "sheet2": "蒲郡_混合統計シート②"
    },
    "蒲郡女子戦": {
        "sheet1": "蒲郡_女子統計シート",
        "sheet2": "蒲郡_女子統計シート②"
    },
}

gc = get_gsheet_client()

if gc is None:
    st.error("Google認証に失敗しました")
    st.stop()

try:
    sh = gc.open_by_key("1lN794iGtyGV2jNwlYzUA8wEbhRwhPM7FxDAkMaoJss4")

    ws1 = sh.worksheet(SHEET_MAP[place]["sheet1"]) 
    ws2 = sh.worksheet(SHEET_MAP[place]["sheet2"])

    rows1 = ws1.get_all_records()
    rows2 = ws2.get_a ll_records()

    df = pd.DataFrame(rows1 + rows2)
    st.session_state["base_df"] = df
    
except Exception as e:
    st.error("シート読み込みエラー")
    st.exception(e)
    st.stop()


st.title("予想ツール")

st.write("読み込み件数")
st.write(len(df))
