import streamlit as st
import pandas as pd

# --- スコア設定 ---
SYMBOL_VALUES = {"◎": 100, "○": 80, "▲": 60, "△": 40, "×": 20, "無": 0}
# 項目ごとの重み付け（例：枠番勝率を少し重視するなど調整可能）
WEIGHTS = {"モーター": 0.25, "当地勝率": 0.2, "枠番勝率": 0.3, "枠番スタート": 0.25}

# (認証・データ読み込み部分は既存のまま)

st.title("🚤 競艇 Pro 解析システム")

# タブ構成
tab_pre, tab_data, tab_log, tab_memo = st.tabs(["⭐ 事前簡易予想", "📊 統計解析", "📜 過去ログ", "📝 攻略メモ"])

# --- ⭐ 事前簡易予想タブ ---
with tab_pre:
    st.subheader("各艇の4項目評価")
    st.caption("モーター・当地・枠番勝率・スタートを記号で選ぶと、総合期待度を算出します。")

    # 入力フォーム
    with st.form("pre_eval_form"):
        boat_evals = {}
        
        # 1号艇〜6号艇まで横並び、または見やすく配置
        for i in range(1, 7):
            st.markdown(f"#### {i}号艇")
            cols = st.columns(4)
            m = cols[0].selectbox("モーター", ["◎", "○", "▲", "△", "×", "無"], index=5, key=f"m_{i}")
            t = cols[1].selectbox("当地勝率", ["◎", "○", "▲", "△", "×", "無"], index=5, key=f"t_{i}")
            w = cols[2].selectbox("枠番勝率", ["◎", "○", "▲", "△", "×", "無"], index=5, key=f"w_{i}")
            s = cols[3].selectbox("枠番ST", ["◎", "○", "▲", "△", "×", "無"], index=5, key=f"s_{i}")
            
            # 各艇のスコア計算（重み付け平均）
            total_score = (
                SYMBOL_VALUES[m] * WEIGHTS["モーター"] +
                SYMBOL_VALUES[t] * WEIGHTS["当地勝率"] +
                SYMBOL_VALUES[w] * WEIGHTS["枠番勝率"] +
                SYMBOL_VALUES[s] * WEIGHTS["枠番スタート"]
            )
            boat_evals[i] = round(total_score, 1)
            st.divider()

        submitted = st.form_submit_button("予想カードを生成・ランク付け", use_container_width=True, type="primary")

    if submitted:
        # スコア順にソート
        sorted_boats = sorted(boat_evals.items(), key=lambda x: x[1], reverse=True)
        
        st.write("### 🏁 総合期待度ランキング")
        res_cols = st.columns(3)
        
        for idx, (boat_num, score) in enumerate(sorted_boats):
            with res_cols[idx % 3]:
                # 順位に応じたカード表示
                rank_icon = ["🥇", "🥈", "🥉", "4th", "5th", "6th"]
                with st.container(border=True):
                    st.markdown(f"### {rank_icon[idx]} {boat_num}号艇")
                    st.metric("総合期待度", f"{score}%")
                    st.progress(score / 100)
                    
                    # 評価のワンポイントアドバイス
                    if score >= 80: st.info("🔥 鉄板級の評価です")
                    elif score >= 60: st.warning("✅ 軸・相手に必須")
                    elif score < 30: st.error("⚠️ 軽視可能")

        if sorted_boats[0][1] >= 85:
            st.balloons()
