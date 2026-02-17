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

# ----------------------------
# タブ2：補正タイム（統計解析）
# ----------------------------
with tab_stat:

    st.subheader("補正展示・直線・一周・回り足（会場別統計）")

    if df.empty:
        st.warning("蓄積データがありません")
        st.stop()

    # ----------------------------
    # 会場選択
    # ----------------------------
    places = sorted(df["会場"].dropna().unique())
    selected_place = st.selectbox("会場を選択してください", places)

    base = df[df["会場"] == selected_place].copy()

    st.caption(f"対象データ数：{len(base)} 件")

    if len(base) < 5:
        st.warning("補正に使うデータが少なすぎます（5件以上推奨）")
        st.stop()

    # =====================================================
    # 展示タイム差分（管理者ページで保存している列）
    # 9～14列目（6艇分）
    # =====================================================
    ex_cols = base.iloc[:, 9:15].apply(pd.to_numeric, errors="coerce")

    # 各艇ごとの平均差分
    mean_each_exhibit = ex_cols.mean()

    st.markdown("### 会場別 展示タイム補正値（艇別）")

    df_bias = pd.DataFrame({
        "号艇": [f"{i}号艇" for i in range(1, 7)],
        "展示補正値": mean_each_exhibit.values
    })

    st.dataframe(
        df_bias.style.format({"展示補正値": "{:.4f}"}),
        use_container_width=True
    )

    # =====================================================
    # 直線・一周・回り足（会場平均との差）
    # ※ 現状は艇別差分を保存していない前提
    # =====================================================
    mean_straight = pd.to_numeric(base["直線"], errors="coerce").mean()
    mean_lap      = pd.to_numeric(base["一周"], errors="coerce").mean()
    mean_turn     = pd.to_numeric(base["回り足"], errors="coerce").mean()

    st.markdown("### 会場平均との差（参考）")

    st.write({
        "直線平均との差": round(mean_straight, 4),
        "一周平均との差": round(mean_lap, 4),
        "回り足平均との差": round(mean_turn, 4)
    })

    # =====================================================
    # 今日の補正シミュレーション
    # =====================================================
    st.markdown("---")
    st.markdown("## 今日の補正シミュレーション")

    boats = [1,2,3,4,5,6]

    cols = st.columns(6)

    raw_ex = []
    raw_st = []
    raw_lp = []
    raw_tr = []

    for i in range(6):
        with cols[i]:
            st.markdown(f"### {i+1}号艇")

            ex = st.number_input(
                "展示",
                value=6.50,
                step=0.01,
                key=f"sim_ex_{i}"
            )

            stt = st.number_input(
                "直線",
                value=5.00,
                step=0.01,
                key=f"sim_st_{i}"
            )

            lp = st.number_input(
                "一周",
                value=37.00,
                step=0.01,
                key=f"sim_lp_{i}"
            )

            tr = st.number_input(
                "回り足",
                value=5.0,
                step=0.1,
                key=f"sim_tr_{i}"
            )

            raw_ex.append(ex)
            raw_st.append(stt)
            raw_lp.append(lp)
            raw_tr.append(tr)

    # ----------------------------
    # 補正計算
    # ----------------------------
    corr_ex = mean_each_exhibit.values

    corrected_ex = []
    corrected_st = []
    corrected_lp = []
    corrected_tr = []

    for i in range(6):

        corrected_ex.append(raw_ex[i] + corr_ex[i])

        corrected_st.append(
            raw_st[i] + (mean_straight - raw_st[i])
        )

        corrected_lp.append(
            raw_lp[i] + (mean_lap - raw_lp[i])
        )

        corrected_tr.append(
            raw_tr[i] + (mean_turn - raw_tr[i])
        )

    result_today = pd.DataFrame({
        "艇番": boats,
        "展示": raw_ex,
        "補正展示": corrected_ex,
        "直線": raw_st,
        "補正直線": corrected_st,
        "一周": raw_lp,
        "補正一周": corrected_lp,
        "回り足": raw_tr,
        "補正回り足": corrected_tr
    })

    # ----------------------------
    # 順位
    # ----------------------------
    result_today["展示順位"] = result_today["補正展示"].rank(method="min")
    result_today["直線順位"] = result_today["補正直線"].rank(method="min")
    result_today["一周順位"] = result_today["補正一周"].rank(method="min")
    result_today["回り足順位"] = result_today["補正回り足"].rank(method="min", ascending=False)

    st.markdown("### 補正後データ（順位つき）")

    st.dataframe(
        result_today
        .style
        .format({
            "展示": "{:.2f}",
            "補正展示": "{:.3f}",
            "直線": "{:.2f}",
            "補正直線": "{:.3f}",
            "一周": "{:.2f}",
            "補正一周": "{:.3f}",
            "回り足": "{:.1f}",
            "補正回り足": "{:.2f}",
            "展示順位": "{:.0f}",
            "直線順位": "{:.0f}",
            "一周順位": "{:.0f}",
            "回り足順位": "{:.0f}"
        })
        .applymap(
            lambda v: "background-color:#ff4d4d" if v == 1 else
                      "background-color:#ffe066" if v == 2 else "",
            subset=["展示順位","直線順位","一周順位","回り足順位"]
        ),
        use_container_width=True
    )

    st.caption(f"{selected_place} 補正母数：{len(base)}件")
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





















