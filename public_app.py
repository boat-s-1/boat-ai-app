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

# --- タブ2：統計解析（過去データ照合・完全版） ---
with tab_stat:

       st.subheader("統計解析（過去データ照合）")

    # -------------------------
    # 会場選択（消えていたやつ）
    # -------------------------
    places = sorted(df["会場"].dropna().unique())
    place = st.selectbox("会場を選択してください", places)

    base_df = df[df["会場"] == place].copy()

    if base_df.empty:
        st.warning("この会場のデータがありません")
        st.stop()

    st.caption(f"対象データ数：{len(base_df)}件")

    # -------------------------
    # 使用列チェック
    # -------------------------
    need_cols = [
        "展示1","展示2","展示3","展示4","展示5","展示6",
        "直線1","直線2","直線3","直線4","直線5","直線6",
        "一周1","一周2","一周3","一周4","一周5","一周6",
        "回り足1","回り足2","回り足3","回り足4","回り足5","回り足6"
    ]

    missing = [c for c in need_cols if c not in base_df.columns]

    if missing:
        st.error("必要な列が見つかりません")
        st.write(missing)
        st.stop()

    for c in need_cols:
        base_df[c] = pd.to_numeric(base_df[c], errors="coerce")

    # -------------------------
    # 各艇ごとの平均との差（補正値）
    # -------------------------
    mean_each_boat = {}

    for i in range(1, 7):
        cols = [
            f"展示{i}",
            f"直線{i}",
            f"一周{i}",
            f"回り足{i}"
        ]
        mean_each_boat[i] = base_df[cols].mean().mean()

    mean_each_boat = pd.Series(mean_each_boat)

    st.markdown("### 会場別・各艇の平均値（参考）")
    st.dataframe(
        pd.DataFrame({
            "号艇": [f"{i}号艇" for i in range(1,7)],
            "平均との差平均": mean_each_boat.values
        }),
        use_container_width=True
    )

    st.markdown("---")
    st.markdown("## 今日のタイム入力")

    labels = ["展示","直線","一周","回り足"]
    today = {}

    for label in labels:
        st.markdown(f"### {label}")
        cols = st.columns(6)
        today[label] = []

        for i in range(6):
            with cols[i]:
                v = st.number_input(
                    f"{i+1}号艇",
                    value=6.50 if label=="展示" else 7.00,
                    step=0.01,
                    key=f"today_{label}_{i}"
                )
                today[label].append(v)

    # -------------------------
    # 補正後計算
    # -------------------------
    rows = []

    for i in range(6):
        row = {
            "号艇": f"{i+1}号艇",
            "展示(補正後)": today["展示"][i] + mean_each_boat[i+1],
            "直線(補正後)": today["直線"][i] + mean_each_boat[i+1],
            "一周(補正後)": today["一周"][i] + mean_each_boat[i+1],
            "回り足(補正後)": today["回り足"][i] + mean_each_boat[i+1],
        }

        row["総合スコア"] = (
            row["展示(補正後)"]
            + row["直線(補正後)"]
            + row["一周(補正後)"]
            + row["回り足(補正後)"]
        )

        rows.append(row)

    result_df = pd.DataFrame(rows)

    result_df["順位"] = result_df["総合スコア"].rank(method="min").astype(int)
    result_df = result_df.sort_values("順位")

    # -------------------------
    # 色付け用
    # -------------------------
    def highlight_top2(col):

        colors = [""] * len(col)

        order = col.sort_values(ascending=True).index.tolist()

        if len(order) >= 1:
            colors[col.index.get_loc(order[0])] = "background-color:#ffb3b3"
        if len(order) >= 2:
            colors[col.index.get_loc(order[1])] = "background-color:#fff2a8"

        return colors

    color_cols = [
        "展示(補正後)",
        "直線(補正後)",
        "一周(補正後)",
        "回り足(補正後)"
    ]

    styled = result_df.style.apply(
        highlight_top2,
        subset=color_cols
    ).format({
        "展示(補正後)": "{:.3f}",
        "直線(補正後)": "{:.3f}",
        "一周(補正後)": "{:.3f}",
        "回り足(補正後)": "{:.3f}",
        "総合スコア": "{:.3f}"
    })

    st.markdown("## 補正後・総合順位")
    st.dataframe(styled, use_container_width=True)

    # -------------------------
    # 信頼度表示（さっきエラー出てた所修正版）
    # -------------------------
    st.markdown("## この会場データの信頼度")

    st.write(f"対象データ件数：{len(base_df)}件")

    if len(base_df) >= 50:
        st.success("かなり信頼できます")
    elif len(base_df) >= 20:
        st.info("ある程度参考になります")
    else:
        st.warning("まだデータが少なめです")
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



























