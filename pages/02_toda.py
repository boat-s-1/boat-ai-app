import streamlit as st
import pandas as pd
import os

# ==============================
# 1. 会場名の固定定義
# ==============================
# 変数を「戸田」に固定します
PLACE_NAME = "戸田"
st.session_state["selected_place"] = PLACE_NAME 

# ページ設定
st.set_page_config(page_title=f"競艇Pro {PLACE_NAME}", layout="wide")

# ==============================
# 2. メインUI
# ==============================
st.title(f"🚀 {PLACE_NAME} 解析システム")

# タブの定義（事前予想を1番目に配置）
tab_pre, tab_stat, tab_start, tab_input = st.tabs([
    "🎯 事前簡易予想", 
    "📊 統計解析", 
    "🚀 スタート予想", 
    "📝 データ入力"
])

# ==============================
# --- タブ1：事前簡易予想 ---
# ==============================
with tab_pre:
    st.subheader("🎯 事前簡易予想（評価カード）")

    SYMBOL_VALUES = {"◎": 100, "○": 80, "▲": 60, "△": 40, "×": 20, "無": 0}
    WEIGHTS = {
        "モーター": 0.25,
        "当地勝率": 0.2,
        "枠番勝率": 0.3,
        "枠番スタート": 0.25
    }

    with st.form("pre_eval_form"):
        boat_evals = {}
        # 3行2列で6艇分を表示
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

                    score = (
                        SYMBOL_VALUES[m] * WEIGHTS["モーター"]
                        + SYMBOL_VALUES[t] * WEIGHTS["当地勝率"]
                        + SYMBOL_VALUES[w] * WEIGHTS["枠番勝率"]
                        + SYMBOL_VALUES[s] * WEIGHTS["枠番スタート"]
                    )
                    boat_evals[i] = round(score, 3)

        submitted = st.form_submit_button("📊 予想カード生成", use_container_width=True, type="primary")

    # 結果表示
    if submitted:
        df_score = pd.DataFrame([{"艇番": k, "score": v} for k, v in boat_evals.items()])
        df_score["score"] = df_score["score"].fillna(0)

        total_score = df_score["score"].sum()
        if total_score == 0:
            st.warning("すべて『無』のため、％を計算できません")
        else:
            # ％正規化
            df_score["予想％"] = df_score["score"] / total_score * 100
            df_score["予想％"] = df_score["予想％"].round(1)

            # 並び替えと誤差補正
            df_score = df_score.sort_values("予想％", ascending=False).reset_index(drop=True)
            diff = 100.0 - df_score["予想％"].sum()
            df_score.loc[0, "予想％"] = round(df_score.loc[0, "予想％"] + diff, 1)
            df_score["順位"] = df_score.index + 1

            st.markdown("### 🏁 予想結果（合計100％）")
            res_cols = st.columns(3)
            for i, r in df_score.iterrows():
                rank = int(r["順位"])
                boat = int(r["艇番"])
                pct = float(r["予想％"])

                # スタイル設定
                styles = {
                    1: {"bg": "#fff1c1", "border": "#f5b700", "title": "🥇 1位"},
                    2: {"bg": "#f0f0f0", "border": "#b5b5b5", "title": "🥈 2位"},
                    3: {"bg": "#ffe4d6", "border": "#e39a6f", "title": "🥉 3位"}
                }
                s = styles.get(rank, {"bg": "#fafafa", "border": "#dddddd", "title": f"{rank}位"})

                with res_cols[i % 3]:
                    st.markdown(f"""
                        <div style="background:{s['bg']}; border:2px solid {s['border']}; border-radius:14px; padding:14px; text-align:center; box-shadow:0 4px 8px rgba(0,0,0,0.05); margin-bottom:10px;">
                            <div style="font-size:15px;color:#555;">{s['title']}</div>
                            <div style="font-size:26px;font-weight:700;margin-top:4px;">{boat}号艇</div>
                            <div style="font-size:22px;color:#222;margin-top:6px;">{pct:.1f}%</div>
                        </div>
                    """, unsafe_allow_html=True)

            st.divider()
            st.markdown("### 📋 内訳（デバッグ用）")
            st.dataframe(df_score[["順位", "艇番", "score", "予想％"]], use_container_width=True, hide_index=True)

