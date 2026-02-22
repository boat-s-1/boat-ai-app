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
tab_pre, tab_stat,tab5,tab_cond,tab_view,tab_women_stat = st.tabs(["⭐ 簡易予想", "📊 統計解析","スタート予想","風・波補正","女子戦","女子戦補正"])

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

    # ------------------------
    # データ読み込み
    # ------------------------
    ws2 = sh.worksheet("管理用_NEW")
    base_df = pd.DataFrame(ws2.get_all_records())

    if base_df.empty:
        st.warning("管理用_NEW にデータがありません")
        st.stop()

    for c in ["展示", "直線", "一周", "回り足", "艇番"]:
        if c in base_df.columns:
            base_df[c] = pd.to_numeric(base_df[c], errors="coerce")

    if "会場" not in base_df.columns:
        st.error("管理用_NEW に『会場』列がありません")
        st.stop()

    place_list = sorted(base_df["会場"].dropna().unique())
    place = st.selectbox("会場を選択", place_list, key="tab2_place")

    place_df = base_df[base_df["会場"] == place].copy()

    st.divider()

    # ------------------------
    # 色付け
    # ------------------------
    def highlight_rank(df):

        def color_col(s):
            s2 = pd.to_numeric(s, errors="coerce")
            rank = s2.rank(method="min")

            out = []
            for v, r in zip(s2, rank):
                if pd.isna(v):
                    out.append("")
                elif r == 1:
                    out.append("background-color:#ff6b6b")
                elif r == 2:
                    out.append("background-color:#ffd43b")
                else:
                    out.append("")
            return out

        return df.style.apply(color_col, axis=0)

    # ------------------------
    # 入力（横並び）
    # ------------------------
    st.markdown("### 展示タイム入力（当日データ）")

    input_rows = []

    head = st.columns([1, 2, 2, 2, 2])
    head[0].markdown("**艇番**")
    head[1].markdown("**一周**")
    head[2].markdown("**回り足**")
    head[3].markdown("**直線**")
    head[4].markdown("**展示**")

    for b in range(1, 7):

        cols = st.columns([1, 2, 2, 2, 2])

        cols[0].markdown(f"**{b}号艇**")

        isshu = cols[1].number_input(
            "",
            step=0.01,
            format="%.2f",
            value=37.00,
            key=f"tab2_in_isshu_{b}",
            label_visibility="collapsed"
        )

        mawari = cols[2].number_input(
            "",
            step=0.01,
            format="%.2f",
            value=5.00,
            key=f"tab2_in_mawari_{b}",
            label_visibility="collapsed"
        )

        choku = cols[3].number_input(
            "",
            step=0.01,
            format="%.2f",
            value=6.90,
            key=f"tab2_in_choku_{b}",
            label_visibility="collapsed"
        )

        tenji = cols[4].number_input(
            "",
            step=0.01,
            format="%.2f",
            value=6.50,
            key=f"tab2_in_tenji_{b}",
            label_visibility="collapsed"
        )

        input_rows.append({
            "艇番": b,
            "展示": tenji,
            "直線": choku,
            "一周": isshu,
            "回り足": mawari
        })

    input_df = pd.DataFrame(input_rows).set_index("艇番")

    # ★タブ5連動用に保存
    st.session_state["tab2_input_df"] = input_df.copy()

    st.divider()

    # ------------------------
    # 入力値表示
    # ------------------------
    st.markdown("### 公式展示タイム表（入力値）")

    st.dataframe(
        highlight_rank(input_df),
        use_container_width=True
    )

    # ------------------------
    # 場平均補正
    # ------------------------
    st.divider()
    st.markdown("### 場平均補正タイム（会場平均との差補正）")

    place_mean = (
        place_df
        .groupby("艇番")[["展示", "直線", "一周", "回り足"]]
        .mean()
    )

    overall_mean = place_df[["展示", "直線", "一周", "回り足"]].mean()

    adj_df = input_df.copy()

    for b in range(1, 7):
        if b in place_mean.index:
            for col in ["展示", "直線", "一周", "回り足"]:
                if pd.notna(input_df.loc[b, col]) and pd.notna(place_mean.loc[b, col]):
                    adj_df.loc[b, col] = (
                        input_df.loc[b, col]
                        - place_mean.loc[b, col]
                        + overall_mean[col]
                    )

    st.dataframe(
        highlight_rank(adj_df),
        use_container_width=True
    )

    # ------------------------
    # 枠番補正
    # ------------------------
    st.divider()
    st.markdown("### 枠番補正込みタイム（イン有利補正）")

    lane_bias = (
        place_df
        .groupby("艇番")[["展示", "直線", "一周", "回り足"]]
        .mean()
        - overall_mean
    )

    final_df = adj_df.copy()

    for b in range(1, 7):
        if b in lane_bias.index:
            for col in ["展示", "直線", "一周", "回り足"]:
                if pd.notna(adj_df.loc[b, col]) and pd.notna(lane_bias.loc[b, col]):
                    final_df.loc[b, col] = (
                        adj_df.loc[b, col]
                        - lane_bias.loc[b, col]
                    )

    st.dataframe(
        highlight_rank(final_df),
        use_container_width=True
    )
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

    # ★タブ2入力取得
    tab2_df = st.session_state.get("tab2_input_df")

    for i, (_, r) in enumerate(base.iterrows()):

        boat = int(r["艇番"])

        with input_cols[i]:

            st.markdown(f"**{boat}号艇**")

            if tab2_df is not None and boat in tab2_df.index:
                tenji_default = float(tab2_df.loc[boat, "展示"])
            else:
                tenji_default = float(r["展示"]) if pd.notna(r["展示"]) else 0.0

            tenji_input[boat] = st.number_input(
                "展示",
                step=0.01,
                value=tenji_default,
                key=f"tab5_tenji_{boat}"
            )

            if tab2_df is not None and boat in tab2_df.index:
                isshu_default = float(tab2_df.loc[boat, "一周"])
            else:
                isshu_default = float(r["一周"]) if pd.notna(r["一周"]) else 0.0

            isshu_input[boat] = st.number_input(
                "一周",
                step=0.01,
                value=isshu_default,
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

        tenji_diff = mean_tenji - tenji_input[boat]
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
# --- タブ：条件補正 ---
with tab_cond:

    st.subheader("🌊 条件別 補正データ（風・波・会場）")

    ws = sh.worksheet("管理用_NEW")
    df = pd.DataFrame(ws.get_all_records())

    if df.empty:
        st.warning("管理用_NEW にデータがありません")
        st.stop()

    # 数値化
    for c in ["展示","直線","一周","回り足","艇番","風速","波高"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # -----------------------
    # 条件入力
    # -----------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        place = st.selectbox(
            "会場",
            sorted(df["会場"].dropna().unique()),
            key="cond_place"
        )

    with col2:
        wind = st.selectbox(
            "風向き",
            sorted(df["風向き"].dropna().unique()),
            key="cond_wind"
        )

    with col3:
        wind_range = st.slider(
            "風速範囲(m)",
            0.0, 15.0, (0.0, 5.0),
            step=0.5,
            key="cond_wind_spd"
        )

    with col4:
        wave_range = st.slider(
            "波高範囲(cm)",
            0.0, 50.0, (0.0, 10.0),
            step=1.0,
            key="cond_wave"
        )

    # -----------------------
    # 条件抽出
    # -----------------------

    cond_df = df[
        (df["会場"] == place) &
        (df["風向き"] == wind) &
        (df["風速"] >= wind_range[0]) &
        (df["風速"] <= wind_range[1]) &
        (df["波高"] >= wave_range[0]) &
        (df["波高"] <= wave_range[1])
    ].copy()

    st.caption(f"抽出レース数：{len(cond_df)} 件")

    if cond_df.empty:
        st.warning("条件に一致するデータがありません")
        st.stop()

    # -----------------------
    # 艇番別 平均タイム
    # -----------------------

    st.divider()
    st.markdown("### 🚤 艇番別・条件一致 平均タイム")

    mean_df = (
        cond_df
        .groupby("艇番")[["展示","直線","一周","回り足"]]
        .mean()
        .round(3)
        .sort_index()
    )

    st.dataframe(mean_df, use_container_width=True)

    # -----------------------
    # 全体平均との差（条件補正値）
    # -----------------------

    st.divider()
    st.markdown("### 🧠 条件平均との差（＝条件補正の正体）")

    overall = cond_df[["展示","直線","一周","回り足"]].mean()

    diff_df = mean_df.copy()

    for c in ["展示","直線","一周","回り足"]:
        diff_df[c] = mean_df[c] - overall[c]

    diff_df = diff_df.round(3)

    st.dataframe(diff_df, use_container_width=True)

    st.caption("※マイナスが大きいほど、その条件では有利な艇番傾向です")

# -----------------------------
# 閲覧用：女子戦データ
# -----------------------------
with tab_view:

    st.subheader("👩 女子戦データ閲覧")

    ws = sh.worksheet("管理用_NEW")
    df = pd.DataFrame(ws.get_all_records())

    if df.empty:
        st.info("データがありません")
        st.stop()

    # 列チェック
    if "女子戦" not in df.columns:
        st.error("女子戦 列が見つかりません")
        st.stop()

    # 日付を日付型に
    df["日付"] = pd.to_datetime(df["日付"], errors="coerce")

    # 女子戦のみ
    df = df[df["女子戦"].astype(str).str.lower().isin(["true", "1", "yes", "y", "○"])]

    if df.empty:
        st.info("女子戦データがまだありません")
        st.stop()

    # 絞り込みUI
    col1, col2 = st.columns(2)

    with col1:
        place_list = ["すべて"] + sorted(df["会場"].dropna().unique().tolist())
        sel_place = st.selectbox("会場", place_list)

    with col2:
        date_list = ["すべて"] + sorted(
            df["日付"].dropna().dt.strftime("%Y-%m-%d").unique().tolist()
        )
        sel_date = st.selectbox("日付", date_list)

    view_df = df.copy()

    if sel_place != "すべて":
        view_df = view_df[view_df["会場"] == sel_place]

    if sel_date != "すべて":
        view_df = view_df[
            view_df["日付"].dt.strftime("%Y-%m-%d") == sel_date
        ]

    view_df = view_df.sort_values(
        ["日付", "会場", "レース番号", "艇番"]
    )

    st.caption(f"表示件数：{len(view_df)} 件")

    show_cols = [
        "日付","会場","レース番号","艇番",
        "展示","直線","一周","回り足",
        "ST","風向き","風速","波高",
        "着順","スタート評価"
    ]

    exist_cols = [c for c in show_cols if c in view_df.columns]

    st.dataframe(
        view_df[exist_cols],
        use_container_width=True,
        hide_index=True
    )

# -----------------------------
# 閲覧用：女子戦 × 場平均補正
# -----------------------------
with tab_women_stat:

    st.subheader("👩 女子戦｜場平均補正タイム")

    ws = sh.worksheet("管理用_NEW")
    df = pd.DataFrame(ws.get_all_records())

    if df.empty:
        st.info("データがありません")
        st.stop()

    # 必須列チェック
    need_cols = ["女子戦","会場","艇番","展示","直線","一周","回り足"]
    for c in need_cols:
        if c not in df.columns:
            st.error(f"{c} 列が見つかりません")
            st.stop()

    # 数値化
    for c in ["艇番","展示","直線","一周","回り足"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # 女子戦だけ
    women_df = df[
        df["女子戦"].astype(str).str.lower().isin(["true","1","yes","y","○"])
    ].copy()

    if women_df.empty:
        st.info("女子戦データがまだありません")
        st.stop()

    # 会場選択
    place_list = sorted(women_df["会場"].dropna().unique().tolist())
    place = st.selectbox("会場を選択", place_list, key="women_stat_place")

    place_df = women_df[women_df["会場"] == place].copy()

    st.caption(f"{place}｜女子戦データ件数：{len(place_df)} 件")

    # ------------------------
    # 艇番別平均との差
    # ------------------------
    lane_mean = (
        place_df
        .groupby("艇番")[["展示","直線","一周","回り足"]]
        .mean()
    )

    overall_mean = place_df[["展示","直線","一周","回り足"]].mean()

    # 補正量（＝平均との差）
    diff_df = lane_mean.copy()

    for col in ["展示","直線","一周","回り足"]:
        diff_df[col] = lane_mean[col] - overall_mean[col]

    st.markdown("### 艇番別 平均タイム（女子戦）")
    st.dataframe(
        lane_mean.round(3),
        use_container_width=True
    )

    st.markdown("### 場平均との差（女子戦・補正量）")

    st.caption("※ プラス＝遅い / マイナス＝速い")

    st.dataframe(
        diff_df.round(3),
        use_container_width=True
    )


























