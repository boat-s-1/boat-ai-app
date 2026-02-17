import streamlit as st
import pandas as pd
import gspread
import plotly.express as px
from google.oauth2.service_account import Credentials

def get_gsheet_client():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
        return gspread.authorize(credentials)
    except: return None

if "pwd_ok" not in st.session_state: st.session_state["pwd_ok"] = False
if not st.session_state["pwd_ok"]:
    st.title("🔐 競艇 Pro 解析ログイン")
    pwd = st.text_input("アクセスコード", type="password")
    if st.button("ログイン"):
        if pwd == "boat-pro-777":
            st.session_state["pwd_ok"] = True
            st.rerun()
    st.stop()

st.set_page_config(page_title="競艇 Pro 解析パネル", layout="wide")
df = pd.DataFrame()
gc = get_gsheet_client()

if gc:
    try:
        sh = gc.open("競艇予想学習データ")
        ws = sh.get_worksheet(0)
        raw_data = ws.get_all_values()
        if len(raw_data) > 1:
            df = pd.DataFrame(raw_data[1:], columns=raw_data[0])
    except: pass

st.title("🚤 競艇 Pro 解析システム")

# --- メイン解析タブ ---
tab1, tab2, tab3, tab4 = st.tabs(["🎯 簡易版（狙い目）", "📊 詳細版（全データ）", "📜 過去ログ", "📝 攻略メモ"])

with tab1:
    st.subheader("本日の狙い目診断")
    c1, c2 = st.columns([1, 2])
    with c1:
        place = st.selectbox("会場", ["若松", "大村", "多摩川", "蒲郡", "戸田", "江戸川", "平和島", "浜名湖", "常滑", "津", "三国", "びわこ", "住之江", "尼崎", "鳴門", "丸亀", "児島", "宮島", "徳山", "下関", "芦屋", "福岡", "唐津", "桐生"])
        wdir = st.selectbox("風向き", ["向い風", "追い風", "左横風", "右横風", "無風"])
        # 簡易版は代表的なタイム（展示等）だけで判定
        test_time = [st.number_input(f"{i}号艇 タイム", 6.0, 7.5, 6.70, 0.01, key=f"s_{i}") for i in range(1, 7)]
        btn = st.button("簡易解析スタート", use_container_width=True, type="primary")

    with c2:
        if btn and not df.empty:
            fastest = min(test_time)
            diffs = [round(t - fastest, 3) for t in test_time]
            
            # 独自ロジックでのアドバイス
            best_boat = diffs.index(0) + 1
            st.success(f"⭐ 今レースの機力注目艇: **{best_boat}号艇**")
            if diffs[0] == 0:
                st.balloons()
                st.info("💡 1号艇が最速です。イン逃げの信頼度が非常に高いデータが出ています。")
            
            # 過去の統計グラフ
            match = df[(df.iloc[:, 1] == place) & (df.iloc[:, 6] == wdir)]
            if not match.empty:
                w1 = pd.to_numeric(match.iloc[:, 3], errors='coerce').tolist()
                all_3 = w1 + pd.to_numeric(match.iloc[:, 4], errors='coerce').tolist() + pd.to_numeric(match.iloc[:, 5], errors='coerce').tolist()
                res = [{"号艇": f"{i}号", "1着率": (w1.count(i)/len(match))*100, "3連対率": (all_3.count(i)/len(match))*100} for i in range(1,7)]
                st.plotly_chart(px.bar(pd.DataFrame(res), x="号艇", y=["1着率", "3連対率"], barmode="group", title="過去の同条件的中傾向"), use_container_width=True)
            else:
                st.write("過去に同条件のデータがありません。")

with tab2:
    st.subheader("玄人向け：全機力偏差データ")
    if not df.empty:
        st.write("展示・直線・1周・回り足のすべての偏差を比較します。")
        # 詳細な入力項目（4種類）
        cols = st.columns(4)
        ex_t = [cols[0].number_input(f"{i}号 展示", 6.0, 7.5, 6.70, 0.01, key=f"ex_d_{i}") for i in range(1, 7)]
        st_t = [cols[1].number_input(f"{i}号 直線", 6.0, 15.0, 7.00, 0.01, key=f"st_d_{i}") for i in range(1, 7)]
        lp_t = [cols[2].number_input(f"{i}号 1周", 30.0, 45.0, 37.00, 0.01, key=f"lp_d_{i}") for i in range(1, 7)]
        tn_t = [cols[3].number_input(f"{i}号 回り", 3.0, 10.0, 5.00, 0.01, key=f"tn_d_{i}") for i in range(1, 7)]
        
        if st.button("詳細偏差を表示"):
            def show_m(name, times):
                st.write(f"▼ {name}偏差")
                f = min(times)
                ds = [round(t - f, 3) for t in times]
                dc = st.columns(6)
                for j, d in enumerate(ds): dc[j].metric(f"{j+1}号", f"{d:.2f}")
            
            show_m("展示タイム", ex_t)
            show_m("直線タイム", st_t)
            show_m("1周タイム", lp_t)
            show_m("回り足タイム", tn_t)

with tab3:
    st.subheader("データログ")
    st.dataframe(df, use_container_width=True)

with tab4:
    st.subheader("会場別攻略メモ")
    try:
        ws_m = sh.worksheet("攻略メモ")
        m_data = ws_m.get_all_records()
        if m_data:
            for m in reversed(m_data):
                st.info(f"📌 **{m['会場']}** ({m['日付']})\n\n{m['メモ']}")
    except: st.write("メモがありません。")
