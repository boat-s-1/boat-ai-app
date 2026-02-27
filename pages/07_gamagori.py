import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="競艇Pro 蒲郡", layout="wide")

PLACE_NAME = "蒲郡"

# 戻るボタン
if st.button("← 会場選択へ戻る", key="back_to_home_gamagori"):
    st.switch_page("public_app.py")

# -------------------------
# 認証
# -------------------------
def get_gsheet_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    try:
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=scopes
        )
        return gspread.authorize(credentials)
    except:
        return None


# ==============================
# レース種別選択
# ==============================
if "selected_place" not in st.session_state:
    st.session_state.selected_place = None

if st.session_state.selected_place is None:

    st.title("🏁 レース種別を選択")

    cols = st.columns(4)

    if cols[0].button("混合戦", use_container_width=True):
        st.session_state.selected_place = "蒲郡混合戦"
        st.rerun()

    if cols[1].button("女子戦", use_container_width=True):
        st.session_state.selected_place = "蒲郡女子戦"
        st.rerun()

    cols[2].button("G1競走（準備中）", disabled=True, use_container_width=True)
    cols[3].button("SG競走（準備中）", disabled=True, use_container_width=True)

    st.stop()


# ==============================
# ここから本体
# ==============================
place = st.session_state.selected_place
st.caption(f"選択中の会場：{place}")

SHEET_MAP = {
    "蒲郡混合戦": {
        "sheet1": "蒲郡_混合統計シート",
        "sheet2": "蒲郡_混合統計シート②"
    },
    "蒲郡女子戦": {
        "sheet1": "蒲郡_女子統計シート",
        "sheet2": "蒲郡_女子統計シート②"
    },
}

gc = get_gsheet_client()

if gc is None:
    st.error("Google認証に失敗しました")
    st.stop()

try:
    sh = gc.open_by_key("1lN794iGtyGV2jNwlYzUA8wEbhRwhPM7FxDAkMaoJss4")

    ws1 = sh.worksheet(SHEET_MAP[place]["sheet1"]) 
    ws2 = sh.worksheet(SHEET_MAP[place]["sheet2"])

    rows1 = ws1.get_all_records()
    rows2 = ws2.get_a ll_records()

    df = pd.DataFrame(rows1 + rows2)
    st.session_state["base_df"] = df
    
except Exception as e:
    st.error("シート読み込みエラー")
    st.exception(e)
    st.stop()


st.title("予想ツール")

st.write("読み込み件数")
st.write(len(df))

# タブ構成
tab_kani, tab_tokei = st.tabs(["⭐ 簡易予想","統計解析"])

# -------------------------
# 選択中会場の受け取り
# -------------------------
if "selected_place" not in st.session_state:
    st.warning("会場が選択されていません")
    st.stop()

PLACE_NAME = st.session_state.selected_place


# --- タブ1：事前簡易予想 ---
with tab_kani:

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


