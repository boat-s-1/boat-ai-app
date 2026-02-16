import streamlit as st
import pandas as pd
import datetime
import gspread
from google.oauth2.service_account import Credentials

# ---------------------------
# 1. 認証設定 (Secretsから読み込み)
# ---------------------------
def get_gsheet_client():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        # Manage app > Settings > Secrets に設定した情報を読み込む
        credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
        return gspread.authorize(credentials)
    except:
        return None

# ---------------------------
# 2. ページ設定
# ---------------------------
st.set_page_config(page_title="競艇予想 Pro Cloud", layout="wide")
st.title("🚤 競艇予想 Pro Cloud")

# データのキャッシュ（読み込みを高速化）
@st.cache_data(ttl=600)
def load_data():
    try:
        gc = get_gsheet_client()
        if gc:
            sh = gc.open("競艇予想学習データ")
            ws = sh.get_worksheet(0)
            return ws.get_all_records(), ws
    except:
        return [], None
    return [], None

all_records, ws_obj = load_data()

# ---------------------------
# 3. メイン機能（タブ切り替え）
# ---------------------------
tab1, tab2, tab3 = st.tabs(["⚡ 簡易タイム比較", "📊 場別・補正計算", "📈 学習データ登録"])

# --- ⚡ 簡易タイム比較 ---
with tab1:
    st.subheader("展示タイム比較")
    cols = st.columns(6)
    e_times = [cols[i].number_input(f"{i+1}号艇", 6.0, 7.5, 6.7, 0.01, key=f"easy_{i}") for i in range(6)]
    fastest = min(e_times)
    st.divider()
    for i, t in enumerate(e_times):
        diff = round(t - fastest, 3)
        st.write(f"{i+1}号艇: **{t}** (トップ差: :red[+{diff}])")

# --- 📊 場別・補正計算 ---
with tab2:
    st.subheader("平均差分を考慮した機力評価")
    st_place = st.selectbox("競艇場", ["桐生", "戸田", "江戸川", "平和島", "多摩川", "浜名湖", "蒲郡", "常滑", "津", "三国", "びわこ", "住之江", "尼崎", "鳴門", "丸亀", "児島", "宮島", "徳山", "下関", "若松", "芦屋", "福岡", "唐津", "大村"])
    d_cols = st.columns(6)
    d_times = [d_cols[i].number_input(f"{i+1}号艇", 6.0, 7.5, 6.7, 0.01, key=f"det_{i}") for i in range(6)]
    
    if st.button("🚀 補正計算を実行", use_container_width=True):
        # データの整理（場ごとの平均を算出）
        bias_dict = {}
        for row in all_records:
            p = row.get("競艇場")
            if p:
                if p not in bias_dict: bias_dict[p] = []
                bias_dict[p] = [float(row.get(f"{j}号艇差分", 0)) for j in range(1, 7)]
        
        bias = bias_dict.get(st_place, [0.0]*6)
        corrected = [round(t - b, 3) for t, b in zip(d_times, bias)]
        best = min(corrected)
        
        res_df = pd.DataFrame({
            "号艇": [f"{i}号艇" for i in range(1, 7)],
            "補正後タイム": corrected,
            "評価": ["⭐" if v == best else "" for v in corrected]
        })
        st.table(res_df)
        st.info("補正後タイムが小さいほど、その場の平均より良いタイムです。")

# --- 📈 学習データ登録 ---
with tab3:
    st.subheader("今日のレース結果を学習")
    with st.form("study_form"):
        f_p = st.selectbox("競艇場", ["桐生", "戸田", "江戸川", "平和島", "多摩川", "浜名湖", "蒲郡", "常滑", "津", "三国", "びわこ", "住之江", "尼崎", "鳴門", "丸亀", "児島", "宮島", "徳山", "下関", "若松", "芦屋", "福岡", "唐津", "大村"], key="form_p")
        f_ds = [st.number_input(f"{i+1}号艇差分", -0.5, 0.5, 0.0, 0.01, key=f"form_d_{i}") for i in range(6)]
        if st.form_submit_button("💾 クラウドに保存", use_container_width=True):
            if ws_obj:
                try:
                    ws_obj.append_row([str(datetime.date.today()), f_p] + f_ds)
                    st.success("スプレッドシートへの保存に成功しました！")
                    st.cache_data.clear() # キャッシュを消して即反映
                except:
                    st.error("保存に失敗しました。")
            else:
                st.error("スプレッドシートにアクセスできません。")
