import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.express as px
import streamlit.components.v1 as components

# ==========================================
# 1. 基本設定とデータソース (GAS連携)
# ==========================================
st.set_page_config(page_title="競艇Pro Analytica - 24場完全版", layout="wide", page_icon="🎯")

# あなたが作成したGASのURL
GAS_URL = "https://script.google.com/macros/s/AKfycbwypoD8dV1DhXsX6C1wK893MAWKImWtKmbbQ9JwVOw0Rm13FZ8K9B4S97S8hGKeAvbQ/exec"

# ==========================================
# 2. 高速解析エンジン (GAS JSON読込)
# ==========================================
@st.cache_data(ttl=3600)
def load_all_stats_from_gas():
    stats = {}
    try:
        # GASから全シートのデータを一括取得
        response = requests.get(GAS_URL)
        all_data = response.json()
        
        for sheet_name, rows in all_data.items():
            if len(rows) < 2: continue
            
            # 会場名の整形 (例: 桐生_混合統計 -> 桐生)
            place = sheet_name.replace("_混合統計", "").strip()
            
            # DataFrame化 (1行目はヘッダー)
            df = pd.DataFrame(rows[1:], columns=rows[0])
            
            # 列名の空白削除
            df.columns = df.columns.str.strip()
            
            # 数値変換 (エラーはNaNにして除外)
            df['着順_num'] = pd.to_numeric(df['着順'], errors='coerce')
            df['展示_num'] = pd.to_numeric(df['展示'], errors='coerce')
            df = df.dropna(subset=['着順_num', '展示_num'])
            
            if df.empty: continue
            
            # 展示順位の計算 (レースごとにグループ化)
            # ※日付、レース番号、会場名が一致するものを1レースとする
            df['展示順位'] = df.groupby(['日付', 'レース番号'])['展示_num'].rank(method='min')
            
            # 統計指標の算出
            top_ex = df[df['展示順位'] == 1]
            win_rate = (top_ex['着順_num'] == 1).mean() * 100 if not top_ex.empty else 35.0
            show_rate = (top_ex['着順_num'] <= 3).mean() * 100 if not top_ex.empty else 65.0
            in_nige = (df[df['艇番'] == 1]['着順_num'] == 1).mean() * 100 if not df[df['艇番'] == 1].empty else 50.0
            
            stats[place] = {
                "展示信頼度": round(win_rate, 1), # 展示1位が1着をとる確率
                "展示貢献度": round(show_rate, 1), # 展示1位が3着以内に入る確率
                "イン逃げ率": round(in_nige, 1),
                "サンプル数": len(df)
            }
        return stats
    except Exception as e:
        st.error(f"データ連携エラー: {e}")
        return {}

# データの読み込み
ACTUAL_STATS = load_all_stats_from_gas()

# ==========================================
# 3. デザイン共通設定
# ==========================================
get_symbol = lambda val: {6: "◎", 5: "○", 4: "▲", 3: "△", 2: "×", 1: "・", 0: "無"}.get(val, "無")
boat_bg = {1: "#ffffff", 2: "#333333", 3: "#e03131", 4: "#1971c2", 5: "#fcc419", 6: "#2f9e44"}
boat_tx = {1: "#000000", 2: "#ffffff", 3: "#ffffff", 4: "#ffffff", 5: "#000000", 6: "#ffffff"}

# ==========================================
# 4. サイドバー (会場選択と実績表示)
# ==========================================
with st.sidebar:
    st.header("📋 開催地設定")
    if ACTUAL_STATS:
        available_places = sorted(list(ACTUAL_STATS.keys()))
        r_place = st.selectbox("会場を選択", available_places)
        r_num = st.number_input("レース番号", 1, 12, 1)
        
        # 統計表示
        p_stat = ACTUAL_STATS[r_place]
        st.divider()
        st.markdown(f"### 🏟️ {r_place} の実績データ")
        st.metric("イン逃げ率", f"{p_stat['イン逃げ率']}%")
        st.metric("展示1位の1着率", f"{p_stat['展示信頼度']}%")
        st.metric("展示1位の3連対率", f"{p_stat['展示貢献度']}%")
        st.caption(f"分析対象: {p_stat['サンプル数']} レース分")
    else:
        st.warning("GASからのデータ読込を待機中...")
    
    st.write("")
    # 広告コード (任意)
    components.html('<div style="display:flex; justify-content:center;"><script src="https://adm.shinobi.jp/s/00848ad75df65c15ca7f98de1efcf942"></script></div>', height=260)

