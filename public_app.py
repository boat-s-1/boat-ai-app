import streamlit as st
import pandas as pd
import numpy as np
import os
import base64
import gspread
import plotly.express as px
from google.oauth2.service_account import Credentials
import datetime
import base64

def encode_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def encode_image(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""
def highlight_rank(df):

    def _highlight(col):

        s = pd.to_numeric(col, errors="coerce")

        order = s.rank(method="min", ascending=True)

        styles = []
        for r in order:
            if pd.isna(r):
                styles.append("")
            elif r == 1:
                styles.append("background-color:#ff6b6b;color:white;")
            elif r == 2:
                styles.append("background-color:#ffd93d;")
            else:
                styles.append("")
        return styles

    return df.style.apply(_highlight, axis=0).format("{:.2f}")
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
st.image("header.png", use_container_width=True)
# ▼ スリット表示用CSS（ここに貼る）
st.markdown("""
<style>
.slit-area{
    background:#dff3ff;
    padding:20px;
    border-radius:12px;
    position:relative;
}

/* スタート基準ライン */
.slit-line{
    position:absolute;
    top:0;
    bottom:0;
    left:120px;
    width:3px;
    background:#ff5c5c;
    opacity:0.9;
}

.slit-row{
    display:flex;
    align-items:center;
    height:70px;
    position:relative;
    z-index:2;
}

.slit-boat{
    transition: all 0.4s ease;
    display:flex;
    align-items:center;
}
</style>
""", unsafe_allow_html=True)

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

st.title("予想ツール")

# タブ構成
tab_pre, tab_stat, tab_log, tab_memo, tab5 = st.tabs(["⭐ 簡易予想", "📊 統計解析", "📜 過去ログ", "📝 攻略メモ","スタート予想"])

# --- タブ1：事前簡易予想 ---
with tab_pre:
    st.subheader("各艇評価")
    SYMBOL_VALUES = {"◎": 100, "○": 80, "▲": 60, "△": 40, "×": 20, "無": 0}
    WEIGHTS = {"モーター": 0.25, "当地勝率": 0.2, "枠番勝率": 0.3, "枠番スタート": 0.25}

    with st.form("pre_eval_form"):
        boat_evals = {}
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
                    score = (SYMBOL_VALUES[m] * WEIGHTS["モーター"] + SYMBOL_VALUES[t] * WEIGHTS["当地勝率"] +
                             SYMBOL_VALUES[w] * WEIGHTS["枠番勝率"] + SYMBOL_VALUES[s] * WEIGHTS["枠番スタート"])
                    boat_evals[i] = round(score, 1)
        submitted = st.form_submit_button("予想カード生成", use_container_width=True, type="primary")

    if submitted:
        sorted_boats = sorted(boat_evals.items(), key=lambda x: x[1], reverse=True)
        res_cols = st.columns(3)
        for idx, (boat_num, score) in enumerate(sorted_boats[:6]):
            with res_cols[idx % 3]:
                st.metric(f"{boat_num}号艇", f"{score}%")

# --- タブ2：統計解析 ---
with tab_stat:

    st.subheader("会場別 補正・総合比較")

    # 管理用_NEW を使う
    ws2 = sh.worksheet("管理用_NEW")
    base_df = pd.DataFrame(ws2.get_all_records())

    if base_df.empty:
        st.warning("管理用_NEW にデータがありません")
        st.stop()

    # 数値化
    for c in ["展示","直線","一周","回り足","艇番"]:
        if c in base_df.columns:
            base_df[c] = pd.to_numeric(base_df[c], errors="coerce")

    place_list = sorted(base_df["会場"].dropna().unique())

    place = st.selectbox("会場を選択", place_list, key="tab2_place")

    place_df = base_df[base_df["会場"] == place].copy()

    st.divider()

    st.markdown("### 展示タイム入力")

    input_rows = []

    cols = st.columns(6)

    for b in range(1, 7):

        with cols[b-1]:

            st.markdown(f"#### {b}号艇")

            tenji  = st.number_input(
    "展示", value=6.70, step=0.01, format="%.2f",
    key=f"tab2_in_tenji_{b}"
)
choku  = st.number_input(
    "直線", value=7.00, step=0.01, format="%.2f",
    key=f"tab2_in_choku_{b}"
)
isshu  = st.number_input(
    "一周", value=37.00, step=0.01, format="%.2f",
    key=f"tab2_in_isshu_{b}"
)
mawari = st.number_input(
    "回り足", value=5.00, step=0.01, format="%.2f",
    key=f"tab2_in_mawari_{b}"
)

input_rows.append({
            "艇番": b,
            "展示": tenji,
            "直線": choku,
            "一周": isshu,
            "回り足": mawari
        })

    input_df = pd.DataFrame(input_rows).set_index("艇番")

    st.divider()
    st.markdown("### 公式展示タイム表")

    st.dataframe(
        highlight_rank(input_df),
        use_container_width=True
    )

    # -------------------------
    # 会場平均との差（補正）
    # -------------------------

    st.divider()
    st.markdown("### 会場補正後タイム")

    place_mean = (
        place_df
        .groupby("艇番")[["展示","直線","一周","回り足"]]
        .mean()
    )

    overall_mean = (
        place_df[["展示","直線","一周","回り足"]]
        .mean()
    )

    adj_df = input_df.copy()

    for b in range(1,7):
        if b in place_mean.index:
            for col in ["展示","直線","一周","回り足"]:
                adj_df.loc[b, col] = (
                    input_df.loc[b, col]
                    - place_mean.loc[b, col]
                    + overall_mean[col]
                )

    st.dataframe(
        highlight_rank(adj_df),
        use_container_width=True
    )

    # -------------------------
    # 艇番補正（イン有利）
    # -------------------------

    st.divider()
    st.markdown("### 艇番（枠）補正込みタイム")

    lane_bias = (
        place_df
        .groupby("艇番")[["展示","直線","一周","回り足"]]
        .mean()
        - overall_mean
    )

    final_df = adj_df.copy()

    for b in range(1,7):
        if b in lane_bias.index:
            for col in ["展示","直線","一周","回り足"]:
                final_df.loc[b, col] = (
                    adj_df.loc[b, col]
                    - lane_bias.loc[b, col]
                )

    st.dataframe(
        highlight_rank(final_df),
        use_container_width=True
    )
# --- タブ3：過去ログ ---
with tab_log:
    st.dataframe(df)

# --- タブ4：攻略メモ ---
with tab_memo:
    st.write("攻略メモ機能")

# --- タブ5：スタート予想 ---
with tab5:

    st.subheader("🚀 スタート予想（展示＋1周＋ST 補正）")

    ws = sh.worksheet("管理用_NEW")
    data = ws.get_all_records()
    df_place = pd.DataFrame(data)

    if df_place.empty:
        st.info("データがありません")
        st.stop()

    df_place["登録日時"] = pd.to_datetime(df_place["登録日時"], errors="coerce")
    df_place["レース番号"] = df_place["レース番号"].astype(str)

    latest_row = df_place.sort_values("登録日時").iloc[-1]

    race_date  = latest_row["日付"]
    race_place = latest_row["会場"]
    race_no    = str(latest_row["レース番号"])

    base = df_place[
        (df_place["日付"] == race_date) &
        (df_place["会場"] == race_place) &
        (df_place["レース番号"] == race_no)
    ].copy()

    if len(base) < 6:
        st.warning("このレースの6艇データが揃っていません")
        st.stop()

    st.caption(f"{race_date} {race_place} {race_no}R")

    # -----------------------
    # 会場平均との差を出すための平均
    # -----------------------
    place_df = df_place[df_place["会場"] == race_place].copy()

    for c in ["展示", "一周", "ST"]:
        place_df[c] = pd.to_numeric(place_df[c], errors="coerce")

    mean_tenji = place_df["展示"].mean()
    mean_isshu = place_df["一周"].mean()

    st.markdown("### 📝 今回レースの展示・1周入力（補正用）")

    input_cols = st.columns(6)

    tenji_input = {}
    isshu_input = {}

    base = base.sort_values("艇番")

    for i, (_, r) in enumerate(base.iterrows()):
        boat = int(r["艇番"])

        with input_cols[i]:
            st.markdown(f"**{boat}号艇**")
            tenji_input[boat] = st.number_input(
                "展示",
                step=0.01,
                value=float(r["展示"]) if pd.notna(r["展示"]) else 0.0,
                key=f"tab5_tenji_{boat}"
            )
            isshu_input[boat] = st.number_input(
                "一周",
                step=0.01,
                value=float(r["一周"]) if pd.notna(r["一周"]) else 0.0,
                key=f"tab5_isshu_{boat}"
            )

    # -----------------------
    # スコア計算
    # -----------------------
    base["ST"] = pd.to_numeric(base["ST"], errors="coerce")

    eval_map = {
        "◎": 2.0,
        "◯": 1.0,
        "△": 0.5,
        "×": -1.0
    }

    base["評価補正"] = base["スタート評価"].map(eval_map).fillna(0)

    scores = []

    for _, r in base.iterrows():

        boat = int(r["艇番"])

        st_score = -r["ST"] + r["評価補正"]

        # 展示補正（速いほどプラス）
        tenji_diff = mean_tenji - tenji_input[boat]

        # 1周補正（速いほどプラス）
        isshu_diff = mean_isshu - isshu_input[boat]

        total = (
            st_score
            + tenji_diff * 2.0
            + isshu_diff * 0.3
        )

        scores.append(total)

    base["start_score"] = scores

    # -----------------------
    # スリット表示
    # -----------------------
    st.markdown("### 🟦 スリット予想イメージ")

    st.markdown('<div class="slit-area">', unsafe_allow_html=True)
    st.markdown('<div class="slit-line"></div>', unsafe_allow_html=True)

    for _, r in base.iterrows():

        boat_no = int(r["艇番"])
        score   = float(r["start_score"])

        offset = max(0, min(160, (score + 0.5) * 120))

        img_path = os.path.join(BASE_DIR, "images", f"boat{boat_no}.png")
        img_base64 = encode_image(img_path)

        html = f"""
        <div class="slit-row">
            <div class="slit-boat" style="margin-left:{offset}px;">
                <img src="data:image/png;base64,{img_base64}" height="48">
                <div style="margin-left:10px;font-size:13px;">
                    <b>{boat_no}号艇</b><br>
                    展示 {tenji_input[boat_no]:.2f}
                    一周 {isshu_input[boat_no]:.2f}<br>
                    ST {r["ST"]:.2f} {r["スタート評価"]}
                </div>
            </div>
        </div>
        """

        st.markdown(html, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
















