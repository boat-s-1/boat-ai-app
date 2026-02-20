import streamlit as st
import pandas as pd
import datetime
import gspread
from google.oauth2.service_account import Credentials

# --- 1. 認証 & 接続設定 ---
def get_gsheet_client():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        if "gcp_service_account" not in st.secrets:
            return None
        credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
        return gspread.authorize(credentials)
    except:
        return None

# --- ページ設定 ---
st.set_page_config(page_title="管理者：機力分析", layout="wide")

# 会場リスト（画像に合わせて「若松」などを優先）
PLACES = ["若松", "大村", "多摩川", "蒲郡", "戸田", "江戸川", "平和島", "浜名湖", "常滑", "津", "三国", "びわこ", "住之江", "尼崎", "鳴門", "丸亀", "児島", "宮島", "徳山", "下関", "芦屋", "福岡", "唐津", "桐生"]
DIRS = ["向い風", "追い風", "左横風", "右横風", "無風"]

gc = get_gsheet_client()
sh = gc.open("競艇予想学習データ") if gc else None
ws_data = sh.worksheet("管理用_NEW") if sh else None
ws_memo = sh.worksheet("攻略メモ") if sh else None

st.title("🚤 競艇予想 Pro (管理者用)")

tab1, tab2, tab3,tab4 = st.tabs(["🕒 タイム入力", "🏁 的中データ登録", "📝 攻略メモ","詳細入力"])

# --- Tab 1: タイム入力 ---
with tab1:
    st.subheader("現在のレース：タイム入力")
    cols = st.columns(3)
    for i in range(1, 7):
        with cols[(i-1) % 3]:
            with st.expander(f"🚤 {i}号艇 タイム", expanded=True):
                # 5秒台（超抜）も入力できるように下限を 4.0 まで広げています
                st.number_input("展示タイム", 4.0, 9.0, 6.70, 0.01, key=f"ex_{i}")
                st.number_input("直線タイム", 4.0, 15.0, 7.00, 0.01, key=f"st_{i}")
                st.number_input("1周タイム", 30.0, 60.0, 37.00, 0.01, key=f"lp_{i}")
                st.number_input("回り足タイム", 3.0, 15.0, 5.00, 0.01, key=f"tn_{i}")

# --- Tab 2: 的中データ登録 ---
with tab2:
    if ws_data:
        with st.form("result_form"):
            c1, c2 = st.columns(2)
            f_place = c1.selectbox("会場", PLACES)
            f_race = c2.number_input("レース番号", 1, 12, 1) # 見出し「レース番号」に合わせました
            
            st.write("▼ 的中着順")
            res_cols = st.columns(3)
            f_w1 = res_cols[0].selectbox("1着", [1,2,3,4,5,6], key="w1")
            f_w2 = res_cols[1].selectbox("2着", [1,2,3,4,5,6], index=1, key="w2")
            f_w3 = res_cols[2].selectbox("3着", [1,2,3,4,5,6], index=2, key="w3")
            
            w_cols = st.columns(3)
            f_wdir = w_cols[0].selectbox("風向き", DIRS)
            f_wspd = w_cols[1].number_input("風速(m)", 0, 15, 0)
            f_wave = w_cols[2].number_input("波高(cm)", 0, 50, 0)

            if st.form_submit_button("3着までまとめて保存"):
                if len({f_w1, f_w2, f_w3}) < 3:
                    st.error("着順が重複しています！")
                else:
                    try:
                        def get_diffs(prefix):
                            times = [st.session_state[f"{prefix}_{i}"] for i in range(1, 7)]
                            fastest = min(times)
                            return [round(t - fastest, 3) for t in times]
                        
                        # スプレッドシートの見出し名に完全に一致させて保存
                        new_row = [
                            str(datetime.date.today()), f_place, f_race, 
                            f_w1, f_w2, f_w3, 
                            f_wdir, f_wspd, f_wave
                        ] + get_diffs("ex") + get_diffs("st") + get_diffs("lp") + get_diffs("tn")
                        
                        ws_data.append_row(new_row)
                        st.success(f"✅ 保存完了: {f_w1}-{f_w2}-{f_w3}")
                    except Exception as e:
                        st.error(f"保存失敗: {e}")

