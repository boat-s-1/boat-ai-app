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

# -------------------------
# タブ2：統計解析（過去データ照合）
# -------------------------
with tab_stat:

      st.subheader("会場別 補正タイム解析（蓄積データ）")

    if df.empty:
        st.warning("データがありません")
        st.stop()

    # ----------------------------
    # 会場選択（消えていた部分）
    # ----------------------------
    place_list = sorted(df["会場"].dropna().unique())
    place = st.selectbox("会場を選択してください", place_list)

    base = df[df["会場"] == place].copy()

    st.caption(f"対象データ数：{len(base)}件")

    if len(base) < 5:
        st.warning("補正に使うデータが少なすぎます（最低5件推奨）")

    # ----------------------------
    # 数値化
    # ----------------------------
    ex_cols       = base.iloc[:, 9:15].apply(pd.to_numeric, errors="coerce")
    straight_cols = base.iloc[:, 15:21].apply(pd.to_numeric, errors="coerce")
    lap_cols      = base.iloc[:, 21:27].apply(pd.to_numeric, errors="coerce")
    turn_cols     = base.iloc[:, 27:33].apply(pd.to_numeric, errors="coerce")

    # ----------------------------
    # 艇別平均との差（補正値）
    # ----------------------------
    mean_each_boat_ex = ex_cols.mean() - ex_cols.mean().mean()
    mean_each_boat_st = straight_cols.mean() - straight_cols.mean().mean()
    mean_each_boat_lp = lap_cols.mean() - lap_cols.mean().mean()
    mean_each_boat_tr = turn_cols.mean() - turn_cols.mean().mean()

    corr_table = pd.DataFrame({
        "号艇": [f"{i}号艇" for i in range(1, 7)],
        "展示補正": mean_each_boat_ex.values,
        "直線補正": mean_each_boat_st.values,
        "一周補正": mean_each_boat_lp.values,
        "回り足補正": mean_each_boat_tr.values,
    })

    st.markdown("### 艇別補正値（平均との差）")

    st.dataframe(
        corr_table.style.format({
            "展示補正": "{:+.4f}",
            "直線補正": "{:+.4f}",
            "一周補正": "{:+.4f}",
            "回り足補正": "{:+.4f}",
        }),
        use_container_width=True
    )

    # ====================================================
    # 今日のシミュレーション
    # ====================================================
    st.markdown("---")
    st.markdown("## 今日の補正シミュレーション")

    st.markdown("### 展示タイム")

    cols = st.columns(6)
    today_ex = []

    for i in range(6):
        with cols[i]:
            today_ex.append(
                st.number_input(
                    f"{i+1}号艇",
                    value=6.50,
                    step=0.01,
                    key=f"today_ex_{i}"
                )
            )

    st.markdown("### 直線タイム")

    cols = st.columns(6)
    today_st = []

    for i in range(6):
        with cols[i]:
            today_st.append(
                st.number_input(
                    f"{i+1}号艇",
                    value=7.00,
                    step=0.01,
                    key=f"today_st_{i}"
                )
            )

    st.markdown("### 一周タイム")

    cols = st.columns(6)
    today_lp = []

    for i in range(6):
        with cols[i]:
            today_lp.append(
                st.number_input(
                    f"{i+1}号艇",
                    value=37.00,
                    step=0.01,
                    key=f"today_lp_{i}"
                )
            )

    st.markdown("### 回り足（評価値など）")

    cols = st.columns(6)
    today_tr = []

    for i in range(6):
        with cols[i]:
            today_tr.append(
                st.number_input(
                    f"{i+1}号艇",
                    value=5.00,
                    step=0.1,
                    key=f"today_tr_{i}"
                )
            )

    # ----------------------------
    # 補正適用
    # ----------------------------
    corr_ex = mean_each_boat_ex.values
    corr_st = mean_each_boat_st.values
    corr_lp = mean_each_boat_lp.values
    corr_tr = mean_each_boat_tr.values

    corrected_ex = [today_ex[i] + corr_ex[i] for i in range(6)]
    corrected_st = [today_st[i] + corr_st[i] for i in range(6)]
    corrected_lp = [today_lp[i] + corr_lp[i] for i in range(6)]
    corrected_tr = [today_tr[i] + corr_tr[i] for i in range(6)]

    # ----------------------------
    # 総合スコア
    # ※小さい方が良い指標はそのまま
    # ※回り足は大きい方が良い前提でマイナス化
    # ----------------------------
    total_score = []

    for i in range(6):
        s = (
            corrected_ex[i]
            + corrected_st[i]
            + corrected_lp[i]
            - corrected_tr[i]
        )
        total_score.append(s)

    result_today = pd.DataFrame({
        "号艇": [f"{i}号艇" for i in range(1, 7)],
        "展示(補正後)": corrected_ex,
        "直線(補正後)": corrected_st,
        "一周(補正後)": corrected_lp,
        "回り足(補正後)": corrected_tr,
        "総合スコア": total_score
    })

    # 順位（小さい方が良い）
    result_today["順位"] = result_today["総合スコア"].rank(method="min").astype(int)

    result_today = result_today.sort_values("順位")

    st.markdown("## 補正後・総合順位")

    st.dataframe(
        result_today.style.format({
            "展示(補正後)": "{:.3f}",
            "直線(補正後)": "{:.3f}",
            "一周(補正後)": "{:.3f}",
            "回り足(補正後)": "{:.3f}",
            "総合スコア": "{:.3f}",
        }),
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


































