import streamlit as st
import pandas as pd
import numpy as np
import datetime
import gspread
from google.oauth2.service_account import Credentials
from streamlit_drawable_canvas import st_canvas

# ---------------------------
# 1. Google Sheets 接続関数
# ---------------------------
def get_gsheet_client():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    info = {
        "type": "service_account",
        "project_id": "premium-nuance-442911-j5",
        "private_key_id": "83f7f3552987683fced748cf5699fb3f6885713d",
        "private_key": """-----BEGIN PRIVATE KEY-----
MIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDTCoRo6jCjXE+B
...（中略：あなたの秘密鍵をそのまま残してください）...
-----END PRIVATE KEY-----""",
        "client_email": "boat-ai-bot@premium-nuance-442911-j5.iam.gserviceaccount.com",
        "client_id": "112206275852095080080",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/boat-ai-bot%40premium-nuance-442911-j5.iam.gserviceaccount.com"
    }
    try:
        credentials = Credentials.from_service_account_info(info, scopes=scopes)
        return gspread.authorize(credentials)
    except:
        return None

# ---------------------------
# 2. ページ設定（エラー防止用）
# ---------------------------
st.set_page_config(page_title="競艇予想 Pro Cloud", layout="wide")

# ブラウザ翻訳によるエラーを防ぐ
st.markdown("<div id='main-app' lang='ja' style='display:none;'></div>", unsafe_allow_html=True)

st.title("🚤 競艇予想 Pro Cloud")

# ---------------------------
# 3. データの同期（キャッシュ利用で軽量化）
# ---------------------------
@st.cache_data(ttl=600)  # 10分間データをキャッシュして負荷軽減
def load_gsheet_data():
    try:
        gc = get_gsheet_client()
        if gc:
            sh = gc.open("競艇予想学習データ")
            worksheet = sh.get_worksheet(0)
            return worksheet.get_all_records(), worksheet
    except:
        return [], None
    return [], None

all_records, ws_object = load_gsheet_data()

# データの加工
place_bias = {}
for row in all_records:
    p = row.get("競艇場")
    if p:
        if p not in place_bias: place_bias[p] = []
        for i in range(1, 7):
            val = row.get(f"{i}号艇差分", 0)
            try: v = float(val) if val not in ["", None] else 0.0
            except: v = 0.0
            place_bias[p].append(v)

# ---------------------------
# 4. タブ切り替え（安定性重視）
# ---------------------------
tab1, tab2, tab3, tab4 = st.tabs(["⚡ 簡易比較", "📊 詳細補正", "✏️ 展開予想", "📈 データ追加"])

# --- ⚡ 簡易比較 ---
with tab1:
    st.subheader("生タイム比較")
    e_cols = st.columns(6)
    e_times = [e_cols[i].number_input(f"{i+1}号艇", 6.0, 7.5, 6.7, 0.01, key=f"e{i}") for i in range(6)]
    fastest = min(e_times)
    st.write("---")
    for i, t in enumerate(e_times):
        diff = round(t - fastest, 3)
        st.write(f"{i+1}号艇: **{t}** (差: :red[+{diff}])")

# --- 📊 詳細補正 ---
with tab2:
    st.subheader("場別平均・補正計算")
    st_place = st.selectbox("競艇場", ["桐生", "戸田", "江戸川", "平和島", "多摩川", "浜名湖", "蒲郡", "常滑", "津", "三国", "びわこ", "住之江", "尼崎", "鳴門", "丸亀", "児島", "宮島", "徳山", "下関", "若松", "芦屋", "福岡", "唐津", "大村"])
    d_cols = st.columns(6)
    d_times = [d_cols[i].number_input(f"{i+1}号艇", 6.0, 7.5, 6.7, 0.01, key=f"d{i}") for i in range(6)]
    
    if st.button("🚀 補正計算", use_container_width=True):
        bias = place_bias.get(st_place, [0.0]*6)
        corrected = [round(t - b, 3) for t, b in zip(d_times, bias)]
        best = min(corrected)
        res = pd.DataFrame({"号艇": range(1,7), "補正後": corrected, "評価": ["⭐" if v==best else "" for v in corrected]})
        st.table(res)

# --- ✏️ 展開予想（軽量版） ---
with tab3:
    st.subheader("1マーク展開メモ")
    st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=3,
        stroke_color="#000",
        background_color="#eee", # 少し色をつけてキャンバスを認識しやすく
        height=300, # 高さを少し抑えて安定させる
        drawing_mode="freedraw",
        key="canvas_main",
    )
    st.caption("※描けない場合はページを再読み込みしてください")

# --- 📈 データ追加 ---
with tab4:
    st.subheader("クラウドへ学習登録")
    with st.form("add_form"):
        f_p = st.selectbox("競艇場", ["桐生", "戸田", "江戸川", "平和島", "多摩川", "浜名湖", "蒲郡", "常滑", "津", "三国", "びわこ", "住之江", "尼崎", "鳴門", "丸亀", "児島", "宮島", "徳山", "下関", "若松", "芦屋", "福岡", "唐津", "大村"])
        f_ds = [st.number_input(f"{i+1}号艇差分", -0.5, 0.5, 0.0, 0.01, key=f"f{i}") for i in range(6)]
        if st.form_submit_button("💾 保存", use_container_width=True):
            if ws_object:
                ws_object.append_row([str(datetime.date.today()), f_p] + f_ds)
                st.success("保存しました！")
                st.cache_data.clear() # キャッシュを消して最新にする
