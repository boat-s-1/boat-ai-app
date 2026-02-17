import streamlit as st
import pandas as pd
import datetime
import gspread
import numpy as np
from google.oauth2.service_account import Credentials

# 1. 認証設定（最新の安定した方式）
def get_gsheet_client():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        if "gcp_service_account" not in st.secrets:
            return None
        credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
        return gspread.authorize(credentials)
    except:
        return None

# 画面設定
st.set_page_config(page_title="競艇予想 Pro Cloud", page_icon="🚤", layout="wide")
st.title("🚤 競艇予想 Pro Cloud")

# 2. データの読み込み
@st.cache_data(ttl=5)
def load_data():
    try:
        gc = get_gsheet_client()
        if gc:
            sh = gc.open("競艇予想学習データ")
            ws = sh.get_worksheet(0)
            return ws.get_all_values(), ws
    except:
        return None, None
    return None, None

all_rows, ws_obj = load_data()

# 接続チェック
if all_rows is None:
    st.error("⚠️ スプレッドシートにアクセスできません。共有設定を確認してください。")
else:
    # --- タブ構成 ---
    tab1, tab2, tab3 = st.tabs(["⚡ 簡易比較", "📊 詳細補正", "📈 データ登録"])

    # --- ⚡ 簡易比較（生タイムの計算） ---
    with tab1:
        st.subheader("生タイム比較")
        cols = st.columns(6)
        e_times = [cols[i].number_input(f"{i+1}号艇", 6.0, 7.5, 6.7, 0.01, key=f"e{i}") for i in range(6)]
        
        fastest = min(e_times)
        st.divider()
        
        res_cols = st.columns(6)
        for i, t in enumerate(e_times):
            diff = round(t - fastest, 3)
            with res_cols[i]:
                if diff == 0:
                    st.success(f"**{i+1}号艇**\n\n{t}\n\n最速!")
                else:
                    st.info(f"**{i+1}号艇**\n\n{t}\n\n+{diff}")

    # --- 📊 詳細補正（過去データからの計算） ---
    with tab2:
        st.subheader("場別・機力補正")
        st_place = st.selectbox("対象の競艇場を選択", ["桐生", "戸田", "江戸川", "平和島", "多摩川", "浜名湖", "蒲郡", "常滑", "津", "三国", "びわこ", "住之江", "尼崎", "鳴門", "丸亀", "児島", "宮島", "徳山", "下関", "若松", "芦屋", "福岡", "唐津", "大村"])
        
        d_cols = st.columns(6)
        d_times = [d_cols[i].number_input(f"{i+1}号艇", 6.0, 7.5, 6.7, 0.01, key=f"d{i}") for i in range(6)]
        
        if st.button("🚀 過去の傾向から補正計算", use_container_width=True):
            biases = []
            # 2行目以降のデータを走査
            for row in all_rows[1:]:
                if len(row) >= 9 and row[1] == st_place:
                    try:
                        biases.append([float(row[i]) for i in range(3, 9)])
                    except:
                        continue
            
            if biases:
                avg_bias = np.mean(biases, axis=0)
                st.info(f"💡 {st_place}の過去データ {len(biases)} 件を分析しました。")
                
                corrected = [round(t - b, 3) for t, b in zip(d_times, avg_bias)]
                best = min(corrected)
                
                # 結果表示
                res_df = pd.DataFrame({
                    "号艇": [f"{i}号艇" for i in range(1, 7)],
                    "補正後タイム": corrected,
                    "評価": ["⭐ 最速" if v == best else "" for v in corrected]
                })
                st.table(res_df)
            else:
                st.warning(f"現在、{st_place}の学習データが登録されていません。「データ登録」から保存してください。")

    # --- 📈 データ登録（クラウド保存） ---
    with tab3:
        st.subheader("本日のデータを学習させる")
        with st.form("input_form", clear_on_submit=True):
            f_cols = st.columns([2, 1])
            with f_cols[0]:
                f_p = st.selectbox("開催場", ["桐生", "戸田", "江戸川", "平和島", "多摩川", "浜名湖", "蒲郡", "常滑", "津", "三国", "びわこ", "住之江", "尼崎", "鳴門", "丸亀", "児島", "宮島", "徳山", "下関", "若松", "芦屋", "福岡", "唐津", "大村"])
            with f_cols[1]:
                f_r = st.number_input("レース(R)", 1, 12, 1)
            
            st.write("各艇の「展示タイム - 平均展示」などの差分を入力")
            d_inputs = st.columns(6)
            f_ds = [d_inputs[i].number_input(f"{i+1}差", -0.5, 0.5, 0.0, 0.01, key=f"reg_{i}") for i in range(6)]
            
            submitted = st.form_submit_button("クラウド上のスプレッドシートへ保存", use_container_width=True)
            
            if submitted:
                try:
                    new_row = [str(datetime.date.today()), f_p, int(f_r)] + [float(d) for d in f_ds]
                    ws_obj.append_rows([new_row])
                    st.success("✅ 保存が完了しました！「詳細補正」タブに反映されます。")
                    st.cache_data.clear() # キャッシュクリアして即時反映
                except Exception as e:
                    st.error(f"保存に失敗しました。再試行してください。")
