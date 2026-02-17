import streamlit as st
import pandas as pd
import datetime
import gspread
from google.oauth2.service_account import Credentials

# --- 1. 認証 & 接続設定 ---
def get_gsheet_client():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        # StreamlitのSecretsから認証情報を取得
        if "gcp_service_account" not in st.secrets:
            st.error("Secretsに 'gcp_service_account' が設定されていません。")
            return None
        credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
        return gspread.authorize(credentials)
    except Exception as e:
        st.error(f"接続エラー: {e}")
        return None

# --- ページ設定 ---
st.set_page_config(page_title="管理者用：競艇機力分析", page_icon="⚙️", layout="wide")

# 定数
PLACES = ["桐生", "戸田", "江戸川", "平和島", "多摩川", "浜名湖", "蒲郡", "常滑", "津", "三国", "びわこ", "住之江", "尼崎", "鳴門", "丸亀", "児島", "宮島", "徳山", "下関", "若松", "芦屋", "福岡", "唐津", "大村"]
DIRS = ["向い風", "追い風", "左横風", "右横風", "無風"]

# クラウド接続
gc = get_gsheet_client()
sh = None
ws_data = None
ws_memo = None

if gc:
    try:
        sh = gc.open("競艇予想学習データ")
        ws_data = sh.get_worksheet(0)  # 的中データ用シート
        ws_memo = sh.worksheet("攻略メモ") # 攻略メモ用シート
    except Exception as e:
        st.warning(f"シートの読み込みに失敗しました（シート名を確認してください）: {e}")

st.title("🚤 競艇予想 Pro Cloud (管理者)")

# タブの作成
tab1, tab2, tab3 = st.tabs(["🕒 タイム入力・偏差計算", "📊 的中データ登録", "📝 攻略メモ編集"])

# --- Tab 1: タイム入力 ---
with tab1:
    st.subheader("現在のレース：タイム入力")
    st.info("💡 ここで入力した数値が、的中登録時の『偏差（トップとの差）』として自動計算されます。")
    
    # 6艇分の入力フォーム
    cols = st.columns(3)
    for i in range(1, 7):
        # 2艇ずつ横に並べる
        with cols[(i-1) % 3]:
with st.expander(f"🚤 {i}号艇 タイム", expanded=True):
    st.number_input("展示タイム", 5.0, 8.0, 6.70, 0.01, key=f"ex_{i}")
    st.number_input("直線タイム", 5.0, 10.0, 7.00, 0.01, key=f"st_{i}")
    st.number_input("1周タイム", 30.0, 50.0, 37.00, 0.01, key=f"lp_{i}")
    st.number_input("回り足タイム", 3.0, 10.0, 5.00, 0.01, key=f"tn_{i}")

# --- Tab 2: 的中データ登録 (ここが保存のメイン) ---
with tab2:
    st.subheader("🏁 レース結果の保存")
    if ws_data is None:
        st.error("スプレッドシートのメインシートが見つかりません。")
    else:
        with st.form("result_form"):
            # 基本情報
            c1, c2, c3 = st.columns(3)
            f_place = c1.selectbox("会場", PLACES)
            f_race = c2.number_input("レースR", 1, 12, 1)
            f_win = c3.selectbox("実際の1着", [1, 2, 3, 4, 5, 6])
            
            # 気象
            w1, w2, w3 = st.columns(3)
            f_wdir = w1.selectbox("風向き", DIRS)
            f_wspd = w2.number_input("風速 (m)", 0, 15, 0)
            f_wave = w3.number_input("波高 (cm)", 0, 50, 0)

            st.write("---")
            st.markdown("🔍 **保存内容:** Tab1で入力した各項目の **『トップ差』** を保存します。")

            if st.form_submit_button("最速タイム基準でクラウドへ保存"):
                try:
                    # 各タイム項目をリスト化して偏差（自分のタイム - 最速）を計算
                    def get_diffs(prefix):
                        times = [st.session_state[f"{prefix}_{i}"] for i in range(1, 7)]
                        fastest = min(times)
                        return [round(t - fastest, 3) for t in times]

                    # 各種偏差を算出
                    diff_ex = get_diffs("ex") # 展示
                    diff_st = get_diffs("st") # 直線
                    diff_lp = get_diffs("lp") # 1周
                    diff_tn = get_diffs("tn") # 回り足

                    # 保存する1行を作成
                    # [日付, 会場, レース, 1着, 風向, 風速, 波高, 展示偏差(1-6), 直線偏差(1-6), 1周偏差(1-6), 回り足偏差(1-6)]
                    new_row = [
                        str(datetime.date.today()), f_place, f_race, f_win, f_wdir, f_wspd, f_wave
                    ] + diff_ex + diff_st + diff_lp + diff_tn
                    
                    ws_data.append_row(new_row)
                    st.success(f"✅ {f_place}{f_race}R のデータを保存しました。")
                except Exception as e:
                    st.error(f"保存エラー: {e}")

# --- Tab 3: 攻略メモ編集 ---
with tab3:
    st.subheader("📝 会場別攻略メモの更新")
    if ws_memo is None:
        st.info("スプレッドシートに『攻略メモ』という名前の新しいシートを作成してください。")
    else:
        with st.form("memo_form"):
            m_place = st.selectbox("会場を選択", PLACES)
            m_text = st.text_area("攻略アドバイスを入力（例：インが強い、展示は直線重視など）", height=150)
            if st.form_submit_button("メモを更新する"):
                try:
                    ws_memo.append_row([m_place, m_text, str(datetime.date.today())])
                    st.success(f"✅ {m_place}のメモを更新しました。配布アプリに反映されます。")
                except Exception as e:
                    st.error(f"メモ保存エラー: {e}")