# --- タブ2：統計解析 ---
with tab_stat:
    st.subheader(f"📊 {PLACE_NAME} 補正・総合比較")

    # レース種別の選択（混合か女子か）
    # ※タブの外で定義している場合はそれを使いますが、念のためここでも確認
    race_type = st.radio("統計データ種別", ["混合", "女子"], horizontal=True, key="tab2_race_type")
    target_sheet = f"{PLACE_NAME}_{race_type}統計"

    # ======================================
    # 1. 統計データ読み込みボタン
    # ======================================
    if st.button(f"{target_sheet} データを読み込む", key="tab2_load_btn"):
        with st.spinner(f"{target_sheet} を取得中..."):
            try:
                # gc (gspread_client) は事前に定義済みと想定
                sh = gc.open_by_key("1lN794iGtyGV2jNwlYzUA8wEbhRwhPM7FxDAkMaoJss4")
                ws = sh.worksheet(target_sheet)
                rows = ws.get_all_records()
                
                if rows:
                    base_df = pd.DataFrame(rows)
                    # 型調整
                    for c in ["展示", "直線", "一周", "回り足", "艇番"]:
                        if c in base_df.columns:
                            base_df[c] = pd.to_numeric(base_df[c], errors="coerce")
                    
                    st.session_state["tab2_base_df"] = base_df
                    st.success(f"✅ {len(base_df)}件のデータを読み込みました")
                else:
                    st.error("データが空です")
            except Exception as e:
                st.error(f"シートの読み込みに失敗しました。シート名「{target_sheet}」が存在するか確認してください。\n{e}")

    # データが読み込まれていない場合は中断
    if "tab2_base_df" not in st.session_state:
        st.info(f"「{target_sheet} データを読み込む」ボタンを押してください。")
        st.stop()

    place_df = st.session_state["tab2_base_df"].copy()

    # ======================================
    # 2. 計算用数値の算出
    # ======================================
    # 会場内での艇番別平均
    place_mean = place_df.groupby("艇番")[["展示", "直線", "一周", "回り足"]].mean()
    # 会場全体の平均
    overall_mean = place_df[["展示", "直線", "一周", "回り足"]].mean()
    # 枠番バイアス（イン有利度など）
    lane_bias = place_mean - overall_mean

    race_count = len(place_df) // 6 # 簡易的なレース数計算
    st.caption(f"📊 {PLACE_NAME} ({race_type}戦) 過去データ約 {race_count} レースより算出")

    # ======================================
    # 3. 入力フォーム
    # ======================================
    st.divider()
    st.markdown("### 📝 展示タイム入力（当日）")

    with st.form("tab2_input_form"):
        input_rows = []
        head = st.columns([1, 2, 2, 2, 2])
        head[0].markdown("**艇番**")
        head[1].markdown("**一周**")
        head[2].markdown("**回り足**")
        head[3].markdown("**直線**")
        head[4].markdown("**展示**")

        for b in range(1, 7):
            cols = st.columns([1, 2, 2, 2, 2])
            cols[0].markdown(f"**{b}号艇**")
            isshu = cols[1].number_input("一周", step=0.01, format="%.2f", key=f"tab2_in_isshu_{b}", label_visibility="collapsed")
            mawari = cols[2].number_input("回り足", step=0.01, format="%.2f", key=f"tab2_in_mawari_{b}", label_visibility="collapsed")
            choku = cols[3].number_input("直線", step=0.01, format="%.2f", key=f"tab2_in_choku_{b}", label_visibility="collapsed")
            tenji = cols[4].number_input("展示", step=0.01, format="%.2f", key=f"tab2_in_tenji_{b}", label_visibility="collapsed")
            
            input_rows.append({"艇番": b, "展示": tenji, "直線": choku, "一周": isshu, "回り足": mawari})

        submit_input = st.form_submit_button("🔥 タイム補正を計算する", use_container_width=True)

    if submit_input:
        st.session_state["tab2_input_df"] = pd.DataFrame(input_rows).set_index("艇番")

    # 入力データがない場合はここでストップ
    if "tab2_input_df" not in st.session_state:
        st.stop()

    input_df = st.session_state["tab2_input_df"]

    # ======================================
    # 4. 補正計算と表示
    # ======================================
    def highlight_rank(df):
        def color_col(s):
            s2 = pd.to_numeric(s, errors="coerce")
            rank = s2.rank(method="min")
            return ["background-color:#ff6b6b;color:white;" if r == 1 else "background-color:#ffd43b;" if r == 2 else "" for r in rank]
        return df.style.apply(color_col, axis=0).format("{:.2f}")

    # --- A. 入力値そのまま ---
    st.markdown("#### ① 公式展示タイム表（入力値）")
    st.dataframe(highlight_rank(input_df), use_container_width=True)

    # --- B. 場平均補正 ---
    adj_df = input_df.copy()
    for b in range(1, 7):
        if b in place_mean.index:
            for col in ["展示", "直線", "一周", "回り足"]:
                if pd.notna(input_df.loc[b, col]):
                    adj_df.loc[b, col] = input_df.loc[b, col] - place_mean.loc[b, col] + overall_mean[col]

    st.markdown("#### ② 場平均補正（会場平均との比較）")
    st.dataframe(highlight_rank(adj_df), use_container_width=True)

    # --- C. 枠番補正（イン有利補正） ---
    final_df = adj_df.copy()
    for b in range(1, 7):
        if b in lane_bias.index:
            for col in ["展示", "直線", "一周", "回り足"]:
                if pd.notna(adj_df.loc[b, col]):
                    final_df.loc[b, col] = adj_df.loc[b, col] - lane_bias.loc[b, col]

    st.markdown("#### ③ 枠番補正込み（最終評価タイム）")
    st.dataframe(highlight_rank(final_df), use_container_width=True)
