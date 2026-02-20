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

st.title("🚤 競艇 Pro ハイブリッド解析システム")

# タブ構成
tab_pre, tab_stat, tab_log, tab_memo, tab5 = st.tabs(["⭐ 事前簡易予想", "📊 統計解析", "📜 過去ログ", "📝 攻略メモ","スタート予想"])

# --- タブ1：事前簡易予想 ---
with tab_pre:
    st.subheader("各艇の4項目・記号評価")
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
    st.subheader("会場別 補正・総合順位")
    if not df.empty:
        place_list = sorted(df["会場"].dropna().unique())
        place = st.selectbox("会場を選択", place_list, key="stat_place_select")
        df_view = df[df["会場"] == place].copy()

        # 数値化
        for b in range(1, 7):
            for c in ["展示", "直線", "一周", "回り足"]:
                col = f"{c}{b}"
                if col in df_view.columns:
                    df_view[col] = pd.to_numeric(df_view[col], errors="coerce")

        # 平均計算 & 入力
        mean_each_boat = {}
        cols = st.columns(6)
        input_data = {}
        for b in range(1, 7):
            mean_each_boat[b] = {c: df_view[f"{c}{b}"].mean() if f"{c}{b}" in df_view.columns else 0 for c in ["展示", "直線", "一周", "回り足"]}
            with cols[b - 1]:
                st.markdown(f"**{b}号艇**")
                tenji = st.number_input("展示", value=6.50, step=0.01, key=f"stat_tenji_{b}")
                input_data[b] = {"展示": tenji, "直線": 6.90, "一周": 37.0, "回り足": 5.0} # 簡易化

        # スコア計算表示
        st.write("補正計算結果を表示します...")
    else:
        st.warning("データが読み込めていません")

# --- タブ3：過去ログ ---
with tab_log:
    st.dataframe(df)

# --- タブ4：攻略メモ ---
with tab_memo:
    st.write("攻略メモ機能")

# --- タブ5：スタート予想 ---
with tab5:

    st.subheader("🚀 スタート予想（場別補正＋展示＋1周）")

    ws_new = sh.worksheet("管理用_NEW")
    df_new = pd.DataFrame(ws_new.get_all_records())

    if df_new.empty:
        st.info("データがありません")
        st.stop()

    # 数値化
    for c in ["展示","一周","ST"]:
        df_new[c] = pd.to_numeric(df_new[c], errors="coerce")

    # -----------------------
    # 会場選択
    # -----------------------
    place_list = sorted(df_new["会場"].dropna().unique())

    place = st.selectbox(
        "会場を選択",
        place_list,
        key="tab5_place"
    )

    df_place = df_new[df_new["会場"] == place].copy()

    # -----------------------
    # 当日展示入力
    # -----------------------
    st.markdown("### 🧮 当日の展示タイム入力")

    input_tenji = {}
    input_isshu = {}

    cols = st.columns(6)

    for b in range(1, 7):
        with cols[b-1]:
            st.markdown(f"**{b}号艇**")
            input_tenji[b] = st.number_input(
                "展示",
                step=0.01,
                format="%.2f",
                key=f"tab5_tenji_{b}"
            )
            input_isshu[b] = st.number_input(
                "1周",
                step=0.01,
                format="%.2f",
                key=f"tab5_isshu_{b}"
            )

    st.divider()

    # -----------------------
    # 直近レース（ST＋評価用）
    # -----------------------
# その会場の最新レースだけ取得
latest_key = (
    df_place.sort_values("登録日時")
    .iloc[-1][["日付", "会場", "レース番号"]]
)

base = df_place[
    (df_place["日付"] == latest_key["日付"]) &
    (df_place["会場"] == latest_key["会場"]) &
    (df_place["レース番号"] == latest_key["レース番号"])
].copy()

# ← ここからもインデントをずらさない
if len(base) < 6:
    st.warning("このレースのデータが6艇そろっていません")
    st.stop()

    if len(base) < 6:
        st.warning("この会場のデータがまだ少ないです")

    eval_map = {
        "◎": 2.0,
        "◯": 1.0,
        "△": 0.5,
        "×": -1.0,
        "": 0.0
    }

    base["評価補正"] = base["スタート評価"].map(eval_map).fillna(0)

    # -----------------------
    # 会場平均との差
    # -----------------------
    tenji_mean = df_place.groupby("艇番")["展示"].mean()
    isshu_mean = df_place.groupby("艇番")["一周"].mean()

    rows = []

    for _, r in base.iterrows():

        b = int(r["艇番"])

        tenji_diff = 0
        isshu_diff = 0

        if b in tenji_mean and input_tenji[b] > 0:
            tenji_diff = tenji_mean[b] - input_tenji[b]

        if b in isshu_mean and input_isshu[b] > 0:
            isshu_diff = isshu_mean[b] - input_isshu[b]

        # -----------------------
        # 最終スコア
        # -----------------------
        score = (
            - r["ST"]
            + r["評価補正"]
            + tenji_diff * 2.0
            + isshu_diff * 0.3
        )

        rows.append({
            "艇番": b,
            "ST": r["ST"],
            "スタート評価": r["スタート評価"],
            "score": score
        })

    result = pd.DataFrame(rows)
    result = result.sort_values("艇番")

    st.markdown("### 🟦 スリット予想イメージ")

    st.markdown('<div class="slit-area">', unsafe_allow_html=True)
    st.markdown('<div class="slit-line"></div>', unsafe_allow_html=True)

    for _, r in result.iterrows():

        boat_no = int(r["艇番"])
        score   = float(r["score"])

        offset = max(0, min(160, (score + 0.5) * 120))

        img_path = os.path.join(BASE_DIR, "images", f"boat{boat_no}.png")
        img_base64 = encode_image(img_path)

        html = f"""
        <div class="slit-row">
            <div class="slit-boat" style="margin-left:{offset}px;">
                <img src="data:image/png;base64,{img_base64}" height="48">
                <div style="margin-left:8px;font-size:13px;">
                    <b>{boat_no}号艇</b><br>
                    score {score:.2f}
                </div>
            </div>
        </div>
        """

        st.markdown(html, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)






