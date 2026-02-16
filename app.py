import streamlit as st
import pandas as pd
import numpy as np
import datetime
import gspread
from google.oauth2.service_account import Credentials
from streamlit_drawable_canvas import st_canvas
from PIL import Image

# ---------------------------
# 1. Google Sheets 接続関数
# ---------------------------
def get_gsheet_client():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    # 認証情報を直接指定
    info = {
        "type": "service_account",
        "project_id": "premium-nuance-442911-j5",
        "private_key_id": "83f7f3552987683fced748cf5699fb3f6885713d",
        "private_key": """-----BEGIN PRIVATE KEY-----
MIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDTCoRo6jCjXE+B
hqn+mCSa7/GQA0YO3deGRfCNhgycSerfdSt/bg3H1cEV8l7ungwyYPAQ8pCNQOWz
hjM51c1A42Zx79pCuP3I8DbDAWhHkqGaCgG+TxUo+0F+2gOSHUUJgbrR+iZE+K+o
7QI493xAS2bPTXPUYPm/xFq7W9XLLDP8zUpzgeMfuv7/sKrqCwTAzKVESeXdm5SJ
6KelA0sOds1nko4nt12x4iAyMOpis9gAnQdovbZQVD48WdNIOvgjIHZTv7DQoQmu
85eR5tMliGXLCbwyUUsYo1VqDl57nNs/l7qc5ZLKUWCKdfzRPkVh4+t7HBCXscL4
rPX506dXAgMBAAECggEAS/c4s2U9TchwLBEzxtuwLX9aZjrvcHGFX6V0UhUjG+z1
mSsdlbihSEIWx1Yfuuf0Pvwq3gbaZqYqKOWRMevWftl8Kl4qpCLf44EoTSiIB19u
QTsB5qWj2cUbjdRfPazAiYwDmgrf1Krp3DY4OxZGyQP7RXq9S4D+1XsSJ+gGPKQM
x8mKXNR1ZR7GcPSanc8oFTQS23Y+IJRzhK3qj74j/o88BrYfFAUvbtxxJBiuXZ0m
r3Qgt6BYE2Ks41i3mXeh9lTcdPCOIx9KhXaI9vzBkmYdWEkf4WUkDCo5elpm9KLj
lVfbVbwItx5jd9Pe68CviLnc889skNv/zrZsf/BSmQKBgQDvZ1FlRwTpHvieYSB+
1b1m5Zwj+iZhRImTV630l/xYk6tBrqb9+whpFDnxx7sOqKLgLKGaJUsEwOm0tBCz
1W5kKbCHYxmANl6syRXJcSwT3mj/Er+X/2EKwR4Hd7h5Al9UaWQs0NLDkWern/zL
hDSTGx+wsjqMxoEZ+n8TmCEaiQKBgQDhq9n9YVPiOcttW1+kXKTYQyMtp3ll+dte
vjJlKQGh9PqPdh1esxSWvHd2Rrdl+G/dMlBMDdsJgaBOGL/abyqrZ2JqDmCsFsji
z+bXEcuDOkF789sJ4hIIoBK1KFG51oY546tNRtHk9ljAo5Mi+EG/lk+/5vPiCly6
QuKTZIa63wKBgQDNddk4VyQSwj7TBj5yPBPp3EMN6WDI954uswAbO9kZV9qRa0fs
D2afb/lu1GBoazgltogWl8zzTnEEYck33YN5OQJEnztCeubz2Tv2f0c54hYwWzHN
TCJHrYeNFyVdzThtZGnRwIIxz3eupoa5T0QjwBKJfdyb9rzTw9UNxvEaKQKBgQCP
uY51JGZzPxHDTR2FpYdLQL8H1ZColM/U8FdSPCKRDmABvF0KMg2bzt5aksE9DVPZ
UbD4Lx7gWBFLi9GsgX5wecChARUqpLw+T+CZ+vhdVF3eXrmS+ss3eRNREyOxsuH7
vnccGU2WgBqYXdVYwTnGlimmc6XBwY27BtwcuTphiwKBgQCUmFF6DOxnwYnWSqOD
yh80TFTbXvEabnUTorrsMRiVoLj6d92r8EJyKSPzWTiXxyF06aYdLyJYa8cFrWiy
7XOLiZfPNvvolngaQMIW9HpGgaiP0Ead3giQDyDbYrHE/GneRWh1Em5RF42yKQ8Z
Ss/9proJq3zi3LYUPvO8S9JdJw==
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
    except Exception:
        return None

# ---------------------------
# 2. ページ設定と同期処理
# ---------------------------
st.set_page_config(page_title="競艇予想 Pro Cloud", layout="wide")
st.title("🚤 競艇予想 Pro Cloud")

if "place_bias" not in st.session_state:
    st.session_state.place_bias = {}

try:
    gc = get_gsheet_client()
    if gc:
        sh = gc.open("競艇予想学習データ")
        worksheet = sh.get_worksheet(0)
        all_data = worksheet.get_all_records()
        temp_bias = {}
        for row in all_data:
            p = row.get("競艇場")
            if p:
                if p not in temp_bias: temp_bias[p] = []
                for i in range(1, 7):
                    val = row.get(f"{i}号艇差分", 0)
                    try: float_val = float(val) if val not in ["", None] else 0.0
                    except: float_val = 0.0
                    temp_bias[p].append(float_val)
        st.session_state.place_bias = temp_bias
        st.sidebar.success("✅ クラウド同期完了")
except Exception:
    st.sidebar.warning("⚠️ 同期エラー（閲覧のみ可能）")

# ---------------------------
# 3. タブ切り替え
# ---------------------------
tab_easy, tab_detail, tab_drag, tab_study = st.tabs(["⚡ 簡易", "📊 詳細補正", "✏️ 展開予想", "📈 データ登録"])

# --- ⚡ 簡易版 ---
with tab_easy:
    st.header("簡易タイム比較")
    easy_cols = st.columns(6)
    easy_times = []
    for i in range(6):
        with easy_cols[i]:
            t = st.number_input(f"{i+1}号艇", 6.00, 7.50, 6.70, step=0.01, key=f"easy_{i}")
            easy_times.append(t)
    
    fastest = min(easy_times)
    st.divider()
    for i, t in enumerate(easy_times):
        diff = round(t - fastest, 3)
        st.write(f"{i+1}号艇: **{t}** (トップ差: :red[+{diff}])")

# --- 📊 詳細補正版 ---
with tab_detail:
    st.header("場別平均・展示補正計算")
    col_p, col_r = st.columns(2)
    with col_p:
        st_place = st.selectbox("競艇場", ["桐生", "戸田", "江戸川", "平和島", "多摩川", "浜名湖", "蒲郡", "常滑", "津", "三国", "びわこ", "住之江", "尼崎", "鳴門", "丸亀", "児島", "宮島", "徳山", "下関", "若松", "芦屋", "福岡", "唐津", "大村"])
    with col_r:
        st_race_no = st.number_input("レース番号", 1, 12, 1, key="det_race")

    input_times = []
    cols = st.columns(6)
    for i in range(6):
        with cols[i]:
            t = st.number_input(f"{i+1}号艇", 6.00, 7.50, 6.70, step=0.01, key=f"detail_{i}")
            input_times.append(t)

    if st.button("🚀 補正計算実行", use_container_width=True):
        bias = st.session_state.place_bias.get(st_place, [0.0]*6)
        corrected = [round(t - b, 3) for t, b in zip(input_times, bias)]
        best_val = min(corrected)
        
        res_df = pd.DataFrame({
            "号艇": [f"{i}号艇" for i in range(1, 7)],
            "生タイム": input_times,
            "場別平均": bias,
            "補正後": corrected,
            "評価": ["⭐" if v == best_val else "" for v in corrected]
        })
        st.table(res_df)
        st.info("補正後タイムが小さいほど、その場の平均より優秀なタイム（足が良い）と判断されます。")

# --- ✏️ 展開予想 (ドラッグ) ---
with tab_drag:
    st.header("スリット・展開予想")
    st.write("マウスや指で1マークの攻防を描いてみましょう！")
    
    # 描画ツールの設定
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",  # 固定
        stroke_width=3,
        stroke_color="#000",
        background_color="#fff",
        height=400,
        width=600,
        drawing_mode="freedraw",
        key="canvas",
    )
    if st.button("リセット"):
        st.rerun()

# --- 📈 データ登録 ---
with tab_study:
    st.header("学習データの追加")
    with st.form("data_form"):
        f_place = st.selectbox("競艇場", ["桐生", "戸田", "江戸川", "平和島", "多摩川", "浜名湖", "蒲郡", "常滑", "津", "三国", "びわこ", "住之江", "尼崎", "鳴門", "丸亀", "児島", "宮島", "徳山", "下関", "若松", "芦屋", "福岡", "唐津", "大村"], key="form_p")
        f_diffs = []
        f_cols = st.columns(6)
        for i in range(6):
            with f_cols[i]:
                d = st.number_input(f"{i+1}号艇差分", -0.50, 0.50, 0.00, step=0.01, key=f"form_d_{i}")
                f_diffs.append(d)
        
        if st.form_submit_button("💾 クラウドに保存", use_container_width=True):
            try:
                new_row = [str(datetime.date.today()), f_place] + f_diffs
                worksheet.append_row(new_row)
                st.success("✅ スプレッドシートへ保存しました。")
            except Exception as e:
                st.error(f"保存失敗: {e}")
