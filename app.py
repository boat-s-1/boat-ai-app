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
            st.error("Secretsに認証情報がありません。")
            return None
        credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
        return gspread.authorize(credentials)
    except Exception as e:
        st.error(f"接続エラー: {e}")
        return None

# --- ページ設定 ---
st.set_page_config(page_title="管理者用：競艇分析", page_icon="⚙️", layout="wide")

PLACES = ["大村", "若松", "多摩川", "蒲郡", "戸田", "江戸川", "平和島", "浜名湖", "常滑", "津", "三国", "びわこ", "住之江", "尼崎", "鳴門", "丸亀", "児島", "宮島", "徳山", "下関", "芦屋", "福岡", "唐津", "桐生"]
DIRS = ["向い風", "追い風", "左横風", "右横風", "無風"]

gc = get_gsheet_client()
sh = None
ws_data = None
ws_memo = None

if gc:
    try:
        sh = gc.open("競艇予想学習データ")
        ws_data = sh.get_worksheet(0)
        ws_memo = sh.worksheet("攻略メモ")
    except Exception as e:
        st.warning("シート読み込み失敗。シート名を確認してください。")

st.title("🚤 競艇予想 Pro Cloud (管理者)")

tab1, tab2, tab3 = st.tabs(["🕒 タイム入力", "📊 的中データ登録", "📝 攻略メモ"])

# --- Tab 1: タイム入力 ---
with tab1:
    st.subheader("現在のレース：タイム入力")
    cols = st.columns(3)
    for i in range(1, 7):
        with cols[(i-1) % 3]:
            # ここがエラーの原因だった箇所です。しっかりインデントを入れました。
            with st.expander(f"🚤 {i}号艇 タイム", expanded=True):
                st.number_input("展示タイム", 4.0, 9.0, 6.70, 0.01, key=f"ex_{i}")
                st.number_input("直線タイム", 4.0, 15.0, 7.00, 0.01, key=f"st_{i}")
                st.number_input("1周タイム", 30.0, 60.0, 37.00, 0.01, key=f"lp_{i}")
                st.number_input("回り足タイム", 3.0, 15.0, 5.00, 0.01, key=f"tn_{i}")

# --- Tab 2: 的中データ登録 ---
# --- Tab 2: 的中データ登録 (1-3着対応版) ---
with tab2:
    if ws_data is None:
        st.error("シートが見つかりません。")
    else:
        with st.form("result_form"):
            c1, c2, c3 = st.columns(3)
            f_place = c1.selectbox("会場", PLACES)
            f_race = c2.number_input("レースR", 1, 12, 1)
            
            # 1着・2着・3着を選べるように変更
            res_cols = st.columns(3)
            f_win1 = res_cols[0].selectbox("1着", [1, 2, 3, 4, 5, 6], key="w1")
            f_win2 = res_cols[1].selectbox("2着", [1, 2, 3, 4, 5, 6], key="w2")
            f_win3 = res_cols[2].selectbox("3着", [1, 2, 3, 4, 5, 6], key="w3")
            
            w1, w2, w3 = st.columns(3)
            f_wdir = w1.selectbox("風向き", DIRS)
            f_wspd = w2.number_input("風速 (m)", 0, 15, 0)
            f_wave = w3.number_input("波高 (cm)", 0, 50, 0)

            if st.form_submit_button("3着までまとめて保存"):
                # バリデーション：着順が重複していないか
                if len({f_win1, f_win2, f_win3}) < 3:
                    st.error("着順が重複しています！正しく入力してください。")
                else:
                    try:
                        def get_diffs(prefix):
                            times = [st.session_state[f"{prefix}_{i}"] for i in range(1, 7)]
                            fastest = min(times)
                            return [round(t - fastest, 3) for t in times]

                        d_ex = get_diffs("ex")
                        d_st = get_diffs("st")
                        d_lp = get_diffs("lp")
                        d_tn = get_diffs("tn")

                        # 保存データに 2着, 3着 を追加
                        new_row = [
                            str(datetime.date.today()), f_place, f_race, 
                            f_win1, f_win2, f_win3, # ここを拡張
                            f_wdir, f_wspd, f_wave
                        ] + d_ex + d_st + d_lp + d_tn
                        
                        ws_data.append_row(new_row)
                        st.success(f"✅ {f_win1}-{f_win2}-{f_win3} で保存しました！")
                    except Exception as e:
                        st.error(f"保存失敗: {e}")
# --- Tab 3: 攻略メモ ---
with tab3:
    if ws_memo is not None:
        with st.form("memo_form"):
            m_place = st.selectbox("会場を選択", PLACES)
            m_text = st.text_area("メモを入力", height=100)
            if st.form_submit_button("メモ更新"):
                ws_memo.append_row([m_place, m_text, str(datetime.date.today())])
                st.success("✅ メモを更新しました。")

