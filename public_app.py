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

# --- タブ2：統計解析・補正シミュレーション ---
with tab_stat:
      st.subheader("補正展示タイム（会場別・蓄積データ）")

    places = sorted(df["場"].dropna().unique())
    selected_place = st.selectbox("会場を選択", places)

    df_place = df[df["場"] == selected_place].copy()

    st.header("展示タイム補正シミュレーション")

    # ============================
    # ① 仮の補正値（号艇別平均補正）
    # ※ 後で蓄積データから作る想定
    # ============================
    mean_each_boat = pd.Series(
        [0.000, 0.020, 0.030, 0.050, 0.070, 0.090],
        index=[1, 2, 3, 4, 5, 6]
    )

    # ============================
    # ② 入力欄
    # ============================
    st.subheader("展示タイム")

    ex_times = []
    cols = st.columns(6)
    for i in range(6):
        with cols[i]:
            v = st.number_input(
                f"{i+1}号艇",
                value=6.50,      # 初期値
                step=0.01,
                min_value=0.00,
                key=f"tab2_ex_{i+1}"
            )
            ex_times.append(v)

    st.subheader("直線タイム")

    st_times = []
    cols = st.columns(6)
    for i in range(6):
        with cols[i]:
            v = st.number_input(
                f"{i+1}号艇",
                value=6.50,
                step=0.01,
                min_value=0.00,
                key=f"tab2_st_{i+1}"
            )
            st_times.append(v)

    st.subheader("1周タイム")

    lap_times = []
    cols = st.columns(6)
    for i in range(6):
        with cols[i]:
            v = st.number_input(
                f"{i+1}号艇",
                value=37.0,
                step=0.1,
                min_value=0.0,
                key=f"tab2_lap_{i+1}"
            )
            lap_times.append(v)

    # ============================
    # ③ 今日データ作成
    # ============================
    df_today = pd.DataFrame({
        "号艇": [f"{i}号艇" for i in range(1, 7)],
        "展示タイム": ex_times,
        "直線タイム": st_times,
        "1周タイム": lap_times,
        "補正値": mean_each_boat.values
    })

    # ============================
    # ④ 補正展示タイム
    # ============================
    df_today["補正展示タイム"] = (
        df_today["展示タイム"] + df_today["補正値"]
    )

    # ============================
    # ⑤ 順位
    # （小さいほど良い）
    # ============================
    df_today["展示順位"] = df_today["補正展示タイム"].rank(
        method="min", ascending=True
    ).astype(int)

    df_today["直線順位"] = df_today["直線タイム"].rank(
        method="min", ascending=True
    ).astype(int)

    df_today["1周順位"] = df_today["1周タイム"].rank(
        method="min", ascending=True
    ).astype(int)

    # ============================
    # ⑥ 色付け
    # ============================
    def highlight_rank(col):
        styles = []
        for v in col:
            if v == 1:
                styles.append("background-color:#ffcccc")   # 1位 赤
            elif v == 2:
                styles.append("background-color:#fff2cc")   # 2位 黄
            else:
                styles.append("")
        return styles

    styled = (
        df_today
        .style
        .format({
            "展示タイム": "{:.2f}",
            "直線タイム": "{:.2f}",
            "1周タイム": "{:.1f}",
            "補正値": "{:.3f}",
            "補正展示タイム": "{:.3f}"
        })
        .apply(highlight_rank, subset=["展示順位"])
        .apply(highlight_rank, subset=["直線順位"])
        .apply(highlight_rank, subset=["1周順位"])
    )

    # ============================
    # ⑦ 表示
    # ============================
    st.subheader("公式ページ風 比較表")

    st.dataframe(
        styled,
        use_container_width=True
    )
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


















