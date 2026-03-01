import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import os
import base64

# ======================================
# 1. 初期設定・認証
# ======================================
PLACE_NAME = "下関"
st.session_state["selected_place"] = PLACE_NAME 

# ページ設定
st.set_page_config(page_title=f"競艇Pro {PLACE_NAME}", layout="wide")

# Google Sheets 認証
if "gcp_service_account" in st.secrets:
    info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(
        info, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    )
    gc = gspread.authorize(creds)
else:
    st.error("Google Cloudの認証情報が設定されていません。")
    st.stop()

# 画像読み込み用の設定
BASE_DIR = os.path.dirname(os.path.dirname(__file__)) 

# ======================================
# 2. メインUI（データ管理エリア）
# ======================================
st.title(f"🚀 {PLACE_NAME} 解析システム")

with st.container(border=True): 
    c1, c2, c3 = st.columns([1.5, 2, 2])
    
    with c1:
        race_type_val = st.radio("解析対象を選択", ["混合", "女子"], horizontal=True, key="top_race_type")
    
    with c2:
        target_sheet = f"{PLACE_NAME}_{race_type_val}統計"
        
        if st.button(f"🔄 {target_sheet} を読み込む", use_container_width=True, key="top_load_btn"):
            with st.spinner("データ取得中..."):
                try:
                    # スプレッドシートID（下関用）
                    sh = gc.open_by_key("1rSzJuk5Hyv60nMwX67pCufXz45HLykyIXuqVE6wtNII")
                    ws = sh.worksheet(target_sheet)

                    # データ取得と重複ヘッダー対策
                    data = ws.get_all_records()
                    df = pd.DataFrame(data)

                    # 列の存在チェックと数値変換
                    required_cols = ["展示", "直線", "一周", "回り足", "艇番", "ST", "着順"]
                    for c in required_cols:
                        if c in df.columns:
                            df[c] = pd.to_numeric(df[c], errors="coerce")
                        else:
                            st.warning(f"⚠️ 列『{c}』がシートにありません。0で代用します。")
                            df[c] = 0 

                    st.session_state["tab2_base_df"] = df
                    st.toast(f"✅ {target_sheet} を適用しました")
                except Exception as e:
                    st.error(f"読込失敗: {e}")

    with c3:
        if "tab2_base_df" in st.session_state:
            count = len(st.session_state["tab2_base_df"])
            st.success(f"適用中: {target_sheet} ({count}件)")
        else:
            st.warning("⚠️ データ未読込です")

st.divider()

# データが読み込まれるまで以降の処理を停止（KeyError防止）
if "tab2_base_df" not in st.session_state:
    st.info("👆 まずは「データを読み込む」ボタンを押してください。")
    st.stop()

# ======================================
# 3. タブの定義
# ======================================
tab_pre, tab_stat, tab_start, tab_rank, tab_mix_check = st.tabs([
    "🎯 事前簡易予想", "📊 統計解析", "🚀 スタート予想", "展示・ST 項目別順位", "📝 スタート指数"
])

# --- タブ1：事前簡易予想 ---
with tab_pre:
    st.subheader("🎯 事前簡易予想（評価カード）")
    # (既存の事前予想ロジックは正常なため維持)
    SYMBOL_VALUES = {"◎": 100, "○": 80, "▲": 60, "△": 40, "×": 20, "無": 0}
    WEIGHTS = {"モーター": 0.25, "当地勝率": 0.2, "枠番勝率": 0.3, "枠番スタート": 0.25}

    with st.form("pre_eval_form"):
        boat_evals = {}
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
            st.dataframe(df_score, use_container_width=True)

