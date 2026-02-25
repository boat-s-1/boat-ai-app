import streamlit as st
import pandas as pd
import numpy as np
import os
import base64
import gspread
import plotly.express as px
from google.oauth2.service_account import Credentials
import datetime

# ★必ず最初に
st.set_page_config(page_title="競艇Pro 蒲郡", layout="wide")

# -------------------------
# 会場固定
# -------------------------
PLACE_NAME = "蒲郡"

# 戻るボタン
if st.button("← 会場選択へ戻る"):
    st.switch_page("public_app.py")
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

# --- 3. データ読み込み ---
# ==============================
# 会場トップページ
# ==============================
if "selected_place" not in st.session_state:
    st.session_state.selected_place = None

if st.session_state.selected_place is None:

    st.title("🏁 レースを選択")

    places = ["混合戦", "女子戦"]

    cols = st.columns(2)

    for i, p in enumerate(places):
        if cols[i % 3].button(p, use_container_width=True):
            st.session_state.selected_place = p
            st.rerun()

    st.stop()


# ==============================
# ここから本体処理
# ==============================
place = st.session_state.selected_place

st.caption(f"選択中の会場：{place}")

df = pd.DataFrame()
gc = get_gsheet_client()

# ▼ レースごとのシート名対応
SHEET_MAP = {
    "蒲郡混合戦": {
        "sheet1": "蒲郡混合_統計シート",
        "sheet2": "蒲郡混合_統計シート②"
    },
    "蒲郡女子戦": {
        "sheet1": "蒲郡女子_統計シート",
        "sheet2": "蒲郡女子_統計シート②"
    },
}

if gc:
    try:
        sh = gc.open_by_key("1lN794iGtyGV2jNwlYzUA8wEbhRwhPM7FxDAkMaoJss4")

        ws1_name = SHEET_MAP[place]["sheet1"]
        ws2_name = SHEET_MAP[place]["sheet2"]

        ws1 = sh.worksheet(ws1_name)
        ws2 = sh.worksheet(ws2_name)

        rows1 = ws1.get_all_records()
        rows2 = ws2.get_all_records()

        all_rows = rows1 + rows2

        if len(all_rows) > 0:
            df = pd.DataFrame(all_rows)

    except Exception as e:
        st.error(e)
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
        sh = gc.open_by_key("1lN794iGtyGV2jNwlYzUA8wEbhRwhPM7FxDAkMaoJss4")

        ws1 = sh.worksheet("統計シート")
        ws2 = sh.worksheet("統計シート②")

        rows1 = ws1.get_all_records()
        rows2 = ws2.get_all_records()

        all_rows = rows1 + rows2

        if len(all_rows) > 0:
            df = pd.DataFrame(all_rows)

    except Exception as e:
        st.error(e)
st.title("予想ツール")

# タブ構成
tab_pre, tab_stat,tab5,tab_mix_check,tab_cond,tab_view,tab_women_stat,tab_women_input,tab_women_start,tab_women_result = st.tabs(["⭐ 簡易予想", "📊 統計解析","スタート予想","混合戦スタート精度","風・波補正","女子戦","女子戦補正閲覧","女子戦補正入力","女子戦スタート予想","女子戦スタート精度"])

