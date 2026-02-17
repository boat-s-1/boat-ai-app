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
    except:
        return None

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

# 評価の点数変換
score_map = {"⭐": 5, "◎": 4, "◯": 3, "▪️": 2, "△": 1, "✖️": 0}

if all_rows is None:
    st.error("⚠️ スプレッドシートにアクセスできません。")
else:
    tab1, tab2, tab3 = st.tabs(["📊 総合評価カード", "🕒 詳細補正計算", "📈 学習データ登録"])

    # --- 📊 総合評価カード（新機能） ---
    with tab1:
        st.subheader("項目別評価入力")
        items = ["モーター", "当地勝率", "スタート", "展示"]
        
        # 入力エリア
        input_data = []
        for i in range(6):
            st.markdown(f"**{i+1}号艇**")
            cols = st.columns(4)
            row_scores = []
            for j, item in enumerate(items):
                val = cols[j].selectbox(f"{item}", ["⭐", "◎", "◯", "▪️", "△", "✖️"], index=2, key=f"eval_{i}_{j}")
                row_scores.append(score_map[val])
            input_data.append(sum(row_scores))
        
        st.divider()
        
        # 計算と順位表示
        max_possible = len(items) * 5 # 全項目⭐の場合
        percentages = [round((s / max_possible) * 100, 1) for s in input_data]
        
        st.subheader("🏆 予想期待度順位")
        res_cols = st.columns(6)
        
        # 期待度順に並び替え
        ranked_indices = np.argsort(percentages)[::-1]
        
        for rank, idx in enumerate(ranked_indices):
            with res_cols[rank]:
                color = "inverse" if rank == 0 else "off"
                st.metric(label=f"{rank+1}位: {idx+1}号艇", value=f"{percentages[idx]}%", delta=f"計 {input_data[idx]}点")
                if rank == 0: st.write("👑 本命 candidate")

    # --- 🕒 詳細補正計算 ---
    with tab2:
        st.subheader("場別・機力補正（過去ログ使用）")
        st_place = st.selectbox("競艇場", ["桐生", "戸田", "江戸川", "平和島", "多摩川", "浜名湖", "蒲郡", "常滑", "津", "三国", "びわこ", "住之江", "尼崎", "鳴門", "丸亀", "児島", "宮島", "徳山", "下関", "若松", "芦屋", "福岡", "唐津", "大村"])
        d_cols = st.columns(6)
        d_times = [d_cols[i].number_input(f"{i+1}号艇タイム", 6.0, 7.5, 6.7, 0.01, key=f"d{i}") for i in range(6)]
        
        if st.button("🚀 補正計算実行", use_container_width=True):
            biases = []
            for row in all_rows[1:]:
                if len(row) >= 9 and row[1] == st_place:
                    try: biases.append([float(row[i]) for i in range(3, 9)])
                    except: continue
            
            if biases:
                avg_bias = np.mean(biases, axis=0)
                corrected = [round(t - b, 3) for t, b in zip(d_times, avg_bias)]
                best = min(corrected)
                st.table(pd.DataFrame({"号艇": [f"{i}号艇" for i in range(1,7)], "補正後": corrected, "評価": ["⭐" if v==best else "" for v in corrected]}))
            else:
                st.warning("データ不足です。")

    # --- 📈 学習データ登録 ---
    with tab3:
        st.subheader("クラウド同期登録")
        with st.form("reg_form", clear_on_submit=True):
            f_p = st.selectbox("開催場", ["桐生", "戸田", "江戸川", "平和島", "多摩川", "浜名湖", "蒲郡", "常滑", "津", "三国", "びわこ", "住之江", "尼崎", "鳴門", "丸亀", "児島", "宮島", "徳山", "下関", "若松", "芦屋", "福岡", "唐津", "大村"])
            f_r = st.number_input("R", 1, 12, 1)
            f_ds = [st.number_input(f"{i+1}差分", -0.5, 0.5, 0.0, 0.01) for i in range(6)]
            if st.form_submit_button("スプレッドシートへ保存"):
                new_row = [str(datetime.date.today()), f_p, int(f_r)] + [float(d) for d in f_ds]
                ws_obj.append_rows([new_row])
                st.success("保存完了！")
                st.cache_data.clear()
