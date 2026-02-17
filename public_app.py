import streamlit as st
import pandas as pd
import gspread
import plotly.express as px
from google.oauth2.service_account import Credentials

# --- 1. 認証 & 接続設定 ---
def get_gsheet_client():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
        return gspread.authorize(credentials)
    except: return None

# --- 2. ログイン機能 ---
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
            # データの読み込みをより柔軟にする
            ws = sh.get_worksheet(0)
            data = ws.get_all_records() # 見出しを自動認識して辞書形式で読み込む
            if data:
                df = pd.DataFrame(data)
        except Exception as e:
            st.error(f"データ読み込みエラー: {e}")

    st.title("🚀 三連単機力解析パネル")
    # ここでデータ件数を表示
    st.info(f"📊 現在の蓄積データ数: {len(df)} レース")

    tab1, tab2 = st.tabs(["🎯 リアルタイム解析", "📊 過去リスト"])

    with tab1:
        if df.empty:
            st.warning("スプレッドシートにデータが見つかりません。管理者アプリから登録するか、シートを確認してください。")
        else:
            col_in, col_res = st.columns([1, 2])
            with col_in:
                place = st.selectbox("会場", ["大村", "若松", "多摩川", "蒲郡", "戸田", "江戸川", "平和島", "浜名湖", "常滑", "津", "三国", "びわこ", "住之江", "尼崎", "鳴門", "丸亀", "児島", "宮島", "徳山", "下関", "芦屋", "福岡", "唐津", "桐生"])
                wdir = st.selectbox("風向き", ["向い風", "追い風", "左横風", "右横風", "無風"])
                times = [st.number_input(f"{i}号艇", 4.0, 15.0, 6.70, 0.01, key=f"t_{i}") for i in range(1, 7)]
                btn = st.button("解析実行", use_container_width=True)

            with col_res:
                if btn:
                    fastest = min(times); diffs = [round(t - fastest, 3) for t in times]
                    st.write("▼ 機力偏差")
                    d_cols = st.columns(6)
                    for i, d in enumerate(diffs): d_cols[i].metric(f"{i+1}号艇", f"{d:.3f}")

                    # 会場と風向きで絞り込み
                    match = df[(df["会場"] == place) & (df["風向き"] == wdir)]
                    if not match.empty:
                        res = []
                        # 列名を数値として取得
                        w1 = pd.to_numeric(match["1着"], errors='coerce').tolist()
                        w2 = pd.to_numeric(match["2着"], errors='coerce').tolist()
                        w3 = pd.to_numeric(match["3着"], errors='coerce').tolist()
                        all_3 = w1 + w2 + w3
                        
                        for i in range(1, 7):
                            r1 = (w1.count(i) / len(match)) * 100
                            r3 = (all_3.count(i) / len(match)) * 100
                            res.append({"号艇": f"{i}号艇", "1着率": r1, "3連対率": r3})
                        
                        fig = px.bar(pd.DataFrame(res), x="号艇", y=["1着率", "3連対率"], barmode="group",
                                     color_discrete_map={"1着率": "#FF4B4B", "3連対率": "#1F77B4"})
                        st.plotly_chart(fig, use_container_width=True)
                    else: st.info(f"{place}・{wdir} の過去データがまだありません。")

    with tab2:
        st.subheader("データ一覧")
        st.dataframe(df, use_container_width=True)
