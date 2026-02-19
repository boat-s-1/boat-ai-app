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
# --- タブ：管理用データ入力 ---
with tab4:
    st.subheader("管理用データ登録")

    # =========================
    # 基本情報
    # =========================
    c_meta1, c_meta2, c_meta3 = st.columns(3)
    with c_meta1:
        race_date = st.date_input("レース日付")
    with c_meta2:
        place = st.selectbox("会場", ["蒲郡","常滑","浜名湖","住之江","大村","徳山","唐津"])
    with c_meta3:
        race_no = st.number_input("レース番号", 1, 12, 1)

    c_meta4, c_meta5, c_meta6 = st.columns(3)
    with c_meta4:
        wind_dir = st.selectbox("風向き", ["追い風","向かい風","左横風","右横風","無風"])
    with c_meta5:
        wind_speed = st.number_input("風速（m）", 0, 20, 0)
    with c_meta6:
        wave = st.number_input("波高（cm）", 0, 50, 0)

    st.markdown("---")
    
    # データ保持用辞書
    boat_data = {}
    eval_list = ["◎","◯","△","×",""]

    # =========================
    # 1. 展示・足まわりデータ入力
    # =========================
    st.markdown("### 🚤 展示・足まわり")
    for b in range(1, 7):
        with st.expander(f"{b}号艇 - 展示データ", expanded=True):
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                ex = st.number_input("展示", 0.0, 10.0, 6.50, 0.01, key=f"ex_{b}")
            with c2:
                stt = st.number_input("直線", 0.0, 10.0, 5.00, 0.01, key=f"st_{b}")
            with c3:
                lap = st.number_input("一周", 0.0, 80.0, 37.0, 0.01, key=f"lp_{b}")
            with c4:
                turn = st.number_input("回り足", 0.0, 10.0, 5.0, 0.1, key=f"tr_{b}")
            
            # 辞書に一時保存
            boat_data[b] = {
                "展示": ex, "直線": stt, "一周": lap, "回り足": turn
            }

    st.markdown("---")

    # =========================
    # 2. レース結果入力（別枠）
    # =========================
    st.markdown("### 🏁 レース結果 (ST・評価・着順)")
    
    # 見出し行
    h1, h2, h3, h4 = st.columns([1, 2, 2, 2])
    h1.write("**艇番**")
    h2.write("**ST**")
    h3.write("**スタート評価**")
    h4.write("**着順**")

    for b in range(1, 7):
        c1, c2, c3, c4 = st.columns([1, 2, 2, 2])
        with c1:
            st.markdown(f"**{b}**")
        with c2:
            st_time = st.number_input("ST", -0.50, 1.00, 0.10, 0.01, key=f"res_stt_{b}", label_visibility="collapsed")
        with c3:
            start_eval = st.selectbox("評価", eval_list, key=f"res_eval_{b}", label_visibility="collapsed")
        with c4:
            rank = st.number_input("着順", 1, 6, b, key=f"res_rank_{b}", label_visibility="collapsed")
        
        # 既存の辞書に結合
        boat_data[b].update({
            "ST": st_time,
            "スタート評価": start_eval,
            "着順": rank
        })

    # =========================
    # データのパッキング
    # =========================
    rows = []
    now_ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for b in range(1, 7):
        row = {
            "日付": race_date.strftime("%Y-%m-%d"),
            "登録日時": now_ts,
            "会場": place,
            "レース番号": race_no,
            "艇番": b,
            "展示": boat_data[b]["展示"],
            "直線": boat_data[b]["直線"],
            "一周": boat_data[b]["一周"],
            "回り足": boat_data[b]["回り足"],
            "ST": boat_data[b]["ST"],
            "風向き": wind_dir,
            "風速": wind_speed,
            "波高": wave,
            "着順": boat_data[b]["着順"],
            "スタート評価": boat_data[b]["スタート評価"]
        }
        rows.append(row)

    # =========================
    # 保存実行
    # =========================
    st.markdown("---")
    if st.button("このレースを登録する", key="final_save_button"):
        try:
            ws = sh.worksheet("管理用_NEW")
            df_add = pd.DataFrame(rows)
            
            # スプレッドシートへ追加
            ws.append_rows(
                df_add.values.tolist(),
                value_input_option="USER_ENTERED"
            )
            st.success("スプレッドシートに登録しました！")
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")












