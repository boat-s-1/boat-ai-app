import streamlit as st
import pandas as pd
import os
import gspread
from google.oauth2.service_account import Credentials

# ==============================
# 1. 基本設定
# ==============================
# public_app.py から遷移してきた際の会場名を取得（デフォルトは戸田）
PLACE_NAME = st.session_state.get("selected_place", "戸田")
SPREADSHEET_KEY = "1lN794iGtyGV2jNwlYzUA8wEbhRwhPM7FxDAkMaoJss4"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(page_title=f"競艇Pro {PLACE_NAME}", layout="wide")

# ==============================
# 2. 認証 & データ取得関数
# ==============================
def get_gsheet_client():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
        return gspread.authorize(credentials)
    except Exception as e:
        st.error(f"認証エラー: {e}")
        return None

# ==============================
# 3. メインUI
# ==============================
st.title(f"🏁 {PLACE_NAME} 解析システム")

# 会場選択へ戻るボタン
if st.sidebar.button("← 会場選択へ戻る"):
    st.switch_page("public_app.py")

# --- レース種別の選択 ---
st.subheader("📋 解析設定")
col_opt1, col_opt2 = st.columns(2)
with col_opt1:
    race_type = st.radio("レース種別を選択", ["混合", "女子"], horizontal=True)

# --- データ読み込み ---
sheet_name = f"{PLACE_NAME}_{race_type}統計"
st.info(f"現在の対象シート: {sheet_name}")

if st.button(f"{sheet_name} データを読み込む"):
    gc = get_gsheet_client()
    if gc:
        try:
            sh = gc.open_by_key(SPREADSHEET_KEY)
            ws = sh.worksheet(sheet_name)
            data = ws.get_all_records()
            
            if data:
                df = pd.DataFrame(data)
                # 数値型に変換（列名が共通なのが強み！）
                num_cols = ["展示", "直線", "回り足", "一周", "ST", "レース番号", "艇番"]
                for c in num_cols:
                    if c in df.columns:
                        df[c] = pd.to_numeric(df[c], errors="coerce")
                
                st.session_state["current_df"] = df
                st.success(f"{len(df)} 件のデータを読み込みました")
            else:
                st.warning("データが空です")
        except Exception as e:
            st.error(f"シート '{sheet_name}' の読み込みに失敗しました。シート名を確認してください。\nエラー: {e}")

# ==============================
# 4. 解析・予想機能（データがある場合のみ表示）
# ==============================
if "current_df" in st.session_state:
    df = st.session_state["current_df"]
    
    # タブを最小限に絞る
    tab1, tab2, tab3 = st.tabs(["📊 統計解析", "🚀 スタート予想", "📝 当日データ入力"])

    with tab1:
        st.subheader(f"{race_type}戦 統計データ一覧")
        st.dataframe(df.head(20), use_container_width=True)
        
        # 平均値の表示など
        st.markdown("#### 艇番別 平均展示タイム")
        mean_df = df.groupby("艇番")[["展示", "直線", "回り足", "一周"]].mean()
        st.table(mean_df.style.format("{:.2f}"))

    with tab2:
        st.subheader("🚀 指数計算 & スリット予想")
        # ここにスリット表示ロジックを入れる
        # ... (前回のコードを流用)

    with tab3:
        st.subheader("📝 当日タイム入力")
        # ここに入力フォームを入れる
