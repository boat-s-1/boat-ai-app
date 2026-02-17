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
    df_view = df.copy()
    
    st.subheader("補正展示タイム（会場別・蓄積データ）")

    if df.empty:
        st.warning("蓄積データがありません")
        st.stop()

    if df_view.empty:
        st.warning("今日の表示データがありません")
        st.stop()

    # -----------------------------
    # 会場選択
    # -----------------------------
    places = sorted(df.iloc[:, 1].dropna().unique())
    race_place = st.selectbox("会場を選択してください", places)

    # -----------------------------
    # 会場で抽出（蓄積データ）
    # -----------------------------
    base = df[df.iloc[:, 1] == race_place]

    st.write(f"対象データ数：{len(base)} 件")

    if len(base) < 5:
        st.warning("補正に使うデータが少なすぎます（最低5件以上推奨）")
        st.stop()

    # =============================
    # 展示タイム差分（管理者保存分）
    # 9〜14列目が 1〜6号艇の差分
    # =============================
    ex_cols = base.iloc[:, 9:15].apply(pd.to_numeric, errors="coerce")

    # 号艇ごとの平均差分
    mean_each_boat = ex_cols.mean()

    st.markdown("### 会場別・展示タイム補正値（蓄積データより）")

    df_corr_table = pd.DataFrame({
        "号艇": [f"{i}号艇" for i in range(1, 7)],
        "補正値": mean_each_boat.values
    })

    st.dataframe(
        df_corr_table.style.format({"補正値": "{:.4f}"}),
        use_container_width=True
    )

    # =============================
    # 今日のレース用データ
    # =============================
    today_df = df_view.copy()

    # 念のため数値化
    for c in cols:
    if c in today_df.columns:
        today_df[c] = pd.to_numeric(today_df[c], errors="coerce")

    # -----------------------------
    # 会場平均との差（参考）
    # -----------------------------
    mean_exhibit_all = ex_cols.mean().mean()
    mean_straight = pd.to_numeric(base["直線"], errors="coerce").mean()
    mean_lap      = pd.to_numeric(base["一周"], errors="coerce").mean()
    mean_turn     = pd.to_numeric(base["回り足"], errors="coerce").mean()

    # -----------------------------
    # レーン補正係数
    # -----------------------------
    def lane_coef(lane):
        if lane == 1:
            return 0.7
        elif lane == 2:
            return 0.85
        else:
            return 1.0

    today_df["lane_coef"] = today_df["艇番"].apply(lane_coef)

    # -----------------------------
    # 補正値
    # （展示は号艇別補正値を使用）
    # -----------------------------
    today_df["展示補正値"] = mean_each_boat.values

    today_df["補正展示"] = today_df["展示"] + today_df["展示補正値"] * today_df["lane_coef"]
    today_df["補正直線"] = today_df["直線"] + (mean_straight - today_df["直線"]) * today_df["lane_coef"]
    today_df["補正一周"] = today_df["一周"] + (mean_lap - today_df["一周"]) * today_df["lane_coef"]
    today_df["補正回り足"] = today_df["回り足"] + (mean_turn - today_df["回り足"]) * today_df["lane_coef"]

    # -----------------------------
    # 順位（小さいほど良い）
    # -----------------------------
    today_df["展示順位"] = today_df["補正展示"].rank(method="min")
    today_df["直線順位"] = today_df["補正直線"].rank(method="min")
    today_df["一周順位"] = today_df["補正一周"].rank(method="min")
    today_df["回り足順位"] = today_df["補正回り足"].rank(method="min")

    st.markdown("### 今日の補正結果（蓄積データ反映）")

    show_cols = [
        "艇番",
        "展示", "補正展示", "展示順位",
        "直線", "補正直線", "直線順位",
        "一周", "補正一周", "一周順位",
        "回り足", "補正回り足", "回り足順位"
    ]

    st.dataframe(
        today_df[show_cols]
        .sort_values("補正展示")
        .style
        .format({
            "展示": "{:.2f}", "補正展示": "{:.3f}",
            "直線": "{:.2f}", "補正直線": "{:.3f}",
            "一周": "{:.2f}", "補正一周": "{:.3f}",
            "回り足": "{:.2f}", "補正回り足": "{:.3f}"
        })
        .applymap(
            lambda v: "background-color:#ff4d4d" if v == 1 else
                      "background-color:#ffe066" if v == 2 else "",
            subset=["展示順位", "直線順位", "一周順位", "回り足順位"]
        ),
        use_container_width=True
    )

    st.caption(f"{race_place} 補正母数：{len(base)}件")

    # ==================================================
    # 今日の手入力シミュレーション（初期値あり）
    # ==================================================
    st.markdown("---")
    st.markdown("## 今日の補正タイム入力シミュレーション")

    boats = [f"{i}号艇" for i in range(1, 7)]

    input_cols = st.columns(6)

    ex = []
    stl = []
    lap = []
    turn = []

    for i in range(6):
        with input_cols[i]:
            st.markdown(f"**{i+1}号艇**")
            ex.append(
                st.number_input("展示", value=6.50, step=0.01, key=f"sim_ex_{i}")
            )
            stl.append(
                st.number_input("直線", value=7.00, step=0.01, key=f"sim_st_{i}")
            )
            lap.append(
                st.number_input("一周", value=37.00, step=0.01, key=f"sim_lap_{i}")
            )
            turn.append(
                st.number_input("回り足", value=0.00, step=0.01, key=f"sim_turn_{i}")
            )

    sim_df = pd.DataFrame({
        "艇番": [1,2,3,4,5,6],
        "展示": ex,
        "直線": stl,
        "一周": lap,
        "回り足": turn
    })

    sim_df["lane_coef"] = sim_df["艇番"].apply(lane_coef)

    sim_df["展示補正値"] = mean_each_boat.values

    sim_df["補正展示"] = sim_df["展示"] + sim_df["展示補正値"] * sim_df["lane_coef"]
    sim_df["補正直線"] = sim_df["直線"] + (mean_straight - sim_df["直線"]) * sim_df["lane_coef"]
    sim_df["補正一周"] = sim_df["一周"] + (mean_lap - sim_df["一周"]) * sim_df["lane_coef"]
    sim_df["補正回り足"] = sim_df["回り足"] + (mean_turn - sim_df["回り足"]) * sim_df["lane_coef"]

    sim_df["展示順位"] = sim_df["補正展示"].rank(method="min")
    sim_df["直線順位"] = sim_df["補正直線"].rank(method="min")
    sim_df["一周順位"] = sim_df["補正一周"].rank(method="min")
    sim_df["回り足順位"] = sim_df["補正回り足"].rank(method="min")

    st.markdown("### 入力値から算出した補正結果")

    st.dataframe(
        sim_df[[
            "艇番",
            "展示","補正展示","展示順位",
            "直線","補正直線","直線順位",
            "一周","補正一周","一周順位",
            "回り足","補正回り足","回り足順位"
        ]]
        .sort_values("補正展示")
        .style
        .format({
            "展示": "{:.2f}", "補正展示": "{:.3f}",
            "直線": "{:.2f}", "補正直線": "{:.3f}",
            "一周": "{:.2f}", "補正一周": "{:.3f}",
            "回り足": "{:.2f}", "補正回り足": "{:.3f}"
        })
        .applymap(
            lambda v: "background-color:#ff4d4d" if v == 1 else
                      "background-color:#ffe066" if v == 2 else "",
            subset=["展示順位", "直線順位", "一周順位", "回り足順位"]
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
















