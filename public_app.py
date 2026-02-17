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

if "pwd_ok" not in st.session_state: st.session_state["pwd_ok"] = False
if not st.session_state["pwd_ok"]:
    st.title("🔐 ログイン")
    pwd = st.text_input("コード", type="password")
    if st.button("ログイン"):
        if pwd == "boat-pro-777":
            st.session_state["pwd_ok"] = True
            st.rerun()
    st.stop()

st.set_page_config(page_title="競艇 Pro 解析", layout="wide")
df = pd.DataFrame()
gc = get_gsheet_client()

if gc:
    try:
        sh = gc.open("競艇予想学習データ")
        ws = sh.get_worksheet(0)
        # 最も確実な読み込み方法に変更
        raw_data = ws.get_all_values()
        if len(raw_data) > 1:
            df = pd.DataFrame(raw_data[1:], columns=raw_data[0])
    except Exception as e:
        st.error(f"読み込みエラー: {e}")

st.title("🚀 三連単機力解析パネル")
# --- 診断用コード：これを public_app.py の st.title の下あたりに入れてください ---
st.write("🔧 診断システム起動中...")

if gc is None:
    st.error("❌ 接続エラー：Googleサービスへの認証に失敗しています。Secretsを確認してください。")
else:
    try:
        sh = gc.open("競艇予想学習データ")
        st.success("✅ ファイルは見つかりました！")
        ws = sh.get_worksheet(0)
        raw = ws.get_all_values()
        st.write(f"シートの行数: {len(raw)}")
    except Exception as e:
        st.error(f"❌ ファイル読み込みエラー: {e}")
st.info(f"📊 現在の蓄積データ数: {len(df)} レース")

tab1, tab2 = st.tabs(["🎯 リアルタイム解析", "📊 過去リスト"])

with tab1:
    if df.empty:
        st.warning("データが読み込めていません。スプレッドシート名と中身を確認してください。")
    else:
        col_in, col_res = st.columns([1, 2])
        with col_in:
            place = st.selectbox("会場", ["若松", "大村", "多摩川", "蒲郡", "戸田", "江戸川", "平和島", "浜名湖", "常滑", "津", "三国", "びわこ", "住之江", "尼崎", "鳴門", "丸亀", "児島", "宮島", "徳山", "下関", "芦屋", "福岡", "唐津", "桐生"])
            wdir = st.selectbox("風向き", ["向い風", "追い風", "左横風", "右横風", "無風"])
            times = [st.number_input(f"{i}号艇", 4.0, 15.0, 6.70, 0.01, key=f"t_{i}") for i in range(1, 7)]
            btn = st.button("解析実行", use_container_width=True)

        with col_res:
            if btn:
                fastest = min(times); diffs = [round(t - fastest, 3) for t in times]
                st.write("▼ 今回の機力偏差")
                d_cols = st.columns(6)
                for i, d in enumerate(diffs): d_cols[i].metric(f"{i+1}号", f"{d:.3f}")

                # 絞り込み（列名が何であっても、左から2番目=会場、7番目=風向きとして扱う）
                m = df[(df.iloc[:, 1] == place) & (df.iloc[:, 6] == wdir)]
                if not m.empty:
                    res = []
                    # 1,2,3着の列（D,E,F列）を直接指定して集計
                    w1 = pd.to_numeric(m.iloc[:, 3], errors='coerce').tolist()
                    w2 = pd.to_numeric(m.iloc[:, 4], errors='coerce').tolist()
                    w3 = pd.to_numeric(m.iloc[:, 5], errors='coerce').tolist()
                    all_3 = w1 + w2 + w3
                    for i in range(1, 7):
                        r1 = (w1.count(i) / len(m)) * 100
                        r3 = (all_3.count(i) / len(m)) * 100
                        res.append({"号艇": f"{i}号艇", "1着率": r1, "3連対率": r3})
                    fig = px.bar(pd.DataFrame(res), x="号艇", y=["1着率", "3連対率"], barmode="group")
                    st.plotly_chart(fig, use_container_width=True)
                else: st.info("条件に合う過去データなし")

with tab2:
    st.dataframe(df, use_container_width=True)

