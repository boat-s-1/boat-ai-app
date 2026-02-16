import streamlit as st
import pandas as pd
import datetime
import gspread
from google.oauth2.service_account import Credentials

# 1. 認証設定
def get_gsheet_client():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
        return gspread.authorize(credentials)
    except:
        return None

st.set_page_config(page_title="競艇予想 Pro Cloud", layout="wide")
st.title("🚤 競艇予想 Pro Cloud")

# データの読み込み
@st.cache_data(ttl=60) # テストのためキャッシュを1分に短縮
def load_data():
    try:
        gc = get_gsheet_client()
        if gc:
            sh = gc.open("競艇予想学習データ")
            ws = sh.get_worksheet(0)
            # get_all_values() を使い、列の番号で制御する
            return ws.get_all_values(), ws
    except Exception as e:
        return None, None
    return None, None

all_rows, ws_obj = load_data()

if all_rows is None:
    st.error("スプレッドシートにアクセスできません。共有設定を確認してください。")
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
            st.write(f"{i+1}号艇: {t} (差: +{round(t-fastest, 3)})")

    # --- 📊 詳細補正 ---
    with tab2:
        st.subheader("場別・機力補正")
        st_place = st.selectbox("競艇場", ["桐生", "戸田", "江戸川", "平和島", "多摩川", "浜名湖", "蒲郡", "常滑", "津", "三国", "びわこ", "住之江", "尼崎", "鳴門", "丸亀", "児島", "宮島", "徳山", "下関", "若松", "芦屋", "福岡", "唐津", "大村"])
        d_cols = st.columns(6)
        d_times = [d_cols[i].number_input(f"{i+1}号艇", 6.0, 7.5, 6.7, 0.01, key=f"d{i}") for i in range(6)]
        
        if st.button("🚀 補正計算", use_container_width=True):
            # データの解析（2行目以降をループ）
            biases = []
            for row in all_rows[1:]:
                # row[1]が競艇場、row[3]以降が各艇の差分と仮定
                if len(row) >= 9 and row[1] == st_place:
                    try:
                        biases.append([float(row[i]) for i in range(3, 9)])
                    except:
                        continue
            
            # 平均を計算
            if biases:
                avg_bias = np.mean(biases, axis=0)
                st.info(f"{st_place}の過去データ {len(biases)} 件から計算中...")
            else:
                avg_bias = [0.0] * 6
                st.warning("この場のデータがまだありません。0で計算します。")
            
            corrected = [round(t - b, 3) for t, b in zip(d_times, avg_bias)]
            best = min(corrected)
            res = pd.DataFrame({"号艇": range(1,7), "補正後": corrected, "評価": ["⭐" if v==best else "" for v in corrected]})
            st.table(res)

    # --- 📈 データ登録 ---
    with tab3:
        st.subheader("学習登録")
        with st.form("reg"):
            f_p = st.selectbox("場", ["桐生", "戸田", "江戸川", "平和島", "多摩川", "浜名湖", "蒲郡", "常滑", "津", "三国", "びわこ", "住之江", "尼崎", "鳴門", "丸亀", "児島", "宮島", "徳山", "下関", "若松", "芦屋", "福岡", "唐津", "大村"])
            f_r = st.number_input("レース(1-12)", 1, 12, 1)
            f_ds = [st.number_input(f"{i+1}差分", -0.5, 0.5, 0.0, 0.01) for i in range(6)]
            if st.form_submit_button("保存"):
                ws_obj.append_row([str(datetime.date.today()), f_p, f_r] + f_ds)
                st.success("保存しました！")
                st.cache_data.clear()