# --- タブ2：統計解析 ---
with tab_stat:
    st.subheader(f"📊 {PLACE_NAME} 補正・総合比較")
    place_df = st.session_state["tab2_base_df"].copy()
    items = ["展示", "直線", "一周", "回り足"]

    place_mean = place_df.groupby("艇番")[items].mean()
    overall_mean = place_df[items].mean()
    lane_bias = place_mean - overall_mean
    st.caption(f"📊 {PLACE_NAME} ({race_type_val}) 過去データより算出")

    st.markdown("### 📝 展示タイム入力")
    with st.form("shimo_input_form"):
        input_rows = []
        for b in range(1, 7):
            cols = st.columns([1, 2, 2, 2, 2])
            cols[0].write(f"**{b}**")
            isshu = cols[1].number_input("一周", step=0.01, format="%.2f", key=f"in_iss_{b}", label_visibility="collapsed")
            mawari = cols[2].number_input("回り足", step=0.01, format="%.2f", key=f"in_maw_{b}", label_visibility="collapsed")
            choku = cols[3].number_input("直線", step=0.01, format="%.2f", key=f"in_cho_{b}", label_visibility="collapsed")
            tenji = cols[4].number_input("展示", step=0.01, format="%.2f", key=f"in_ten_{b}", label_visibility="collapsed")
            input_rows.append({"艇番": b, "展示": tenji, "直線": choku, "一周": isshu, "回り足": mawari})
        submit_input = st.form_submit_button("🔥 タイム補正を計算する", use_container_width=True)

    if submit_input:
        st.session_state["tab2_input_df"] = pd.DataFrame(input_rows).set_index("艇番")

    if "tab2_input_df" in st.session_state:
        input_df = st.session_state["tab2_input_df"]
        # (補正計算ロジック)
        final_df = input_df.copy()
        for b in range(1, 7):
            for col in items:
                adj_val = input_df.loc[b, col] - place_mean.loc[b, col] + overall_mean[col]
                final_df.loc[b, col] = adj_val - lane_bias.loc[b, col]
        st.dataframe(final_df.style.highlight_min(axis=0, color='red'), use_container_width=True)

# --- タブ3：スタート予想 ---
with tab_start:
    st.subheader(f"🚀 スタート予想")
    place_df = st.session_state["tab2_base_df"]
    mean_tenji = place_df["展示"].mean()
    mean_isshu = place_df["一周"].mean()

    input_defaults = st.session_state.get("tab2_input_df", pd.DataFrame())
    input_cols = st.columns(6)
    rows = []
    eval_map = {"◎": 2.0, "◯": 1.0, "△": 0.5, "×": -1.0}

    for i in range(1, 7):
        with input_cols[i-1]:
            st.markdown(f"**{i}号艇**")
            t_val = st.number_input("展示", value=float(input_defaults.loc[i, "展示"] if i in input_defaults.index else 0), key=f"st_ten_{i}")
            i_val = st.number_input("一周", value=float(input_defaults.loc[i, "一周"] if i in input_defaults.index else 0), key=f"st_iss_{i}")
            s_val = st.number_input("ST", step=0.01, key=f"st_st_{i}")
            e_val = st.selectbox("評価", ["", "◎", "◯", "△", "×"], key=f"st_ev_{i}")
            
            score = -s_val + eval_map.get(e_val, 0) + (mean_tenji - t_val)*2.0 + (mean_isshu - i_val)*0.3
            rows.append({"艇番": i, "start_score": score, "ST": s_val, "評価": e_val})

    res_df = pd.DataFrame(rows)
    st.dataframe(res_df.sort_values("start_score", ascending=False), use_container_width=True)

# --- タブ4：展示・ST 項目別順位 ---
with tab_rank:
    if "tab2_input_df" in st.session_state:
        # (先ほど作成した🏆表示ロジック)
        st.markdown("### 🥇 補正後ランキング（🏆表示）")
        # 枠色・文字色の設定などは維持
        bg_colors = ["", "#FFFFFF", "#000000", "#FF0000", "#0000FF", "#FFFF00", "#008000"]
        text_colors = ["", "#000000", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#000000", "#FFFFFF"]
        # ... (中略：前回の🏆表示コードを適用) ...
        st.info("統計解析タブの入力を反映しています。")

# --- タブ5：精度検証 ---
with tab_mix_check:
    st.subheader("📝 スタート指数 精度検証")
    # (既存の検証ロジックを維持)
    df_v = st.session_state["tab2_base_df"].copy()
    if "着順" in df_v.columns:
        st.write(f"過去 {len(df_v)//6} レースの的中率を計算中...")
        # ... (中略：前回の検証コードを適用) ...
    else:
        st.error("シートに着順データがありません。")
