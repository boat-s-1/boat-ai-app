import streamlit as st
import pandas as pd
import os

# --- 設定（PLACE_NAMEなどは共通変数として定義済みと想定） ---
# PLACE_NAME = st.session_state.get("selected_place", "戸田")

# --- メインUI ---
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

# --- 他のタブ（統計解析など）はここに続く ---
with tab_stat:
    st.write(f"{PLACE_NAME} の統計データをここに表示")
