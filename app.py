import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# 認証設定（Streamlit CloudのSecretsから読み込む）
def get_gsheet_client():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    # 秘密情報を直接書かず、Secrets設定から取得する
    credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
    return gspread.authorize(credentials)

st.title("🚤 競艇予想 Pro (安定版)")

try:
    gc = get_gsheet_client()
    st.success("✅ クラウド接続に成功しました！")
    
    # 簡易比較機能
    times = [st.number_input(f"{i+1}号艇", 6.0, 7.5, 6.7, 0.01, key=f"t{i}") for i in range(6)]
    if st.button("比較する"):
        fastest = min(times)
        for i, t in enumerate(times):
            st.write(f"{i+1}号艇: {t} (差: {round(t-fastest, 3)})")

except Exception as e:
    st.error("設定待ちです。右下の Manage app > Settings から秘密鍵を設定してください。")
