import streamlit as st
import pandas as pd
import numpy as np
import os
import base64
import gspread
from google.oauth2.service_account import Credentials
import datetime

# --- 設定 ---
st.set_page_config(page_title="競艇Pro 桐生", layout="wide")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PLACE_NAME = "桐生"

# --- 共通関数 ---
def encode_image(path):
    try:
        if os.path.exists(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        return ""
    except:
        return ""

def highlight_rank_style(df):
    """1位を赤、2位を黄にするスタイル適用関数"""
    def _highlight(col):
        s = pd.to_numeric(col, errors="coerce")
        # タイムなどは数値が小さい方が良いため ascending=True
        order = s.rank(method="min", ascending=True)
        styles = []
        for r in order:
            if pd.isna(r):
                styles.append("")
            elif r == 1:
                styles.append("background-color:#ff6b6b;color:white;")
            elif r == 2:
                styles.append("background-color:#ffd93d;")
            else:
                styles.append("")
        return styles
    return df.style.apply(_highlight, axis=0).format(precision=2)

def highlight_score_style(df, subset_col):
    """スコア（大きい方が良い）を基準にしたスタイル適用"""
    def _highlight_score(s):
        s2 = pd.to_numeric(s, errors="coerce")
        rank = s2.rank(ascending=False, method="min")
        return ["background-color:#ff6b6b" if r == 1 else "background-color:#ffd43b" if r == 2 else "" for r in rank]
    return df.style.apply(_highlight_score, subset=subset_col)

# --- 1. 認証 & 接続設定 ---
def get_gsheet_client():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        if "gcp_service_account" in st.secrets:
            credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
            return gspread.authorize(credentials)
        return None
    except Exception as e:
        st.error(f"認証エラー: {e}")
        return None

# --- 2. ログイン機能 ---
if "pwd_ok" not in st.session_state: st.session_state["pwd_ok"] = False
if not st.session_state["pwd_ok"]:
    st.title("🔐 競艇 Pro 解析ログイン")
    pwd = st.text_input("アクセスコード", type="password")
    if st.button("ログイン"):
        if pwd == "boat-pro-777":
            st.session_state["pwd_ok"] = True
            st.rerun()
    st.stop()

# --- 3. データ取得準備 ---
gc = get_gsheet_client()
sh = None
if gc:
    try:
        sh = gc.open_by_key("1lN794iGtyGV2jNwlYzUA8wEbhRwhPM7FxDAkMaoJss4")
    except Exception as e:
        st.error(f"スプレッドシートへのアクセスに失敗しました: {e}")

# --- 会場選択 ---
if st.button("← 会場選択へ戻る"):
    st.switch_page("public_app.py")

if "selected_place" not in st.session_state:
    st.session_state.selected_place = None

if st.session_state.selected_place is None:
    st.title("🏁 会場を選択してください")
    places = ["蒲郡", "大村", "住之江"]
    cols = st.columns(3)
    for i, p in enumerate(places):
        if cols[i].button(p, use_container_width=True):
            st.session_state.selected_place = p
            st.rerun()
    st.stop()

place = st.session_state.selected_place
st.caption(f"選択中の会場：{place}")

# CSS
st.markdown("""
<style>
.slit-area { background:#dff3ff; padding:20px; border-radius:12px; position:relative; min-height:450px; }
.slit-line { position:absolute; top:0; bottom:0; left:120px; width:3px; background:#ff5c5c; opacity:0.9; }
.slit-row { display:flex; align-items:center; height:70px; position:relative; z-index:2; }
.slit-boat { transition: all 0.4s ease; display:flex; align-items:center; }
</style>
""", unsafe_allow_html=True)

# タブ構成
tabs = st.tabs(["⭐ 簡易予想", "📊 統計解析", "🚀 スタート予想", "混合戦スタート精度", "風・波補正", "👩 女子戦データ", "女子戦補正閲覧", "女子戦補正入力", "女子戦スタート予想", "女子戦スタート精度"])
tab_pre, tab_stat, tab5, tab_mix_check, tab_cond, tab_view, tab_women_stat, tab_women_input, tab_women_start, tab_women_result = tabs

# --- タブ1：事前簡易予想 ---
with tab_pre:
    st.subheader("🎯 事前簡易予想（評価カード）")
    SYMBOL_VALUES = {"◎": 100, "○": 80, "▲": 60, "△": 40, "×": 20, "無": 0}
    WEIGHTS = {"モーター": 0.25, "当地勝率": 0.2, "枠番勝率": 0.3, "枠番スタート": 0.25}

    boat_evals = {}
    with st.form("pre_eval_form"):
        for row in range(3):
            cols = st.columns(2)
            for col in range(2):
                i = row * 2 + col + 1
                with cols[col]:
                    st.markdown(f"#### 🚤 {i}号艇")
                    m = st.selectbox("モーター", ["◎", "○", "▲", "△", "×", "無"], index=5, key=f"pre_m_{i}")
                    t = st.selectbox("当地勝率", ["◎", "○", "▲", "△", "×", "無"], index=5, key=f"pre_t_{i}")
                    w = st.selectbox("枠番勝率", ["◎", "○", "▲", "△", "×", "無"], index=5, key=f"pre_w_{i}")
                    s = st.selectbox("枠番ST", ["◎", "○", "▲", "△", "×", "無"], index=5, key=f"pre_s_{i}")
                    score = (SYMBOL_VALUES[m]*WEIGHTS["モーター"] + SYMBOL_VALUES[t]*WEIGHTS["当地勝率"] + 
                             SYMBOL_VALUES[w]*WEIGHTS["枠番勝率"] + SYMBOL_VALUES[s]*WEIGHTS["枠番スタート"])
                    boat_evals[i] = round(score, 3)
        submitted = st.form_submit_button("📊 予想カード生成", use_container_width=True, type="primary")

    if submitted:
        df_score = pd.DataFrame([{"艇番": k, "score": v} for k, v in boat_evals.items()])
        total_score = df_score["score"].sum()
        if total_score > 0:
            df_score["予想％"] = (df_score["score"] / total_score * 100).round(1)
            df_score = df_score.sort_values("予想％", ascending=False).reset_index(drop=True)
            diff = 100.0 - df_score["予想％"].sum()
            df_score.loc[0, "予想％"] = round(df_score.loc[0, "予想％"] + diff, 1)
            
            cols = st.columns(3)
            for i, r in df_score.iterrows():
                rank = i + 1
                bg = "#fff1c1" if rank==1 else "#f0f0f0" if rank==2 else "#ffe4d6" if rank==3 else "#fafafa"
                with cols[i % 3]:
                    st.markdown(f"""<div style="background:{bg}; border:2px solid #ddd; border-radius:14px; padding:14px; text-align:center;">
                        <div style="font-size:26px;font-weight:700;">{int(r['艇番'])}号艇</div>
                        <div style="font-size:22px;">{r['予想％']:.1f}%</div></div>""", unsafe_allow_html=True)

# --- タブ2：統計解析 ---
with tab_stat:
    st.subheader("会場別 補正・総合比較")
    if st.button("統計データを読み込んで比較する", key="tab2_load_btn"):
        if sh:
            ws1 = sh.worksheet(f"{place}_統計シート")
            ws2 = sh.worksheet(f"{place}_統計シート②")
            base_df = pd.DataFrame(ws1.get_all_records() + ws2.get_all_records())
            st.session_state["tab2_base_df"] = base_df
        else:
            st.error("スプレッドシートが利用できません")

    if "tab2_base_df" in st.session_state:
        base_df = st.session_state["tab2_base_df"].copy()
        # 数値型変換
        for c in ["展示", "直線", "一周", "回り足", "艇番"]:
            if c in base_df.columns: base_df[c] = pd.to_numeric(base_df[c], errors="coerce")
        
        # 当日入力フォーム
        with st.form("tab2_input_form"):
            input_rows = []
            cols_h = st.columns([1,2,2,2,2])
            labels = ["艇番","一周","回り足","直線","展示"]
            for idx, l in enumerate(labels): cols_h[idx].write(l)
            
            for b in range(1, 7):
                c = st.columns([1,2,2,2,2])
                c[0].write(f"{b}")
                isshu = c[1].number_input("1", step=0.01, format="%.2f", key=f"t2_i_{b}", label_visibility="collapsed")
                mawari = c[2].number_input("2", step=0.01, format="%.2f", key=f"t2_m_{b}", label_visibility="collapsed")
                choku = c[3].number_input("3", step=0.01, format="%.2f", key=f"t2_c_{b}", label_visibility="collapsed")
                tenji = c[4].number_input("4", step=0.01, format="%.2f", key=f"t2_t_{b}", label_visibility="collapsed")
                input_rows.append({"艇番":b, "展示":tenji, "直線":choku, "一周":isshu, "回り足":mawari})
            
            if st.form_submit_button("再計算"):
                st.session_state["tab2_input_df"] = pd.DataFrame(input_rows).set_index("艇番")

        if "tab2_input_df" in st.session_state:
            input_df = st.session_state["tab2_input_df"]
            st.markdown("### 補正結果")
            st.dataframe(highlight_rank_style(input_df), use_container_width=True)

# --- タブ5：スタート予想 ---
with tab5:
    st.subheader("🚀 スタート予想")
    if sh:
        try:
            ws = sh.worksheet("管理用_NEW")
            df_manage = pd.DataFrame(ws.get_all_records())
            # 必要な処理...
            if not df_manage.empty:
                st.write("データ読み込み完了")
                # ここにスタート予想のメインロジックを記述
        except Exception as e:
            st.error(f"シート読み込みエラー: {e}")

# ※ 他のタブも同様に、sh が None でないことを確認しながら実装を整理してください。
