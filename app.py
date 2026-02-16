import streamlit as st
import pandas as pd
import datetime
import gspread
from google.oauth2.service_account import Credentials

# 1. 認証設定
def get_gsheet_client():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
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
    return gspread.authorize(Credentials.from_service_account_info(info, scopes=scopes))

# 2. 画面構成
st.title("🚤 競艇予想 Pro (安定版)")

try:
    gc = get_gsheet_client()
    sh = gc.open("競艇予想学習データ")
    ws = sh.get_worksheet(0)
    st.success("✅ クラウド接続成功！")
    
    # 簡易入力フォーム
    times = [st.number_input(f"{i+1}号艇", 6.0, 7.5, 6.7, 0.01) for i in range(6)]
    if st.button("比較"):
        fastest = min(times)
        for i, t in enumerate(times):
            st.write(f"{i+1}号艇: {t} (差: {round(t-fastest, 3)})")

except Exception as e:
    st.error(f"接続エラー: {e}")