# ==========================================
# 5. メインコンテンツ
# ==========================================
if ACTUAL_STATS:
    tab1, tab2 = st.tabs(["🔥 実績連動解析", "📊 会場データ比較"])

    with tab1:
        st.subheader(f"🏟️ {r_place} 専用解析モデル")
        
        # ロジック: 展示信頼度が高い場ほど「展示」の配点を自動で高くする
        ex_weight = min(0.5, p_stat['展示信頼度'] / 100 + 0.1)
        other_weight = (1.0 - ex_weight) / 3
        
        weights = {
            "展示気配": round(ex_weight, 2),
            "直線/伸び": round(other_weight, 2),
            "回り足": round(other_weight, 2),
            "一周タイム": round(other_weight, 2)
        }

        # 重要度の可視化
        fig = px.pie(values=list(weights.values()), names=list(weights.keys()), hole=0.4, 
                     color_discrete_sequence=px.colors.qualitative.Bold,
                     title=f"{r_place}での重要度配分 (実績に基づく)")
        st.plotly_chart(fig, use_container_width=True)

        with st.form("analysis_form"):
            live_data = []
            cols = st.columns(2)
            for i in range(1, 7):
                with cols[(i-1)%2]:
                    with st.expander(f"{i}号艇の気配", expanded=(i==1)):
                        st.markdown(f'<div style="background:{boat_bg[i]}; color:{boat_tx[i]}; padding:5px; border-radius:4px; text-align:center; font-weight:bold;">{i}号艇</div>', unsafe_allow_html=True)
                        f1 = st.select_slider(f"展示_{i}", range(7), 0, get_symbol, key=f"ex_{i}")
                        f2 = st.select_slider(f"直線_{i}", range(7), 0, get_symbol, key=f"st_{i}")
                        f3 = st.select_slider(f"旋回_{i}", range(7), 0, get_symbol, key=f"tu_{i}")
                        f4 = st.select_slider(f"総合_{i}", range(7), 0, get_symbol, key=f"all_{i}")
                        
                        score = (f1*weights["展示気配"] + f2*weights["直線/伸び"] + f3*weights["回り足"] + f4*weights["一周タイム"])
                        live_data.append({"艇番": i, "score": score, "展示": get_symbol(f1)})

            if st.form_submit_button("🔥 最終解析を実行", use_container_width=True, type="primary"):
                df_res = pd.DataFrame(live_data).sort_values("score", ascending=False)
                df_res["期待値"] = (df_res["score"] / df_res["score"].sum() * 100).round(1)
                
                st.balloons()
                st.success(f"🥇 推奨：{df_res.iloc[0]['艇番']}号艇 を軸にした展開が有力です。")
                st.dataframe(df_res[["艇番", "期待値", "展示"]], use_container_width=True, hide_index=True)
                
                # 買い目提案
                top_3 = df_res["艇番"].tolist()[:3]
                st.info(f"💡 推奨買い目: {top_3[0]} - {top_3[1]} - {top_3[2]} (実績期待値ベース)")

    with tab2:
        st.subheader("全国24場 データ比較")
        # 全会場の統計をテーブルで表示
        compare_df = pd.DataFrame.from_dict(ACTUAL_STATS, orient='index').reset_index()
        compare_df.columns = ["会場名", "展示信頼度", "展示貢献度", "イン逃げ率", "サンプル数"]
        st.dataframe(compare_df.sort_values("イン逃げ率", ascending=False), use_container_width=True, hide_index=True)

else:
    st.error("GASからのデータ取得に失敗しました。URLとデプロイ設定(アクセス権:全員)を再確認してください。")
