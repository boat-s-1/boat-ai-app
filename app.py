import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# -----------------------
# GoogleSheet 接続（重要）
# -----------------------
@st.cache_resource
def get_spreadsheet():

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scopes
    )

    gc = gspread.authorize(credentials)

    return gc.open("競艇予想学習データ")


sh = get_spreadsheet()


# -----------------------
# ページ設定
# -----------------------
st.set_page_config(layout="wide")
st.title("🚤 競艇予想 管理ツール")

tab4, = st.tabs(["🛠 管理用入力"])


# =========================================================
# タブ4：管理用入力（完全版）
# =========================================================
with tab4:

    st.subheader("🛠 管理用データ入力")

    ws_master = sh.worksheet("管理用_NEW")

    place_list = [
        "桐生","戸田","江戸川","平和島","多摩川",
        "浜名湖","蒲郡","常滑","津","三国",
        "びわこ","住之江","尼崎","鳴門","丸亀",
        "児島","宮島","徳山","下関","若松",
        "芦屋","福岡","唐津","大村"
    ]

    col1, col2, col3 = st.columns(3)

    with col1:
        date = st.date_input("日付", key="tab4_date")

    with col2:
        place = st.selectbox("会場", place_list, key="tab4_place")

    with col3:
        race_no = st.number_input("レース番号", 1, 12, 1, key="tab4_race")

    # 女子戦フラグ
    is_women = st.checkbox("👩 女子戦", key="tab4_women")

    st.divider()

    # ------------------------
    # 展示データ入力
    # ------------------------
    st.markdown("## 📊 展示データ入力（1周 → 回り足 → 直線 → 展示）")

    for boat in range(1, 7):

        st.markdown(f"### 🚤 {boat}号艇")

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.number_input("一周", step=0.01, format="%.2f",
                            key=f"tab4_isshu_{boat}")

        with c2:
            st.number_input("回り足", step=0.01, format="%.2f",
                            key=f"tab4_mawari_{boat}")

        with c3:
            st.number_input("直線", step=0.01, format="%.2f",
                            key=f"tab4_choku_{boat}")

        with c4:
            st.number_input("展示", step=0.01, format="%.2f",
                            key=f"tab4_tenji_{boat}")

    st.divider()

    # ------------------------
    # 結果入力
    # ------------------------
    st.markdown("## 🏁 結果入力")

    w1, w2, w3 = st.columns(3)

    with w1:
        wind_dir = st.radio(
            "風向き",
            ["無風","北","北東","東","南東","南","南西","西","北西"],
            horizontal=True,
            key="tab4_wind"
        )

    with w2:
        wind_speed = st.number_input(
            "風速（m）",
            min_value=0.0,
            step=1.0,
            format="%.1f",
            key="tab4_wind_speed"
        )

    with w3:
        wave_height = st.number_input(
            "波高（cm）",
            min_value=0.0,
            step=1.0,
            format="%.0f",
            key="tab4_wave"
        )

    st.divider()

    # ---- ST ----
    st.markdown("### スタート（ST）")

    cols = st.columns(6)
    for boat in range(1, 7):
        with cols[boat - 1]:
            st.number_input(
                f"{boat}号艇",
                step=0.01,
                format="%.2f",
                key=f"tab4_st_{boat}"
            )

    # ---- スタート評価 ----
    st.markdown("### スタート評価")

    cols = st.columns(6)
    for boat in range(1, 7):
        with cols[boat - 1]:
            st.selectbox(
                f"{boat}号艇",
                ["", "◎", "◯", "△", "×"],
                key=f"tab4_eval_{boat}"
            )

    # ---- 着順 ----
    st.markdown("### 着順")

    cols = st.columns(6)
    for boat in range(1, 7):
        with cols[boat - 1]:
            st.number_input(
                f"{boat}号艇",
                1, 6, 1,
                key=f"tab4_rank_{boat}"
            )

    st.divider()

    # ------------------------
    # 登録処理
    # ------------------------
    if st.button("このレースを登録する", key="tab4_save"):

        now = pd.Timestamp.now()

        rows = []

        for boat in range(1, 7):

            rows.append([
                str(date),                                      # 日付
                now,                                            # 登録日時
                place,                                          # 会場
                race_no,                                        # レース番号
                boat,                                           # 艇番
                st.session_state[f"tab4_tenji_{boat}"],         # 展示
                st.session_state[f"tab4_choku_{boat}"],         # 直線
                st.session_state[f"tab4_isshu_{boat}"],         # 一周
                st.session_state[f"tab4_mawari_{boat}"],        # 回り足
                st.session_state[f"tab4_st_{boat}"],            # ST
                wind_dir,                                       # 風向き
                st.session_state["tab4_wind_speed"],            # 風速
                st.session_state["tab4_wave"],                  # 波高
                st.session_state[f"tab4_rank_{boat}"],          # 着順
                st.session_state[f"tab4_eval_{boat}"],          # スタート評価
                is_women                                        # 女子戦
            ])

        ws_master.append_rows(
            pd.DataFrame(rows).astype(str).values.tolist()
        )

        st.success("登録しました！")


