import streamlit as st
import pandas as pd
import numpy as np
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
tab_pre, tab_stat, tab_log, tab_memo = st.tabs(["⭐ 事前簡易予想", "📊 統計解析", "📜 過去ログ", "📝 攻略メモ"])

# --- タブ1：事前簡易予想（4項目評価） ---
with tab_pre:
    st.subheader("各艇の4項目・記号評価")
    st.caption("モーター・当地・枠番勝率・スタートを評価して期待度を算出します。")

    SYMBOL_VALUES = {"◎": 100, "○": 80, "▲": 60, "△": 40, "×": 20, "無": 0}
    WEIGHTS = {"モーター": 0.25, "当地勝率": 0.2, "枠番勝率": 0.3, "枠番スタート": 0.25}

    with st.form("pre_eval_form"):
        boat_evals = {}
        # 2艇ずつ横に並べて入力しやすく配置
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
                    
                    score = (SYMBOL_VALUES[m] * WEIGHTS["モーター"] +
                             SYMBOL_VALUES[t] * WEIGHTS["当地勝率"] +
                             SYMBOL_VALUES[w] * WEIGHTS["枠番勝率"] +
                             SYMBOL_VALUES[s] * WEIGHTS["枠番スタート"])
                    boat_evals[i] = round(score, 1)
        
        submitted = st.form_submit_button("予想カード生成 ＆ ランク付け", use_container_width=True, type="primary")

    if submitted:
        sorted_boats = sorted(boat_evals.items(), key=lambda x: x[1], reverse=True)
        st.write("### 🏁 総合期待度ランキング")
        res_cols = st.columns(3)
        rank_icons = ["🥇", "🥈", "🥉", "4th", "5th", "6th"]
        
        for idx, (boat_num, score) in enumerate(sorted_boats):
            with res_cols[idx % 3]:
                with st.container(border=True):
                    st.markdown(f"### {rank_icons[idx]} {boat_num}号艇")
                    st.metric("期待度", f"{score}%")
                    st.progress(score / 100)
                    if score >= 80: st.success("🔥 鉄板級")
                    elif score >= 50: st.info("✅ 狙い目")
        if sorted_boats[0][1] >= 85: st.balloons()

# -------------------------
# タブ2：統計解析（過去データ照合）
# -------------------------
with tab_stat:

    st.subheader("会場別 補正・総合順位")

    # =========================
    # 会場選択（消えていた部分）
    # =========================
    place_list = sorted(df["会場"].dropna().unique())
    place = st.selectbox("会場を選択", place_list)

    df_view = df[df["会場"] == place].copy()

    if len(df_view) == 0:
        st.warning("この会場のデータがありません")
        st.stop()

    st.write(f"対象データ件数：{len(df_view)} 件")

    # =========================
    # 数値化
    # =========================
    for b in range(1, 7):
        for c in ["展示", "直線", "一周", "回り足"]:
            col = f"{c}{b}"
            if col in df_view.columns:
                df_view[col] = pd.to_numeric(df_view[col], errors="coerce")

    # =========================
    # 各艇・各項目の平均
    # =========================
    mean_each_boat = {}

    for b in range(1, 7):
        mean_each_boat[b] = {}
        for c in ["展示", "直線", "一周", "回り足"]:
            col = f"{c}{b}"
            if col in df_view.columns:
                mean_each_boat[b][c] = df_view[col].mean()
            else:
                mean_each_boat[b][c] = np.nan

    # =========================
    # 入力
    # =========================
    st.markdown("### 補正前入力")

    input_data = {}

    cols = st.columns(6)
    for b in range(1, 7):
        with cols[b - 1]:
            st.markdown(f"#### {b}号艇")

            tenji = st.number_input(
                "展示",
                value=6.50,
                step=0.01,
                key=f"tenji_{b}"
            )

            chokusen = st.number_input(
                "直線",
                value=mean_each_boat[b]["直線"]
                if not np.isnan(mean_each_boat[b]["直線"]) else 6.90,
                step=0.01,
                key=f"choku_{b}"
            )

            isshu = st.number_input(
                "一周",
                value=mean_each_boat[b]["一周"]
                if not np.isnan(mean_each_boat[b]["一周"]) else 37.00,
                step=0.01,
                key=f"isshu_{b}"
            )

            mawari = st.number_input(
                "回り足",
                value=mean_each_boat[b]["回り足"]
                if not np.isnan(mean_each_boat[b]["回り足"]) else 5.00,
                step=0.01,
                key=f"mawari_{b}"
            )

            input_data[b] = {
                "展示": tenji,
                "直線": chokusen,
                "一周": isshu,
                "回り足": mawari
            }

    # =========================
    # 補正（平均との差）
    # =========================
    rows = []

    for b in range(1, 7):

        tenji_adj = input_data[b]["展示"] - mean_each_boat[b]["展示"]
        choku_adj = input_data[b]["直線"] - mean_each_boat[b]["直線"]
        isshu_adj = input_data[b]["一周"] - mean_each_boat[b]["一周"]
        mawari_adj = input_data[b]["回り足"] - mean_each_boat[b]["回り足"]

        total = tenji_adj + choku_adj + isshu_adj + mawari_adj

        rows.append({
            "号艇": f"{b}号艇",
            "展示(補正後)": round(tenji_adj, 3),
            "直線(補正後)": round(choku_adj, 3),
            "一周(補正後)": round(isshu_adj, 3),
            "回り足(補正後)": round(mawari_adj, 3),
            "総合スコア": round(total, 3)
        })

    result_df = pd.DataFrame(rows)

    # =========================
    # 順位
    # =========================
    result_df["順位"] = result_df["総合スコア"].rank(
        ascending=True,
        method="min"
    ).astype(int)

    result_df = result_df.sort_values("順位")

    st.markdown("### 補正後・総合順位")
    st.dataframe(result_df, use_container_width=True)

    # =========================
    # 信頼度（base_dfではなく df_view）
    # =========================
    st.markdown("### この会場データの信頼度")

    st.write(f"対象データ件数：{len(df_view)} 件")

    if len(df_view) >= 200:
        st.success("データ量：非常に多い（高信頼）")
    elif len(df_view) >= 100:
        st.info("データ量：十分あり（中〜高信頼）")
    elif len(df_view) >= 30:
        st.warning("データ量：やや少なめ（参考程度）")
    else:
        st.error("データ量が少ないため参考値です")
# --- タブ3：過去ログ ---
with tab_log:
    st.subheader("全レースデータ一覧")
    st.dataframe(df, use_container_width=True)

# --- タブ4：攻略メモ ---
with tab_memo:
    st.subheader("会場別メモ")
    try:
        ws_m = sh.worksheet("攻略メモ")
        m_data = ws_m.get_all_records()
        if m_data:
            for m in reversed(m_data):
                with st.chat_message("green"):
                    st.write(f"**{m['会場']}** ({m['日付']})")
                    st.write(m['メモ'])
    except: st.write("メモはありません。")








