# --- Tab 3: 攻略メモ ---
with tab3:
    if ws_memo:
        with st.form("memo"):
            m_p = st.selectbox("会場", PLACES)
            m_t = st.text_area("メモ内容")
            if st.form_submit_button("メモ保存"):
                ws_memo.append_row([m_p, m_t, str(datetime.date.today())])
                st.success("メモを保存しました")
# --- タブ4：管理用入力 ---
with tab4:

    st.subheader("🛠 管理用データ入力")

    ws_master = sh.worksheet("管理用_NEW")
    master_df = pd.DataFrame(ws_master.get_all_records())

    # 全ボートレース場（固定）
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
        place = st.selectbox(
            "会場",
            place_list,
            key="tab4_place"
        )

    with col3:
        race_no = st.number_input(
            "レース番号", 1, 12, 1,
            key="tab4_race"
        )

    st.divider()

    wind_dir = st.radio(
        "風向き（方位）",
        ["北", "北東", "東", "南東", "南", "南西", "西", "北西"],
        horizontal=True,
        key="tab4_wind"
    )

    st.divider()

    # ------------------------
    # 展示データ入力
    # ------------------------
    st.markdown("## 📊 展示データ入力")

    for boat in range(1, 7):

        st.markdown(f"### 🚤 {boat}号艇")

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.number_input(
                "展示",
                step=0.01,
                format="%.2f",
                key=f"tab4_tenji_{boat}"
            )

        with c2:
            st.number_input(
                "直線",
                step=0.01,
                format="%.2f",
                key=f"tab4_choku_{boat}"
            )

        with c3:
            st.number_input(
                "一周",
                step=0.01,
                format="%.2f",
                key=f"tab4_isshu_{boat}"
            )

        with c4:
            st.number_input(
                "回り足",
                step=0.01,
                format="%.2f",
                key=f"tab4_mawari_{boat}"
            )

    st.divider()

    # ------------------------
    # 結果入力
    # ------------------------
    st.markdown("## 🏁 結果入力（スタート・評価・着順）")

    for boat in range(1, 7):

        st.markdown(f"### 🚤 {boat}号艇")

        r1, r2, r3 = st.columns(3)

        with r1:
            st.number_input(
                "スタート（ST）",
                step=0.01,
                format="%.2f",
                key=f"tab4_st_{boat}"
            )

        with r2:
            st.selectbox(
                "スタート評価",
                ["", "◎", "◯", "△", "×"],
                key=f"tab4_eval_{boat}"
            )

        with r3:
            st.number_input(
                "着順",
                1, 6, 1,
                key=f"tab4_rank_{boat}"
            )

    st.divider()

    # ------------------------
    # 登録処理
    # ------------------------
    if st.button("このレースを登録する", key="tab4_save"):

        boats_data = []

        for boat in range(1, 7):

            boats_data.append({
                "日付": str(date),
                "会場": place,
                "レース番号": race_no,
                "風向き": wind_dir,
                "艇番": boat,
                "展示": st.session_state[f"tab4_tenji_{boat}"],
                "直線": st.session_state[f"tab4_choku_{boat}"],
                "一周": st.session_state[f"tab4_isshu_{boat}"],
                "回り足": st.session_state[f"tab4_mawari_{boat}"],
                "ST": st.session_state[f"tab4_st_{boat}"],
                "スタート評価": st.session_state[f"tab4_eval_{boat}"],
                "着順": st.session_state[f"tab4_rank_{boat}"],
            })

        df_add = pd.DataFrame(boats_data)
        df_add["登録日時"] = pd.Timestamp.now()

        ws = sh.worksheet("管理用_NEW")

        ws.append_rows(
            df_add.astype(str).values.tolist()
        )

        st.success("登録しました！")













