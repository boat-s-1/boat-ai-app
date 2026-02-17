import streamlit as st
import pandas as pd
import datetime
import gspread
import numpy as np
from google.oauth2.service_account import Credentials

# 1. 認証設定
def get_gsheet_client():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        if "gcp_service_account" not in st.secrets:
            return None
        credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
        return gspread.authorize(credentials)
    except Exception as e:
        st.error(f"認証エラー: {e}")
        return None

st.set_page_config(page_title="競艇予想 Pro Cloud", layout="wide")
st.title("🚤 競艇予想 Pro Cloud")

# 2. データの読み込み
@st.cache_data(ttl=5) # 登録後すぐに反映させるため5秒に設定
def load_data():
    try:
        gc = get_gsheet_client()
        if gc:
            sh = gc.open("競艇予想学習データ")
            ws = sh.get_worksheet(0)
            return ws.get_all_values(), ws
    except Exception as e:
        return None, None
    return None, None

all_rows, ws_obj = load_data()

if all_rows is None:
    st.error("スプレッドシートにアクセスできません。共有設定またはSecretsを再確認してください。")
else:
    tab1, tab2, tab3 = st.tabs(["⚡ 簡易比較", "📊 詳細補正", "📈 データ登録"])

    # --- ⚡ 簡易比較 ---
    with tab1:
        st.subheader("生タイム比較")
        cols = st.columns(6)
        e_times = [cols[i].number_input(f"{i+1}号艇", 6.0, 7.5, 6.7, 0.01, key=f"e{i}") for i in range(6)]
        fastest = min(e_times)
        st.divider()
        for i, t in enumerate(e_times):
            diff = round(t - fastest, 3)
            st.write(f"{i+1}号艇: {t} (差: :red[+{diff}])")

    # --- 📊 詳細補正 ---
    with tab2:
        st.subheader("場別・機力補正")
        st_place = st.selectbox("競艇場", ["桐生", "戸田", "江戸川", "平和島", "多摩川", "浜名湖", "蒲郡", "常滑", "津", "三国", "びわこ", "住之江", "尼崎", "鳴門", "丸亀", "児島", "宮島", "徳山", "下関", "若松", "芦屋", "福岡", "唐津", "大村"])
        d_cols = st.columns(6)
        d_times = [d_cols[i].number_input(f"{i+1}号艇", 6.0, 7.5, 6.7, 0.01, key=f"d{i}") for i in range(6)]
        
        if st.button("🚀 補正計算", use_container_width=True):
            biases = []
            for row in all_rows[1:]:
                if len(row) >= 9 and row[1] == st_place:
                    try:
                        biases.append([float(row[i]) for i in range(3, 9)])
                    except:
                        continue
            
            if biases:
                avg_bias = np.mean(biases, axis=0)
                st.info(f"{st_place}の過去データ {len(biases)} 件を分析中...")
            else:
                avg_bias = [0.0] * 6
                st.warning(f"{st_place}のデータがまだありません。")
            
            corrected = [round(t - b, 3) for t, b in zip(d_times, avg_bias)]
            best = min(corrected)
            res = pd.DataFrame({"号艇": range(1,7), "補正後": corrected, "評価": ["⭐" if v==best else "" for v in corrected]})
            st.table(res)

    # --- 📈 データ登録 ---
    with tab3:
        st.subheader("学習登録")
        # フォームに名前をつけて管理を厳密にする
        with st.form("my_registration_form", clear_on_submit=True):
            f_p = st.selectbox("場", ["桐生", "戸田", "江戸川", "平和島", "多摩川", "浜名湖", "蒲郡", "常滑", "津", "三国", "びわこ", "住之江", "尼崎", "鳴門", "丸亀", "児島", "宮島", "徳山", "下関", "若松", "芦屋", "福岡", "唐津", "大村"])
            f_r = st.number_input("レース(1-12)", 1, 12, 1)
            f_ds = [st.number_input(f"{i+1}号艇差分", -0.5, 0.5, 0.0, 0.01, key=f"reg_val_{i}") for i in range(6)]
            
            submit = st.form_submit_button("クラウドに保存")
            
            if submit:
                if ws_obj:
                    try:
                        # 書き込み用データの作成
                        new_data = [str(datetime.date.today()), f_p, int(f_r)] + [float(d) for d in f_ds]
                        ws_obj.append_row(new_data)
                        st.success("✅ スプレッドシートへ保存しました！")
                        st.cache_data.clear() # データを最新の状態にする
                    except Exception as e:
                        st.error(f"保存エラー: {e}")
                else:
                    st.error("保存先のシートが見つかりません。")
