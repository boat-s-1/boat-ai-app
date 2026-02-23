import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="BOAT AI（無料版）", layout="wide")

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

st.title("🚤 BOAT AI（無料版）")

tab1, tab2, tab3,tab_mix_check = st.tabs([
    "📊 基本予想",
    "🌊 条件補正",
    "🗂 データ状況",
    "🗂 混合戦"
])

with tab3:

    st.subheader("🗂 データ読み込み状況")

    try:
        ws = sh.worksheet("管理用_NEW")
        df = pd.DataFrame(ws.get_all_records())

        st.write("総レコード数：", len(df))
        st.dataframe(df.head(20))
# -----------------------------
# 🚤 混合戦スタート指数｜検証タブ（無料版）
# -----------------------------
with tab_mix_check:

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

    # -------------------------
    # 型変換
    # -------------------------
    for c in ["艇番","展示","一周","ST","着順"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # -------------------------
    # 会場選択（無料版は会場のみ）
    # -------------------------
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

    # -------------------------
    # スタート指数 再計算
    # -------------------------
    eval_map = {
        "◎": 2.0,
        "◯": 1.0,
        "△": 0.5,
        "×": -1.0
    }

    target["評価補正"] = target["スタート評価"].map(eval_map).fillna(0)

    place_df = df[df["会場"] == place]

    mean_tenji = place_df["展示"].mean()
    mean_isshu = place_df["一周"].mean()

    target["指数"] = (
        -target["ST"].fillna(0)
        + target["評価補正"]
        + (mean_tenji - target["展示"]) * 2.0
        + (mean_isshu - target["一周"]) * 0.3
    )

    # -------------------------
    # レース単位で検証
    # -------------------------
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
        st.info("検証できるレースがまだありません")
        st.stop()

    res_df = pd.DataFrame(results)

    total = len(res_df)

    hit1 = res_df["1位的中"].mean() * 100
    hit2 = res_df["連対的中"].mean() * 100
    hit3 = res_df["3連対的中"].mean() * 100

    # -------------------------
    # サマリー
    # -------------------------
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("検証レース数", total)
    c2.metric("指数1位 → 1着率", f"{hit1:.1f}%")
    c3.metric("指数上位2艇 連対率", f"{hit2:.1f}%")
    c4.metric("指数上位3艇 1着包含率", f"{hit3:.1f}%")

    st.divider()

    st.dataframe(res_df, use_container_width=True)
    except Exception as e:
        st.error("シートが読み込めません")
        st.exception(e)



