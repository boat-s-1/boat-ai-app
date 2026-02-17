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

# --- タブ2：補正展示タイム（蓄積データから算出） ---
with tab_stat:

    st.subheader("補正展示タイム閲覧（会場別・蓄積データ）")

    if df.empty:
        st.warning("データがありません")
        st.stop()

    # 会場選択（2列目が会場）
    places = sorted(df.iloc[:, 1].dropna().unique())
    race_place = st.selectbox("会場を選択してください", places)
# -----------------------------
# 会場別・展示タイム差分（6艇）
# -----------------------------
ex_cols = base.iloc[:, 9:15].apply(pd.to_numeric, errors="coerce")

# 6艇それぞれの平均差分
mean_each_boat = ex_cols.mean()
    # 会場で抽出
    base = df[df.iloc[:, 1] == race_place]

    st.write(f"対象データ数：{len(base)} 件")

    if len(base) < 5:
        st.warning("補正に使うデータが少なすぎます（最低5件以上推奨）")
        st.stop()

    # =====================================
    # 展示タイム差分（6艇）
    # =====================================
    ex_cols = base.iloc[:, 9:15].apply(pd.to_numeric, errors="coerce")

    mean_each_boat = ex_cols.mean()
    mean_exhibit = ex_cols.mean().mean()

    result_ex = pd.DataFrame({
        "号艇": [f"{i}号艇" for i in range(1, 7)],
        "展示補正平均との差": mean_each_boat.values
    })

    st.markdown("### 展示タイム補正値（平均との差）")
    st.dataframe(
        result_ex.style.format({"展示補正平均との差": "{:.4f}"}),
        use_container_width=True
    )

    st.markdown("会場全体平均との差（参考）")
    st.write(round(mean_exhibit, 4))


    # =====================================
    # 直線タイム差分
    # =====================================
    st_cols = base.iloc[:, 15:21].apply(pd.to_numeric, errors="coerce")

    mean_each_st = st_cols.mean()

    result_st = pd.DataFrame({
        "号艇": [f"{i}号艇" for i in range(1, 7)],
        "直線補正平均との差": mean_each_st.values
    })

    st.markdown("### 直線タイム補正値（平均との差）")
    st.dataframe(
        result_st.style.format({"直線補正平均との差": "{:.4f}"}),
        use_container_width=True
    )


    # =====================================
    # 1周タイム差分
    # =====================================
    lp_cols = base.iloc[:, 21:27].apply(pd.to_numeric, errors="coerce")

    mean_each_lp = lp_cols.mean()

    result_lp = pd.DataFrame({
        "号艇": [f"{i}号艇" for i in range(1, 7)],
        "1周補正平均との差": mean_each_lp.values
    })

    st.markdown("### 1周タイム補正値（平均との差）")
    st.dataframe(
        result_lp.style.format({"1周補正平均との差": "{:.4f}"}),
        use_container_width=True
    )


    # =====================================
    # 回り足タイム差分
    # =====================================
    tn_cols = base.iloc[:, 27:33].apply(pd.to_numeric, errors="coerce")

    mean_each_tn = tn_cols.mean()

    result_tn = pd.DataFrame({
        "号艇": [f"{i}号艇" for i in range(1, 7)],
        "回り足補正平均との差": mean_each_tn.values
    })

    st.markdown("### 回り足タイム補正値（平均との差）")
    st.dataframe(
        result_tn.style.format({"回り足補正平均との差": "{:.4f}"}),
        use_container_width=True
    )

    st.caption("※ 管理者ページで保存された『平均との差分データ』のみを使用しています。")
    
    # ==============================
# 今日の展示タイム補正シミュレーション
# ==============================

st.markdown("---")
st.markdown("## 今日の展示タイム補正シミュレーション")

raw_times = []
cols = st.columns(6)

for i in range(6):
    with cols[i]:
        t = st.number_input(
            f"{i+1}号艇 展示タイム",
            min_value=0.0,
            step=0.01,
            value=6.50,   # ★初期値を6.50に
            key=f"today_ex_{i+1}"
        )
        raw_times.append(t)

# 会場別の補正差分（6艇分）
corr = mean_each_boat.values

corrected = []
for i in range(6):
    if raw_times[i] == 0:
        corrected.append(None)
    else:
        corrected.append(raw_times[i] + corr[i])

result_today = pd.DataFrame({
    "艇番": list(range(1, 7)),
    "今日展示": raw_times,
    "今日補正展示": corrected
})

# -----------------------------
# 今日補正展示の順位（小さいほど良い）
# -----------------------------
result_today["今日補正展示順位"] = (
    result_today["今日補正展示"]
    .rank(method="min")
)

st.markdown("### 今日の補正結果")

st.dataframe(
    result_today
    .style
    .format({
        "今日展示": "{:.2f}",
        "今日補正展示": "{:.3f}",
        "今日補正展示順位": "{:.0f}"
    })
    .applymap(
        lambda v: "background-color:#ff4d4d" if v == 1 else
                  "background-color:#ffe066" if v == 2 else "",
        subset=["今日補正展示順位"]
    ),
    use_container_width=True
)

# ==============================
# 既存の補正一覧テーブルへ合流
# ==============================

df = df.merge(
    result_today[["艇番", "今日展示", "今日補正展示", "今日補正展示順位"]],
    on="艇番",
    how="left"
)

# -----------------------------
# 表示列（今日分を先頭に追加）
# -----------------------------
show_cols = [
    "艇番",

    "今日展示", "今日補正展示", "今日補正展示順位",

    "展示", "補正展示", "展示順位",
    "直線", "補正直線", "直線順位",
    "一周", "補正一周", "一周順位",
    "回り足", "補正回り足"
]

st.markdown("### 補正一覧（今日入力＋蓄積補正）")

st.dataframe(
    df[show_cols]
    .sort_values("今日補正展示", na_position="last")
    .style
    .format({
        "今日展示": "{:.2f}",
        "今日補正展示": "{:.3f}",
        "展示": "{:.2f}",
        "補正展示": "{:.3f}",
        "直線": "{:.2f}",
        "補正直線": "{:.3f}",
        "一周": "{:.2f}",
        "補正一周": "{:.3f}",
        "回り足": "{:.2f}",
        "補正回り足": "{:.3f}",
    })
    .applymap(
        lambda v: "background-color:#ff4d4d" if v == 1 else
                  "background-color:#ffe066" if v == 2 else "",
        subset=["今日補正展示順位", "展示順位", "直線順位", "一周順位"]
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