# --- タブ1：事前簡易予想 ---
with tab_pre:

    st.subheader("🎯 事前簡易予想（評価カード）")

    SYMBOL_VALUES = {"◎": 100, "○": 80, "▲": 60, "△": 40, "×": 20, "無": 0}
    WEIGHTS = {
        "モーター": 0.25,
        "当地勝率": 0.2,
        "枠番勝率": 0.3,
        "枠番スタート": 0.25
    }

    with st.form("pre_eval_form"):

        boat_evals = {}

        for row in range(3):
            cols = st.columns(2)

            for col in range(2):
                i = row * 2 + col + 1

                with cols[col]:
                    st.markdown(f"#### 🚤 {i}号艇")

                    m = st.selectbox(
                        "モーター",
                        ["◎", "○", "▲", "△", "×", "無"],
                        index=5,
                        key=f"pre_m_{i}"
                    )

                    t = st.selectbox(
                        "当地勝率",
                        ["◎", "○", "▲", "△", "×", "無"],
                        index=5,
                        key=f"pre_t_{i}"
                    )

                    w = st.selectbox(
                        "枠番勝率",
                        ["◎", "○", "▲", "△", "×", "無"],
                        index=5,
                        key=f"pre_w_{i}"
                    )

                    s = st.selectbox(
                        "枠番ST",
                        ["◎", "○", "▲", "△", "×", "無"],
                        index=5,
                        key=f"pre_s_{i}"
                    )

                    score = (
                        SYMBOL_VALUES[m] * WEIGHTS["モーター"]
                        + SYMBOL_VALUES[t] * WEIGHTS["当地勝率"]
                        + SYMBOL_VALUES[w] * WEIGHTS["枠番勝率"]
                        + SYMBOL_VALUES[s] * WEIGHTS["枠番スタート"]
                    )

                    boat_evals[i] = round(score, 3)

        submitted = st.form_submit_button(
            "📊 予想カード生成",
            use_container_width=True,
            type="primary"
        )

    # -----------------------
    # 結果表示
    # -----------------------
    if submitted:

        df_score = pd.DataFrame(
            [{"艇番": k, "score": v} for k, v in boat_evals.items()]
        )

        # 念のため
        df_score["score"] = df_score["score"].fillna(0)

        # -----------------------
        # ✅ ％正規化（6艇合計＝100％）
        # -----------------------
        total_score = df_score["score"].sum()

        if total_score == 0:
            st.warning("すべて『無』のため、％を計算できません")
            st.stop()

        df_score["予想％"] = df_score["score"] / total_score * 100
        df_score["予想％"] = df_score["予想％"].round(1)

        # 並び替え
        df_score = df_score.sort_values("予想％", ascending=False).reset_index(drop=True)

        # 誤差補正（必ず100.0にする）
        diff = 100.0 - df_score["予想％"].sum()
        df_score.loc[0, "予想％"] = round(df_score.loc[0, "予想％"] + diff, 1)

        # -----------------------
        # 表示用順位
        # -----------------------
        df_score["順位"] = df_score.index + 1

        st.markdown("### 🏁 予想結果（合計100％）")

        cols = st.columns(3)

        for i, r in df_score.iterrows():

            rank = int(r["順位"])
            boat = int(r["艇番"])
            pct  = float(r["予想％"])

            # 少し豪華用スタイル
            if rank == 1:
                bg = "#fff1c1"
                border = "#f5b700"
                title = "🥇 1位"
            elif rank == 2:
                bg = "#f0f0f0"
                border = "#b5b5b5"
                title = "🥈 2位"
            elif rank == 3:
                bg = "#ffe4d6"
                border = "#e39a6f"
                title = "🥉 3位"
            else:
                bg = "#fafafa"
                border = "#dddddd"
                title = f"{rank}位"

            with cols[i % 3]:

                st.markdown(
                    f"""
                    <div style="
                        background:{bg};
                        border:2px solid {border};
                        border-radius:14px;
                        padding:14px;
                        text-align:center;
                        box-shadow:0 4px 8px rgba(0,0,0,0.05);
                    ">
                        <div style="font-size:15px;color:#555;">{title}</div>
                        <div style="font-size:26px;font-weight:700;margin-top:4px;">
                            {boat}号艇
                        </div>
                        <div style="font-size:22px;color:#222;margin-top:6px;">
                            {pct:.1f}%
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.divider()

        st.markdown("### 📋 内訳（デバッグ用）")
        st.dataframe(
            df_score[["順位", "艇番", "score", "予想％"]],
            use_container_width=True
        )
# --- タブ2：統計解析 ---
with tab_stat:

    st.subheader("会場別 補正・総合比較（統計シート）")

    # ======================================
    # 統計データ読み込みボタン
    # ======================================
    if st.button("統計データを読み込んで比較する", key="tab2_load_btn"):

        with st.spinner("統計データを読み込んでいます…"):

            sh = gc.open_by_key("1lN794iGtyGV2jNwlYzUA8wEbhRwhPM7FxDAkMaoJss4")

            ws1 = sh.worksheet("統計シート")
            ws2 = sh.worksheet("統計シート②")

            rows1 = ws1.get_all_records()
            rows2 = ws2.get_all_records()

            base_df = pd.DataFrame(rows1 + rows2)

            st.session_state["tab2_base_df"] = base_df

    if "tab2_base_df" not in st.session_state:
        st.info("『統計データを読み込んで比較する』を押してください。")
        st.stop()

    base_df = st.session_state["tab2_base_df"].copy()

    if base_df.empty:
        st.warning("統計シートにデータがありません")
        st.stop()

    # ======================================
    # 型調整
    # ======================================
    for c in ["展示", "直線", "一周", "回り足", "艇番"]:
        if c in base_df.columns:
            base_df[c] = pd.to_numeric(base_df[c], errors="coerce")

    if "会場" not in base_df.columns:
        st.error("統計シートに『会場』列がありません")
        st.stop()

    st.markdown(f"#### 会場：{PLACE_NAME}")

    place_df = base_df[base_df["会場"] == PLACE_NAME].copy()

    if place_df.empty:
        st.warning("この会場のデータがありません")
        st.stop()

    # ======================================
    # 使用レース数
    # ======================================
    race_count = (
        place_df[["日付", "レース番号"]]
        .dropna()
        .drop_duplicates()
        .shape[0]
    )

    st.caption(f"📊 過去データ {race_count}レースより補正")
    st.divider()

    # ======================================
    # 色付け関数
    # ======================================
    def highlight_rank(df):

        def color_col(s):
            s2 = pd.to_numeric(s, errors="coerce")
            rank = s2.rank(method="min")

            out = []
            for v, r in zip(s2, rank):
                if pd.isna(v):
                    out.append("")
                elif r == 1:
                    out.append("background-color:#ff6b6b;color:white;")
                elif r == 2:
                    out.append("background-color:#ffd43b;")
                else:
                    out.append("")
            return out

        return df.style.apply(color_col, axis=0)

    # ======================================
    # 入力フォーム
    # ======================================
    st.markdown("### 展示タイム入力（当日データ）")

    with st.form("tab2_input_form"):

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
                key=f"tab2_in_isshu_{b}",
                label_visibility="collapsed"
            )

            mawari = cols[2].number_input(
                "",
                step=0.01,
                format="%.2f",
                key=f"tab2_in_mawari_{b}",
                label_visibility="collapsed"
            )

            choku = cols[3].number_input(
                "",
                step=0.01,
                format="%.2f",
                key=f"tab2_in_choku_{b}",
                label_visibility="collapsed"
            )

            tenji = cols[4].number_input(
                "",
                step=0.01,
                format="%.2f",
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

        submit_input = st.form_submit_button("この入力で再計算する")

    if submit_input:
        input_df = pd.DataFrame(input_rows).set_index("艇番")
        st.session_state["tab2_input_df"] = input_df.copy()

    if "tab2_input_df" not in st.session_state:
        st.info("展示タイムを入力して『この入力で再計算する』を押してください")
        st.stop()

    input_df = st.session_state["tab2_input_df"].copy()

    # tab5 連動用
    st.session_state["tab2_input_df"] = input_df.copy()

    st.divider()

    # ======================================
    # 入力値表示
    # ======================================
    st.markdown("### 公式展示タイム表（入力値）")

    st.dataframe(
        highlight_rank(input_df),
        use_container_width=True
    )

    # ======================================
    # 場平均補正
    # ======================================
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
                if (
                    pd.notna(input_df.loc[b, col])
                    and pd.notna(place_mean.loc[b, col])
                ):
                    adj_df.loc[b, col] = (
                        input_df.loc[b, col]
                        - place_mean.loc[b, col]
                        + overall_mean[col]
                    )

    st.dataframe(
        highlight_rank(adj_df),
        use_container_width=True
    )

    # ======================================
    # 枠番補正
    # ======================================
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
                if (
                    pd.notna(adj_df.loc[b, col])
                    and pd.notna(lane_bias.loc[b, col])
                ):
                    final_df.loc[b, col] = (
                        adj_df.loc[b, col]
                        - lane_bias.loc[b, col]
                    )

    st.dataframe(
        highlight_rank(final_df),
        use_container_width=True
    )
# --- タブ5：スタート予想（混合戦・入力型） ---
with tab5:

    st.subheader("🚀 スタート予想（混合戦｜会場別補正・入力型）")

    ws = sh.worksheet("管理用_NEW")
    df = pd.DataFrame(ws.get_all_records())

    if df.empty:
        st.info("データがありません")

    # 型変換
    for c in ["展示", "一周", "ST", "艇番"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # -----------------------
    # 会場選択のみ
    # -----------------------
    place_list = sorted(df["会場"].dropna().unique())

    race_place = st.selectbox(
        "会場を選択",
        place_list,
        key="mix_input_place"
    )

    place_df = df[df["会場"] == race_place].copy()

    if place_df.empty:
        st.warning("この会場のデータがありません")
        st.stop()

    # -----------------------
    # 会場平均との差用
    # -----------------------
    mean_tenji = place_df["展示"].mean()
    mean_isshu = place_df["一周"].mean()

    st.caption(f"会場：{race_place}（過去データ平均との差で補正）")

    # -----------------------
    # 入力
    # -----------------------
    st.markdown("### 📝 展示・1周・ST 入力")

    input_cols = st.columns(6)

    tenji_input = {}
    isshu_input = {}
    st_input    = {}
    eval_input  = {}

    eval_list = ["", "◎", "◯", "△", "×"]

    for i in range(1, 7):

        with input_cols[i - 1]:

            st.markdown(f"**{i}号艇**")

            tenji_input[i] = st.number_input(
                "展示",
                step=0.01,
                format="%.2f",
                key=f"mix_tenji_{i}"
            )

            isshu_input[i] = st.number_input(
                "一周",
                step=0.01,
                format="%.2f",
                key=f"mix_isshu_{i}"
            )

            st_input[i] = st.number_input(
                "ST",
                step=0.01,
                format="%.2f",
                key=f"mix_st_{i}"
            )

            eval_input[i] = st.selectbox(
                "評価",
                eval_list,
                key=f"mix_eval_{i}"
            )

    # -----------------------
    # スコア計算
    # -----------------------
    eval_map = {
        "◎": 2.0,
        "◯": 1.0,
        "△": 0.5,
        "×": -1.0
    }

    rows = []

    for boat in range(1, 7):

        st_score = -st_input[boat] + eval_map.get(eval_input[boat], 0)

        tenji_diff = mean_tenji - tenji_input[boat]
        isshu_diff = mean_isshu - isshu_input[boat]

        total = (
            st_score
            + tenji_diff * 2.0
            + isshu_diff * 0.3
        )

        rows.append({
            "艇番": boat,
            "展示": tenji_input[boat],
            "一周": isshu_input[boat],
            "ST": st_input[boat],
            "評価": eval_input[boat],
            "start_score": total
        })

    result_df = pd.DataFrame(rows)

    # -----------------------
    # 表
    # -----------------------
    st.markdown("### 📊 スタート指数")

    st.dataframe(
        result_df.sort_values("start_score", ascending=False),
        use_container_width=True
    )

    # -----------------------
    # スリット表示
    # -----------------------
    st.markdown("### 🟦 スリット予想イメージ")

    st.markdown('<div class="slit-area">', unsafe_allow_html=True)
    st.markdown('<div class="slit-line"></div>', unsafe_allow_html=True)

    for _, r in result_df.iterrows():

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
                    展示 {r["展示"]:.2f}
                    一周 {r["一周"]:.2f}<br>
                    ST {r["ST"]:.2f} {r["評価"]}
                </div>
            </div>
        </div>
        """

        st.markdown(html, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------
# 閲覧用：女子戦データ
# -----------------------------
with tab_view:

    st.subheader("👩 女子戦データ閲覧")

    ws = sh.worksheet("管理用_NEW")
    df = pd.DataFrame(ws.get_all_records())

    if df.empty:
        st.info("データがありません")

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

# -----------------------------
# 👩 女子戦専用 補正入力・閲覧
# -----------------------------
with tab_women_input:

    st.subheader("👩 女子戦｜展示入力 → 場平均補正")

    ws = sh.worksheet("管理用_NEW")
    df = pd.DataFrame(ws.get_all_records())

    if df.empty:
        st.info("データがありません")

    need_cols = ["女子戦","会場","艇番","展示","直線","一周","回り足"]
    for c in need_cols:
        if c not in df.columns:
            st.error(f"{c} 列が見つかりません")
            st.stop()

    for c in ["艇番","展示","直線","一周","回り足"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # 女子戦だけ
    women_df = df[
        df["女子戦"].astype(str).str.lower().isin(
            ["true","1","yes","y","○"]
        )
    ].copy()

    if women_df.empty:
        st.info("女子戦データがまだありません")
        st.stop()

    # 会場選択
    place_list = sorted(women_df["会場"].dropna().unique())
    place = st.selectbox("会場を選択", place_list, key="women_input_place")

    place_df = women_df[women_df["会場"] == place].copy()

    st.caption(f"{place}｜女子戦データ件数：{len(place_df)} 件")

    st.divider()

    # ------------------------
    # 色付け（1位 赤 / 2位 黄）
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
    st.markdown("### 展示入力（女子戦・当日データ）")

    input_rows = []

    header_cols = st.columns(6)
    for i in range(6):
        header_cols[i].markdown(f"**{i+1}号艇**")

    row1 = st.columns(6)  # 展示
    row2 = st.columns(6)  # 直線
    row3 = st.columns(6)  # 一周
    row4 = st.columns(6)  # 回り足

    tenji_vals = {}
    choku_vals = {}
    isshu_vals = {}
    mawari_vals = {}

    for b in range(1, 7):

        tenji_vals[b] = row1[b-1].number_input(
            "展示",
            step=0.01,
            format="%.2f",
            value=6.50,
            key=f"women_tenji_{b}"
        )

        choku_vals[b] = row2[b-1].number_input(
            "直線",
            step=0.01,
            format="%.2f",
            value=6.90,
            key=f"women_choku_{b}"
        )

        isshu_vals[b] = row3[b-1].number_input(
            "一周",
            step=0.01,
            format="%.2f",
            value=37.00,
            key=f"women_isshu_{b}"
        )

        mawari_vals[b] = row4[b-1].number_input(
            "回り足",
            step=0.01,
            format="%.2f",
            value=5.00,
            key=f"women_mawari_{b}"
        )

        input_rows.append({
            "艇番": b,
            "展示": tenji_vals[b],
            "直線": choku_vals[b],
            "一周": isshu_vals[b],
            "回り足": mawari_vals[b]
        })

    input_df = pd.DataFrame(input_rows).set_index("艇番")

    st.divider()

    # ------------------------
    # 入力値
    # ------------------------
    st.markdown("### 入力値（女子戦）")

    st.dataframe(
        highlight_rank(input_df),
        use_container_width=True
    )

    # ------------------------
    # 女子戦・場平均補正
    # ------------------------
    st.divider()
    st.markdown("### 女子戦・場平均補正タイム")

    lane_mean = (
        place_df
        .groupby("艇番")[["展示","直線","一周","回り足"]]
        .mean()
    )

    overall_mean = place_df[["展示","直線","一周","回り足"]].mean()

    adj_df = input_df.copy()

    for b in range(1, 7):
        if b in lane_mean.index:
            for col in ["展示","直線","一周","回り足"]:
                if pd.notna(input_df.loc[b, col]) and pd.notna(lane_mean.loc[b, col]):
                    adj_df.loc[b, col] = (
                        input_df.loc[b, col]
                        - lane_mean.loc[b, col]
                        + overall_mean[col]
                    )

    st.dataframe(
        highlight_rank(adj_df),
        use_container_width=True
    )

    # ------------------------
    # 女子戦・枠番補正込み
    # ------------------------
    st.divider()
    st.markdown("### 女子戦・枠番補正込みタイム")

    lane_bias = lane_mean - overall_mean

    final_df = adj_df.copy()

    for b in range(1, 7):
        if b in lane_bias.index:
            for col in ["展示","直線","一周","回り足"]:
                if pd.notna(adj_df.loc[b, col]) and pd.notna(lane_bias.loc[b, col]):
                    final_df.loc[b, col] = (
                        adj_df.loc[b, col]
                        - lane_bias.loc[b, col]
                    )

    st.dataframe(
        highlight_rank(final_df),
        use_container_width=True
    )

# --- 女子戦スタート予想（会場だけ・入力式＋スリット） ---
with tab_women_start:

    st.subheader("👩 女子戦スタート予想（会場補正・入力式）")

    if women_df.empty:
        st.warning("女子戦データがありません")

    use_cols = ["展示", "一周", "ST"]
    for c in use_cols:
        women_df[c] = pd.to_numeric(women_df[c], errors="coerce")

    # ------------------------
    # 会場だけ選択
    # ------------------------
    sel_place = st.selectbox(
        "会場を選択（女子戦）",
        sorted(women_df["会場"].dropna().unique()),
        key="women_place_select"
    )

    place_women = women_df[women_df["会場"] == sel_place].copy()

    if place_women.empty:
        st.warning("この会場の女子戦データがありません")
        st.stop()

    # ------------------------
    # 女子戦・会場平均
    # ------------------------
    mean_tenji = place_women["展示"].mean()
    mean_isshu = place_women["一周"].mean()

    st.caption(
        f"女子戦平均（{sel_place}）  展示={mean_tenji:.2f}  一周={mean_isshu:.2f}"
    )

    st.divider()

    # ------------------------
    # 入力（横並び）
    # ------------------------
    st.markdown("### 📝 当日入力")

    input_cols = st.columns(6)

    tenji_input = {}
    isshu_input = {}
    st_input    = {}

    for boat in range(1, 7):

        with input_cols[boat - 1]:

            st.markdown(f"**{boat}号艇**")

            tenji_input[boat] = st.number_input(
                "展示",
                step=0.01,
                format="%.2f",
                key=f"women_tenji_in_{boat}"
            )

            isshu_input[boat] = st.number_input(
                "一周",
                step=0.01,
                format="%.2f",
                key=f"women_isshu_in_{boat}"
            )

            st_input[boat] = st.number_input(
                "ST",
                step=0.01,
                format="%.2f",
                key=f"women_st_in_{boat}"
            )

    # ------------------------
    # 表用データ
    # ------------------------
    table_rows = []

    for boat in range(1, 7):

        tenji_diff = mean_tenji - tenji_input[boat]
        isshu_diff = mean_isshu - isshu_input[boat]

        start_score = (
            -st_input[boat]
            + tenji_diff * 2.0
            + isshu_diff * 0.3
        )

        table_rows.append({
            "艇番": boat,
            "展示": tenji_input[boat],
            "一周": isshu_input[boat],
            "ST": st_input[boat],
            "女子戦スタート指数": start_score
        })

    result_df = pd.DataFrame(table_rows).set_index("艇番")

    st.divider()

    # ------------------------
    # 表
    # ------------------------
    st.markdown("### 📊 女子戦スタート指数")

    def highlight_best(s):
        s2 = pd.to_numeric(s, errors="coerce")
        rank = s2.rank(ascending=False, method="min")
        out = []
        for r in rank:
            if r == 1:
                out.append("background-color:#ff6b6b")
            elif r == 2:
                out.append("background-color:#ffd43b")
            else:
                out.append("")
        return out

    st.dataframe(
        result_df.style.apply(
            highlight_best,
            subset=["女子戦スタート指数"]
        ),
        use_container_width=True
    )

    # ------------------------
    # スリット表示（表の下）
    # ------------------------
    st.divider()
    st.markdown("### 🟦 女子戦スリット予想")

    sorted_df = result_df.sort_values("女子戦スタート指数", ascending=False)

    st.markdown('<div class="slit-area">', unsafe_allow_html=True)
    st.markdown('<div class="slit-line"></div>', unsafe_allow_html=True)

    for boat, r in sorted_df.iterrows():

        score = float(r["女子戦スタート指数"])

        offset = max(0, min(160, (score + 0.5) * 120))

        img_path = os.path.join(BASE_DIR, "images", f"boat{boat}.png")
        img_base64 = encode_image(img_path)

        html = f"""
        <div class="slit-row">
            <div class="slit-boat" style="margin-left:{offset}px;">
                <img src="data:image/png;base64,{img_base64}" height="42">
                <div style="margin-left:10px;font-size:13px;">
                    <b>{boat}号艇</b><br>
                    指数 {score:.2f}<br>
                    展示 {r["展示"]:.2f}　
                    一周 {r["一周"]:.2f}　
                    ST {r["ST"]:.2f}
                </div>
            </div>
        </div>
        """

        st.markdown(html, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
# -----------------------------
# 👩 女子戦スタート指数｜検証タブ
# -----------------------------
with tab_women_result:

    st.subheader("👩 女子戦｜スタート指数 精度検証")

    ws = sh.worksheet("管理用_NEW")
    df = pd.DataFrame(ws.get_all_records())

    if df.empty:
        st.info("データがありません")

    need_cols = [
        "女子戦","日付","会場","レース番号",
        "艇番","展示","一周","ST","スタート評価","着順"
    ]

    for c in need_cols:
        if c not in df.columns:
            st.error(f"{c} 列が見つかりません")
            st.stop()

    # 型変換
    for c in ["艇番","展示","一周","ST","着順"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # 女子戦だけ
    women_df = df[
        df["女子戦"].astype(str).str.lower().isin(
            ["true","1","yes","y","○"]
        )
    ].copy()

    if women_df.empty:
        st.info("女子戦データがまだありません")
        st.stop()

    # -------------------------
    # 会場選択
    # -------------------------
    place_list = sorted(women_df["会場"].dropna().unique())
    place = st.selectbox("会場", place_list, key="women_verify_place")

    target = women_df[women_df["会場"] == place].copy()

    # -------------------------
    # スタート指数を再計算
    # （女子戦タブと同じロジック）
    # -------------------------
    eval_map = {
        "◎": 2.0,
        "◯": 1.0,
        "△": 0.5,
        "×": -1.0
    }

    target["評価補正"] = target["スタート評価"].map(eval_map).fillna(0)

    place_df = women_df[women_df["会場"] == place]

    mean_tenji = place_df["展示"].mean()
    mean_isshu = place_df["一周"].mean()

    target["指数"] = (
        -target["ST"].fillna(0)
        + target["評価補正"]
        + (mean_tenji - target["展示"]) * 2.0
        + (mean_isshu - target["一周"]) * 0.3
    )

    # -------------------------
    # レース単位で集計
    # -------------------------
    results = []

    for (d, r), g in target.groupby(["日付","レース番号"]):

        if len(g) < 6:
            continue

        g = g.sort_values("指数", ascending=False)

        top1 = int(g.iloc[0]["艇番"])
        top2 = int(g.iloc[1]["艇番"])
        top3 = int(g.iloc[2]["艇番"])

        winner = g[g["着順"] == 1]["艇番"]
        second = g[g["着順"] == 2]["艇番"]
        third = g[g["着順"] == 3]["艇番"]

        if len(winner)==0:
            continue

        winner = int(winner.iloc[0])
        second = int(second.iloc[0]) if len(second)>0 else None
        third  = int(third.iloc[0])  if len(third)>0 else None

        results.append({
            "日付": d,
            "R": r,
            "指数1位": top1,
            "指数2位": top2,
            "指数3位": top3,
            "1着": winner,
            "2着": second,
            "3着": third,
            "1位的中": top1 == winner,
            "連対的中": winner in [top1,top2],
            "3連対的中": winner in [top1,top2,top3]
        })

    if len(results) == 0:
        st.info("検証できるレースがまだありません")
        st.stop()

    res_df = pd.DataFrame(results)

    total = len(res_df)

    hit1 = res_df["1位的中"].mean() * 100
    hit2 = res_df["連対的中"].mean() * 100
    hit3 = res_df["3連対的中"].mean() * 100

    # -------------------------
    # サマリー表示
    # -------------------------
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("検証レース数", total)
    c2.metric("指数1位 → 1着率", f"{hit1:.1f}%")
    c3.metric("指数上位2艇 連対率", f"{hit2:.1f}%")
    c4.metric("指数上位3艇 1着包含率", f"{hit3:.1f}%")

    st.divider()

    st.dataframe(res_df, use_container_width=True)

# -----------------------------
# 🧑‍🤝‍🧑 混合戦スタート指数｜検証タブ
# -----------------------------
with tab_mix_check:

    st.subheader("🧑‍🤝‍🧑 混合戦｜スタート指数 精度検証")

    ws = sh.worksheet("管理用_NEW")
    df = pd.DataFrame(ws.get_all_records())

    if df.empty:
        st.info("データがありません")
        st.stop()

    need_cols = [
        "女子戦","日付","会場","レース番号",
        "艇番","展示","一周","ST","スタート評価","着順"
    ]

    for c in need_cols:
        if c not in df.columns:
            st.error(f"{c} 列が見つかりません")
            st.stop()

    # 型変換
    for c in ["艇番","展示","一周","ST","着順"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # -------------------------
    # 混合戦のみ（女子戦ではないもの）
    # -------------------------
    mix_df = df[
        ~df["女子戦"].astype(str).str.lower().isin(
            ["true","1","yes","y","○"]
        )
    ].copy()

    if mix_df.empty:
        st.info("混合戦データがまだありません")
        st.stop()

    # -------------------------
    # 会場選択
    # -------------------------
    place_list = sorted(mix_df["会場"].dropna().unique())
    place = st.selectbox("会場", place_list, key="mix_verify_place")

    target = mix_df[mix_df["会場"] == place].copy()

    # -------------------------
    # スタート指数を再計算
    # （女子戦タブと同じロジック）
    # -------------------------
    eval_map = {
        "◎": 2.0,
        "◯": 1.0,
        "△": 0.5,
        "×": -1.0
    }

    target["評価補正"] = target["スタート評価"].map(eval_map).fillna(0)

    place_df = mix_df[mix_df["会場"] == place]

    mean_tenji = place_df["展示"].mean()
    mean_isshu = place_df["一周"].mean()

    target["指数"] = (
        -target["ST"].fillna(0)
        + target["評価補正"]
        + (mean_tenji - target["展示"]) * 2.0
        + (mean_isshu - target["一周"]) * 0.3
    )

    # -------------------------
    # レース単位で集計
    # -------------------------
    results = []

    for (d, r), g in target.groupby(["日付","レース番号"]):

        if len(g) < 6:
            continue

        g = g.sort_values("指数", ascending=False)

        top1 = int(g.iloc[0]["艇番"])
        top2 = int(g.iloc[1]["艇番"])
        top3 = int(g.iloc[2]["艇番"])

        winner = g[g["着順"] == 1]["艇番"]
        second = g[g["着順"] == 2]["艇番"]
        third  = g[g["着順"] == 3]["艇番"]

        if len(winner) == 0:
            continue

        winner = int(winner.iloc[0])
        second = int(second.iloc[0]) if len(second) > 0 else None
        third  = int(third.iloc[0])  if len(third)  > 0 else None

        results.append({
            "日付": d,
            "R": r,
            "指数1位": top1,
            "指数2位": top2,
            "指数3位": top3,
            "1着": winner,
            "2着": second,
            "3着": third,
            "1位的中": top1 == winner,
            "連対的中": winner in [top1, top2],
            "3連対的中": winner in [top1, top2, top3]
        })

    if len(results) == 0:
        st.info("検証できるレースがまだありません")
        st.stop()

    res_df = pd.DataFrame(results)

    total = len(res_df)

    hit1 = res_df["1位的中"].mean() * 100
    hit2 = res_df["連対的中"].mean() * 100
    hit3 = res_df["3連対的中"].mean() * 100

    # -------------------------
    # サマリー表示（女子戦と同じ）
    # -------------------------
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("検証レース数", total)
    c2.metric("指数1位 → 1着率", f"{hit1:.1f}%")
    c3.metric("指数上位2艇 連対率", f"{hit2:.1f}%")
    c4.metric("指数上位3艇 1着包含率", f"{hit3:.1f}%")

    st.divider()

    st.dataframe(res_df, use_container_width=True)

# --- タブ：条件補正 ---
with tab_cond:

    st.subheader("🌊 条件別 補正データ（風・波・会場）")

    ws = sh.worksheet("管理用_NEW")
    df = pd.DataFrame(ws.get_all_records())

    if df.empty:
        st.warning("管理用_NEW にデータがありません")
    else:

        # 数値化
        for c in ["展示","直線","一周","回り足","艇番","風速","波高"]:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce")

        # セレクト用候補（空対策）
        place_list = sorted(df["会場"].dropna().unique())
        wind_list  = sorted(df["風向き"].dropna().unique())

        if len(place_list) == 0 or len(wind_list) == 0:
            st.warning("会場または風向きのデータがありません")
        else:

            # -----------------------
            # 条件入力
            # -----------------------
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                place = st.selectbox(
                    "会場",
                    place_list,
                    key="cond_place"
                )

            with col2:
                wind = st.selectbox(
                    "風向き",
                    wind_list,
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

            st.caption(f"抽出レコード数：{len(cond_df)} 件")

            if cond_df.empty:
                st.warning("条件に一致するデータがありません")
            else:

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
































































