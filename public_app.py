import streamlit as st
import pandas as pd
import re

def pick_cols(df, prefix):
    pattern = re.compile(rf"^{re.escape(prefix)}[1-6]$")
    return [c for c in df.columns if pattern.match(c)]
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

    st.subheader("統計解析（過去データ照合）")

    # -------------------------
    # 会場選択
    # -------------------------
    places = sorted(df["会場"].dropna().unique())
    place = st.selectbox("会場を選択してください", places)

    base_df = df[df["会場"] == place].copy()

    if base_df.empty:
        st.warning("この会場のデータがありません")
        st.stop()

    # -------------------------
    # 列取得用関数
    # -------------------------
    def pick_cols(df, prefix):
        cols = []
        for i in range(1, 7):
            c = f"{prefix}{i}"
            if c in df.columns:
                cols.append(c)
        return cols

    ex_cols   = pick_cols(base_df, "展示")
    line_cols = pick_cols(base_df, "直線")
    lap_cols  = pick_cols(base_df, "1周")
    turn_cols = pick_cols(base_df, "周り足")

    # 安全チェック
    if not ex_cols or not line_cols or not lap_cols or not turn_cols:
        st.error("必要な列が見つかりません")
        st.write("展示:", ex_cols)
        st.write("直線:", line_cols)
        st.write("1周:", lap_cols)
        st.write("周り足:", turn_cols)
        st.write("実際の列名:", list(base_df.columns))
        st.stop()

    # 数値化
    base_df[ex_cols]   = base_df[ex_cols].apply(pd.to_numeric, errors="coerce")
    base_df[line_cols] = base_df[line_cols].apply(pd.to_numeric, errors="coerce")
    base_df[lap_cols]  = base_df[lap_cols].apply(pd.to_numeric, errors="coerce")
    base_df[turn_cols] = base_df[turn_cols].apply(pd.to_numeric, errors="coerce")

    # -------------------------
    # 補正値（平均との差）
    # -------------------------
    def calc_adjust(cols):
        each_mean = base_df[cols].mean()
        all_mean  = base_df[cols].mean().mean()
        adjust = each_mean - all_mean
        return adjust, each_mean, all_mean

    adj_ex,   mean_ex_each,   mean_ex_all   = calc_adjust(ex_cols)
    adj_line, mean_line_each, mean_line_all = calc_adjust(line_cols)
    adj_lap,  mean_lap_each,  mean_lap_all  = calc_adjust(lap_cols)
    adj_turn, mean_turn_each, mean_turn_all = calc_adjust(turn_cols)

    st.markdown("### 会場別・補正値（平均との差）")

    stat_df = pd.DataFrame({
        "号艇": [f"{i}号艇" for i in range(1, 7)],
        "展示補正": adj_ex.values,
        "直線補正": adj_line.values,
        "1周補正": adj_lap.values,
        "周り足補正": adj_turn.values
    })

    st.dataframe(
        stat_df.style.format("{:.4f}"),
        use_container_width=True
    )

    st.caption(f"母数：{len(base_df)}件")

    st.markdown("---")
    st.markdown("## 今日の展示・直線・1周・周り足 補正シミュレーション")

    boats = [f"{i}号艇" for i in range(1, 7)]
    cols = st.columns(6)

    raw_ex   = []
    raw_line = []
    raw_lap  = []
    raw_turn = []

    for i in range(6):
        with cols[i]:
            st.markdown(f"### {i+1}号艇")
            raw_ex.append(
                st.number_input(
                    "展示",
                    value=6.50,
                    step=0.01,
                    key=f"today_ex_{i}"
                )
            )
            raw_line.append(
                st.number_input(
                    "直線",
                    value=6.80,
                    step=0.01,
                    key=f"today_line_{i}"
                )
            )
            raw_lap.append(
                st.number_input(
                    "1周",
                    value=37.00,
                    step=0.01,
                    key=f"today_lap_{i}"
                )
            )
            raw_turn.append(
                st.number_input(
                    "周り足",
                    value=0.00,
                    step=0.01,
                    key=f"today_turn_{i}"
                )
            )

    # -------------------------
    # 補正後
    # -------------------------
    corr_ex   = [raw_ex[i]   + adj_ex.values[i]   for i in range(6)]
    corr_line = [raw_line[i] + adj_line.values[i] for i in range(6)]
    corr_lap  = [raw_lap[i]  + adj_lap.values[i]  for i in range(6)]
    corr_turn = [raw_turn[i]+ adj_turn.values[i] for i in range(6)]

    result_df = pd.DataFrame({
        "号艇": boats,
        "展示": raw_ex,
        "補正展示": corr_ex,
        "直線": raw_line,
        "補正直線": corr_line,
        "1周": raw_lap,
        "補正1周": corr_lap,
        "周り足": raw_turn,
        "補正周り足": corr_turn
    })

    # -------------------------
    # 順位（小さいほど良い）
    # -------------------------
    result_df["展示順位"]   = result_df["補正展示"].rank(method="min")
    result_df["直線順位"]   = result_df["補正直線"].rank(method="min")
    result_df["1周順位"]    = result_df["補正1周"].rank(method="min")
    result_df["周り足順位"] = result_df["補正周り足"].rank(method="min")

    # -------------------------
    # 色付け（1位＝赤、2位＝黄色）
    # -------------------------
    def rank_color(v):
        if v == 1:
            return "background-color:#ff4d4d;color:white;"
        elif v == 2:
            return "background-color:#ffe066;"
        return ""

    st.markdown("### 補正後タイム（順位付き）")

    st.dataframe(
        result_df.style
        .format({
            "展示": "{:.2f}", "補正展示": "{:.3f}",
            "直線": "{:.2f}", "補正直線": "{:.3f}",
            "1周": "{:.2f}", "補正1周": "{:.3f}",
            "周り足": "{:.2f}", "補正周り足": "{:.3f}",
        })
        .applymap(
            rank_color,
            subset=["展示順位", "直線順位", "1周順位", "周り足順位"]
        ),
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































