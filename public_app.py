import streamlit as st
import pandas as pd
import gspread
import plotly.express as px
from google.oauth2.service_account import Credentials

# --- 1. 認証設定 ---
def get_gsheet_client():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        if "gcp_service_account" not in st.secrets: return None
        credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
        return gspread.authorize(credentials)
    except: return None

# --- 2. パスワード検問 ---
def check_password():
    if "pwd_ok" not in st.session_state: st.session_state["pwd_ok"] = False
    if st.session_state["pwd_ok"]: return True
    st.title("🔐 競艇予想 Pro ログイン")
    pwd = st.text_input("アクセスコードを入力", type="password")
    if st.button("ログイン"):
        if pwd == "boat-pro-777":
            st.session_state["pwd_ok"] = True
            st.rerun()
        else: st.error("コードが違います")
    return False

# --- 3. アプリ本体 ---
if check_password():
    st.set_page_config(page_title="競艇予想 Pro", layout="wide")
    
    # 共通データ読み込み
    df = pd.DataFrame()
    df_memo = pd.DataFrame()
    gc = get_gsheet_client()
    if gc:
        try:
            sh = gc.open("競艇予想学習データ")
            raw = sh.get_worksheet(0).get_all_values()
            if len(raw) > 1: df = pd.DataFrame(raw[1:], columns=raw[0])
            m_raw = sh.worksheet("攻略メモ").get_all_values()
            if len(m_raw) > 1: df_memo = pd.DataFrame(m_raw[1:], columns=m_raw[0])
        except: pass

    st.title("🚤 競艇予想 Pro 解析パネル")

    # タブの作成
    tab1, tab2, tab3 = st.tabs(["⚡ 簡易版", "📊 詳細分析版", "🎯 リアルタイム解析"])

    # --- Tab 1: 簡易版 (パッと見たい時) ---
    with tab1:
        st.subheader("シンプル機力チェック")
        c1, c2 = st.columns(2)
        target_p = c1.selectbox("会場選択", ["大村", "若松", "多摩川", "蒲郡", "戸田", "住之江", "尼崎", "鳴門", "丸亀", "福岡"], key="simple_p")
        if not df_memo.empty:
            memo = df_memo[df_memo["競艇場"] == target_p]
            if not memo.empty:
                st.success(f"📌 {target_p}のポイント: {memo.iloc[-1]['攻略内容']}")
        st.info("展示タイムだけを入力して、ざっくりした機力差を確認するモードです。")

    # --- Tab 2: 詳細分析版 (過去の統計) ---
    with tab2:
        st.subheader("📈 過去データ統計")
        if not df.empty:
            col_a, col_b = st.columns(2)
            sel_place = col_a.selectbox("分析する会場", df["会場"].unique())
            sel_win = col_b.multiselect("絞り込み(号艇)", ["1","2","3","4","5","6"], default=["1","2","3","4","5","6"])
            
            filtered_df = df[(df["会場"] == sel_place) & (df["1着号艇"].isin(sel_win))]
            st.write(f"該当レース数: {len(filtered_df)}件")
            st.dataframe(filtered_df.head(10), use_container_width=True)
        else:
            st.warning("データが蓄積されるとここに詳細な表が表示されます。")

    # --- Tab 3: リアルタイム機力解析 (メイン機能) ---
    with tab3:
        st.subheader("⏱ タイム差から的中率を算出")
        col_in, col_res = st.columns([1, 2])
        
        with col_in:
            p_now = st.selectbox("会場", ["大村", "若松", "多摩川", "蒲郡", "戸田", "平和島", "多摩川"], key="rt_p")
            w_dir = st.selectbox("風向き", ["向い風", "追い風", "左横風", "右横風", "無風"], key="rt_w")
            st.write("展示タイム入力")
            rt_times = [st.number_input(f"{i}号艇", 6.0, 7.5, 6.7, 0.01, key=f"rt_t_{i}") for i in range(1, 7)]
            calc_btn = st.button("解析実行", use_container_width=True)

        with col_res:
            if calc_btn:
                fastest = min(rt_times)
                diffs = [round(t - fastest, 3) for t in rt_times]
                
                # 偏差カード表示
                st.write("▼ 機力偏差（0.000が最速）")
                d_cols = st.columns(6)
                for idx, d in enumerate(diffs):
                    d_cols[idx].metric(f"{idx+1}号艇", f"{d:.3f}")
                
                # 的中率計算
                if not df.empty:
                    match = df[(df["会場"] == p_now) & (df["風向き"] == w_dir)]
                    if not match.empty:
                        rates = match["1着号艇"].value_counts(normalize=True) * 100
                        res_df = pd.DataFrame({
                            "号艇": [f"{i}号艇" for i in range(1, 7)],
                            "過去の的中率(%)": [round(rates.get(str(i), 0), 1) for i in range(1, 7)]
                        })
                        fig = px.bar(res_df, x="号艇", y="過去の的中率(%)", text="過去の的中率(%)", color="過去の的中率(%)", color_continuous_scale="Reds")
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("同条件の過去データがまだありません。")
