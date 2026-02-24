import streamlit as st
import pandas as pd
import os
import base64

import gspread
from google.oauth2.service_account import Credentials

# ------------------
# 基本設定
# ------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(page_title="BOAT AI（無料版）", layout="wide")


# ------------------
# 画像読み込み
# ------------------
def encode_image(path):
    try:
        if not os.path.exists(path):
            return ""
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""


# ------------------
# Google Sheets 接続
# ------------------
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope,
)

gc = gspread.authorize(credentials)

SPREADSHEET_KEY = st.secrets["spreadsheet_key"]
sh = gc.open_by_key(SPREADSHEET_KEY)


# ------------------
# タイトル
# ------------------
st.title("🚤 BOAT AI（無料版）")


# ------------------
# タブ
# ------------------
tab_pre, tab2, tab3, tab5, tab_mix_check = st.tabs([
    "📊 基本予想",
    "🌊 条件補正",
    "🗂 データ状況",
    "🗂 スタート予想",
    "🗂 混合戦"
])


# =====================================================
# データ状況
# =====================================================
with tab3:

    st.subheader("🗂 データ読み込み状況")

    try:
        ws = sh.worksheet("管理用_NEW")
        df = pd.DataFrame(ws.get_all_records())

        st.write("総レコード数：", len(df))
        st.dataframe(df.head(20), use_container_width=True)

    except Exception as e:
        st.error(e)


