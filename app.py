import streamlit as st
import pandas as pd
import gspread
import plotly.express as px
from google.oauth2.service_account import Credentials

def get_gsheet_client():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
        return gspread.authorize(credentials)
    except: return None

def check_password():
    if "pwd_ok" not in st.session_state: st.session_state["pwd_ok"] = False
    if st.session_state["pwd_ok"]: return True
    st.title("🔐 ログイン")
    pwd = st.text_input("コード", type="password")
    if st.button("ログイン"):
        if pwd == "boat-pro-777":
            st.session_state["pwd_ok"] = True
            st.rerun()
    return False

if check_password():
    st.set_page_config(page_title="競艇 Pro 解析", layout="wide")
    df = pd.DataFrame()
    gc = get_gsheet_client()
    if gc:
        try:
            sh = gc.open("競艇予想学習データ")
            raw = sh.get_worksheet(0).get_all_values()
            if len(raw) > 1: df = pd.DataFrame(raw[1:], columns=raw[0])
        except: pass

    st.title("🚀 三連単機力解析パネル")
    tab1, tab2 = st.tabs(["🎯 リアルタイム解析", "📊 過去リスト"])

    with tab1:
        col_in, col_res = st.columns([1, 2])
        with col_in:
            place = st.selectbox("会場", ["大村", "若松", "多摩川", "蒲郡", "戸田"])
            wdir = st.selectbox("風向き", ["向い風", "追い風", "左横風", "右横風", "無風"])
            times = [st.number_input(f"{i}号艇", 4.0, 9.0, 6.70, 0.01, key=f"t_{i}") for i in range(1, 7)]
            btn = st.button("解析実行", use_container_width=True)

        with col_res:
            if btn:
                # 偏差計算表示
                fastest = min(times); diffs = [round(t - fastest, 3) for t in times]
                st.write("▼ 機力偏差")
                d_cols = st.columns(6)
                for i, d in enumerate(diffs): d_cols[i].metric(f"{i+1}号艇", f"{d:.3f}")

                if not df.empty:
                    match = df[(df["会場"] == place) & (df["風向き"] == wdir)]
                    if not match.empty:
                        # 3連対率の集計
                        res = []
                        w1 = match["1着"].astype(int).tolist()
                        all_3 = w1 + match["2着"].astype(int).tolist() + match["3着"].astype(int).tolist()
                        for i in range(1, 7):
                            r1 = (w1.count(i) / len(match)) * 100
                            r3 = (all_3.count(i) / len(match)) * 100
                            res.append({"号艇": f"{i}号艇", "1着率": r1, "3連対率": r3})
                        
                        fig = px.bar(pd.DataFrame(res), x="号艇", y=["1着率", "3連対率"], barmode="group",
                                     color_discrete_map={"1着率": "#FF4B4B", "3連対率": "#1F77B4"})
                        st.plotly_chart(fig, use_container_width=True)
                    else: st.info("同条件の過去データなし")

    with tab2:
        st.dataframe(df, use_container_width=True)
