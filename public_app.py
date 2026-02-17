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
    except:
        return None

# --- 2. ログイン機能 ---
def check_password():
    if "pwd_ok" not in st.session_state:
        st.session_state["pwd_ok"] = False
    if st.session_state["pwd_ok"]:
        return True
    
    st.title("🔐 競艇 Pro 解析ログイン")
    pwd = st.text_input("アクセスコードを入力してください", type="password")
    if st.button("ログイン"):
        if pwd == "boat-pro-777": # 必要に応じて変更してください
            st.session_state["pwd_ok"] = True
            st.rerun()
        else:
            st.error("コードが違います")
    return False

# --- メイン処理 ---
if check_password():
    st.set_page_config(page_title="競艇 Pro 解析パネル", layout="wide")
    
    # データ読み込み
    df = pd.DataFrame()
    gc = get_gsheet_client()
    if gc:
        try:
            sh = gc.open("競艇予想学習データ")
            raw = sh.get_worksheet(0).get_all_values()
            if len(raw) > 1:
                df = pd.DataFrame(raw[1:], columns=raw[0])
        except:
            st.error("データ読み込みに失敗しました。シート名を確認してください。")

    st.title("🚀 三連単機力解析システム")
    st.caption(f"現在の蓄積データ数: {len(df)} レース")

    tab1, tab2, tab3 = st.tabs(["🎯 リアルタイム解析", "📊 過去リスト", "📝 攻略メモ"])

    # --- Tab 1: リアルタイム解析 ---
    with tab1:
        col_in, col_res = st.columns([1, 2])
        
        with col_in:
            st.subheader("条件入力")
            place = st.selectbox("会場", ["大村", "若松", "多摩川", "蒲郡", "戸田", "江戸川", "平和島", "浜名湖", "常滑", "津", "三国", "びわこ", "住之江", "尼崎", "鳴門", "丸亀", "児島", "宮島", "徳山", "下関", "芦屋", "福岡", "唐津", "桐生"])
            wdir = st.selectbox("風向き", ["向い風", "追い風", "左横風", "右横風", "無風"])
            
            st.write("▼ 本日の展示タイム等を入力")
            # 解析用のタイム入力（ここでは簡易的に1つの代表タイムとして扱いますが、必要に応じて増やせます）
            times = []
            for i in range(1, 7):
                t = st.number_input(f"{i}号艇 タイム", 4.0, 15.0, 6.70, 0.01, key=f"t_{i}")
                times.append(t)
            
            btn = st.button("解析実行", use_container_width=True, type="primary")

        with col_res:
            if btn:
                # 1. 今回の機力偏差を計算
                fastest = min(times)
                diffs = [round(t - fastest, 3) for t in times]
                
                st.subheader("📊 解析結果")
                
                # 激アツ条件アラート（ロジック：タイム偏差が0.00の艇に注目）
                alert_triggered = False
                for i, d in enumerate(diffs):
                    if d == 0.00:
                        st.warning(f"🔥 【機力注目】{i+1}号艇が本日最速タイムをマーク！")
                        alert_triggered = True
                
                if alert_triggered:
                    st.balloons() # お祝い演出

                # 偏差のメトリクス表示
                d_cols = st.columns(6)
                for i, d in enumerate(diffs):
                    d_cols[i].metric(f"{i+1}号", f"{d:.2f}", delta=None)

                # 2. 過去データとの照合
                if not df.empty:
                    # 型変換を安全に行う
                    df["1着"] = pd.to_numeric(df["1着"], errors='coerce')
                    df["2着"] = pd.to_numeric(df["2着"], errors='coerce')
                    df["3着"] = pd.to_numeric(df["3着"], errors='coerce')
                    
                    match = df[(df["会場"] == place) & (df["風向き"] == wdir)]
                    
                    if not match.empty:
                        st.write(f"🔎 同条件の過去レース: {len(match)}件")
                        
                        res_list = []
                        w1 = match["1着"].tolist()
                        all_3 = w1 + match["2着"].tolist() + match["3着"].tolist()
                        
                        for i in range(1, 7):
                            r1 = (w1.count(i) / len(match)) * 100
                            r3 = (all_3.count(i) / len(match)) * 100
                            res_list.append({"号艇": f"{i}号艇", "1着率(%)": r1, "3連対率(%)": r3})
                        
                        res_df = pd.DataFrame(res_list)
                        fig = px.bar(res_df, x="号艇", y=["1着率(%)", "3連対率(%)"], 
                                     barmode="group",
                                     color_discrete_map={"1着率(%)": "#FF4B4B", "3連対率(%)": "#1F77B4"})
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("同条件（会場・風向き）の過去データがまだありません。データを蓄積中です！")

    # --- Tab 2: 過去リスト ---
    with tab2:
        st.subheader("蓄積データ一覧")
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            # ダウンロードボタン
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("CSVでダウンロード", csv, "boat_data.csv", "text/csv")
        else:
            st.write("データがありません。")

    # --- Tab 3: 攻略メモ ---
    with tab3:
        st.subheader("会場別攻略メモ")
        # 管理者アプリで保存したメモを表示するロジック
        try:
            ws_memo = sh.worksheet("攻略メモ")
            memo_data = ws_memo.get_all_values()
            if len(memo_data) > 1:
                memo_df = pd.DataFrame(memo_data[1:], columns=memo_data[0])
                for index, row in memo_df.iterrows():
                    with st.chat_message("user"):
                        st.write(f"**【{row['会場']}】** ({row['日付']})")
                        st.write(row['メモ'])
            else:
                st.write("メモはまだありません。")
        except:
            st.write("メモシートが見つかりません。")