# =====================================================
# 混合戦 スタート指数検証
# =====================================================
with tab_mix_check:

    try:

        st.subheader("🚤 混合戦｜スタート指数 精度検証")

        ws = sh.worksheet("管理用_NEW")
        df = pd.DataFrame(ws.get_all_records())

        if df.empty:
            st.info("データがありません")
            st.stop()

        need_cols = [
            "日付","会場","レース番号",
            "艇番","展示","一周","ST","スタート評価","着順"
        ]

        for c in need_cols:
            if c not in df.columns:
                st.error(f"{c} 列が見つかりません")
                st.stop()

        for c in ["艇番","展示","一周","ST","着順"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")

        df["日付"] = pd.to_datetime(df["日付"], errors="coerce")

        place_list = sorted(df["会場"].dropna().unique())

        place = st.selectbox(
            "会場",
            place_list,
            key="mix_verify_place_free"
        )

        target = df[df["会場"] == place].copy()

        if target.empty:
            st.info("対象データがありません")
            st.stop()

        eval_map = {
            "◎": 2.0,
            "◯": 1.0,
            "△": 0.5,
            "×": -1.0
        }

        target["評価補正"] = target["スタート評価"].map(eval_map).fillna(0)

        # --- 無料版：直近30走制限 ---
        place_df = (
            target.sort_values("日付", ascending=False)
                  .groupby("艇番", as_index=False)
                  .head(30)
        )

        mean_tenji = place_df["展示"].mean()
        mean_isshu = place_df["一周"].mean()

        target["指数"] = (
            -target["ST"].fillna(0)
            + target["評価補正"]
            + (mean_tenji - target["展示"]) * 2.0
            + (mean_isshu - target["一周"]) * 0.3
        )

        results = []

        for (d, r), g in target.groupby(["日付","レース番号"]):

            g = g.dropna(subset=["艇番","指数","着順"])

            if len(g) < 6:
                continue

            g = g.sort_values("指数", ascending=False)

            try:
                top1 = int(g.iloc[0]["艇番"])
                top2 = int(g.iloc[1]["艇番"])
                top3 = int(g.iloc[2]["艇番"])
            except:
                continue

            win = g[g["着順"] == 1]["艇番"]
            sec = g[g["着順"] == 2]["艇番"]
            thi = g[g["着順"] == 3]["艇番"]

            if len(win) == 0:
                continue

            winner = int(win.iloc[0])
            second = int(sec.iloc[0]) if len(sec) else None
            third  = int(thi.iloc[0]) if len(thi) else None

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
            st.info("検証できるレースがありません")
            st.stop()

        res_df = pd.DataFrame(results)

        total = len(res_df)

        hit1 = res_df["1位的中"].mean() * 100
        hit2 = res_df["連対的中"].mean() * 100
        hit3 = res_df["3連対的中"].mean() * 100

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("検証レース数", total)
        c2.metric("指数1位 → 1着率", f"{hit1:.1f}%")
        c3.metric("指数上位2艇 連対率", f"{hit2:.1f}%")
        c4.metric("指数上位3艇 1着包含率", f"{hit3:.1f}%")

        st.divider()
        st.dataframe(res_df, use_container_width=True)

    except Exception as e:
        st.error(e)


# =====================================================
# スタート予想（入力型）
# =====================================================
# --- タブ5：スタート予想（混合戦・入力型｜無料版） ---
with tab5:

    st.subheader("🚀 スタート予想（混合戦｜会場別補正・入力型）")

    ws = sh.worksheet("管理用_NEW")
    df = pd.DataFrame(ws.get_all_records())

    if df.empty:
        st.info("データがありません")
        st.stop()

    # 型変換
    for c in ["展示", "一周", "ST", "艇番"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # -----------------------
    # 会場選択
    # -----------------------
    place_list = sorted(df["会場"].dropna().unique())

    race_place = st.selectbox(
        "会場を選択",
        place_list,
        key="mix_input_place"
    )

    place_df = df[df["会場"] == race_place].copy()

    # -----------------------
    # ✅ 有料版チェック（無料版では固定）
    # -----------------------
    st.checkbox(
        "全データを使って補正する（有料版）",
        value=False,
        disabled=True
    )
    st.caption("※無料版では直近30走のみ利用できます")

    # -----------------------
    # ✅ 無料版：直近30走固定
    # -----------------------
    place_df["日付"] = pd.to_datetime(place_df["日付"], errors="coerce")

    place_df = (
        place_df
        .sort_values("日付", ascending=False)
        .groupby("艇番", as_index=False)
        .head(30)
    )

    if place_df.empty:
        st.warning("この会場のデータがありません")
        st.stop()

    # -----------------------
    # 会場平均との差用
    # -----------------------
    mean_tenji = place_df["展示"].mean()
    mean_isshu = place_df["一周"].mean()

    st.caption(f"会場：{race_place}（直近30走平均との差で補正）")

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

    result_df = result_df.sort_values("start_score", ascending=False)

    st.dataframe(
        result_df,
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

                    score = (
                        SYMBOL_VALUES[m] * WEIGHTS["モーター"]
                        + SYMBOL_VALUES[t] * WEIGHTS["当地勝率"]
                        + SYMBOL_VALUES[w] * WEIGHTS["枠番勝率"]
                        + SYMBOL_VALUES[s] * WEIGHTS["枠番スタート"]
                    )

                    boat_evals[i] = round(score, 1)

        submitted = st.form_submit_button("予想カード生成", use_container_width=True, type="primary")

    # ここが重要
    if submitted:

        sorted_boats = sorted(
            boat_evals.items(),
            key=lambda x: x[1],
            reverse=True
        )

        total_score = sum(score for _, score in sorted_boats)

        st.markdown("### 🏁 予想結果（6艇合計100％）")

        rank_colors = {
            1: "#FFD700",
            2: "#E5E5E5",
            3: "#F5CBA7"
        }

        for rank, (boat_num, score) in enumerate(sorted_boats, start=1):

            if total_score > 0:
                percent = score / total_score * 100
            else:
                percent = 0

            bg = rank_colors.get(rank, "#f6f7fb")

            st.markdown(
                f"""
                <div style="
                    background:{bg};
                    padding:14px;
                    border-radius:12px;
                    margin-bottom:10px;
                    box-shadow:0 2px 6px rgba(0,0,0,0.08);
                ">
                    <div style="font-size:16px;font-weight:700;">
                        🏁 {rank}位　{boat_num}号艇
                    </div>
                    <div style="font-size:26px;font-weight:800;">
                        {percent:.1f}%
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.progress(min(percent / 100, 1.0))
