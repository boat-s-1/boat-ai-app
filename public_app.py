import streamlit as st
import pandas as pd
import gspread
import plotly.express as px
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

# --- 2. パスワード検問 ---
def check_password():
    if "pwd_ok" not in st.session_state:
        st.session_state["pwd_ok"] = False
    if st.session_state["pwd_ok"]: return True

    st.title("🔐 競艇予想 Pro ログイン")
    pwd = st.text_input("アクセスコードを入力", type="password")
    if st.button("ログイン"):
        if pwd == "boat-pro-777":
            st.session_state["pwd_ok"] = True
            st.rerun()
        else:
            st.error("コードが違います")
    return False

# --- 3. アプリ本体 ---
if check_password():
    st.set_page_config(page_title="競艇予想 Pro", layout="wide")
    
    # --- データ読み込み ---
    df = pd.DataFrame() # 初期化
    df_memo = pd.DataFrame() # 初期化
    
    gc = get_gsheet_client()
    if gc:
        try:
            sh = gc.open("競艇予想学習データ")
            # メインデータの取得
            raw_data = sh.get_worksheet(0).get_all_values()
            if len(raw_data) > 1:
                df = pd.DataFrame(raw_data[1:], columns=raw_data[0])
            
            # 攻略メモの取得
            memo_data = sh.worksheet("攻略メモ").get_all_values()
            if len(memo_data) > 1:
                df_memo = pd.DataFrame(memo_data[1:], columns=memo_data[0])
        except Exception as e:
            st.sidebar.error(f"データ連携エラー: {e}")

    # サイドバー（実績表示）
    with st.sidebar:
        st.header("📊 蓄積データ実績")
        if not df.empty:
            st.metric("解析済みレース", f"{len(df)} R")
            fig = px.pie(df, names="1着号艇", hole=0.4, title="直近の1着分布")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("まだ蓄積データがありません。管理者がデータを登録するとここにグラフが表示されます。")

    st.title("🚀 リアルタイム機力解析")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("条件設定")
        place = st.selectbox("会場", ["大村", "若松", "多摩川", "蒲郡", "戸田", "江戸川", "平和島", "浜名湖", "常滑", "津", "三国", "びわこ", "住之江", "尼崎", "鳴門", "丸亀", "児島", "宮島", "徳山", "下関", "芦屋", "福岡", "唐津", "桐生"])
        w_dir = st.selectbox("風向き", ["向い風", "追い風", "左横風", "右横風", "無風"])
        w_spd = st.slider("風速 (m)", 0, 10, 0)
        
        st.write("⏱ 展示タイム入力")
        times = [st.number_input(f"{i}号艇", 6.0, 7.5, 6.7, 0.01, key=f"p_{i}") for i in range(1, 7)]

    with col2:
        st.subheader("📉 解析結果")
        if st.button("過去データから的中期待値を算出", use_container_width=True):
            fastest = min(times)
            diffs = [round(t - fastest, 3) for t in times]
            
            # 偏差を表示
            st.write("▼ 本日の機力偏差（0.00が最速）")
            d_cols = st.columns(6)
            for idx, d in enumerate(diffs):
                d_cols[idx].metric(f"{idx+1}号艇", f"{d:.2f}")

            if not df.empty:
                match = df[(df["会場"] == place) & (df["風向き"] == w_dir)]
                if not match.empty:
                    st.write(f"🔎 似た条件の過去レース: {len(match)}件")
                    rates = match["1着号艇"].value_counts(normalize=True) * 100
                    res_df = pd.DataFrame({
                        "号艇": [f"{i}号艇" for i in range(1, 7)],
                        "的中率(%)": [round(rates.get(str(i), 0), 1) for i in range(1, 7)]
                    })
                    fig_res = px.bar(res_df, x="号艇", y="的中率(%)", text="的中率(%)", color="的中率(%)")
                    st.plotly_chart(fig_res, use_container_width=True)
                else:
                    st.info(f"大村の{w_dir}でのデータはまだありません。")
            else:
                st.warning("スプレッドシートにデータが1件もありません。まずは管理者アプリで1レース分保存してください。")

            if not df_memo.empty:
                memo = df_memo[df_memo["競艇場"] == place]
                if not memo.empty:
                    st.warning(f"📝 {place}の攻略メモ: {memo.iloc[-1]['攻略内容']}")
