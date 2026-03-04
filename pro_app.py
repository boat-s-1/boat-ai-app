import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit.components.v1 as components
import time

# ==========================================
# 1. 基本設定
# ==========================================
st.set_page_config(page_title="競艇Pro Analytica - 24場全読込版", layout="wide", page_icon="🎯")

# スプレッドシートのID（URLから抽出したもの）
# 2つのファイルに分かれているとのことですので、両方のIDを指定します
SPREADSHEET_ID_1 = "1lN794iGtyGV2jNwlYzUA8wEbhRwhPM7FxDAkMaoJss4"
SPREADSHEET_ID_2 = "1rSzJuk5Hyv60nMwX67pCufXz45HLykyIXuqVE6wtNII"

ALL_PLACES = [
    "桐生", "戸田", "江戸川", "平和島", "多摩川", "浜名湖", "蒲郡", "常滑", "津", 
    "三国", "びわこ", "住之江", "尼崎", "鳴門", "丸亀", "児島", "宮島", "徳山", 
    "下関", "若松", "芦屋", "福岡", "佐賀", "大村"
]

# ==========================================
# 2. 全シート巡回読込エンジン
# ==========================================
@st.cache_data(ttl=3600)
def load_and_analyze_all_places():
    all_stats = {}
    
    # 進行状況を表示（初回のみ）
    progress_text = "全国24場の実績データを解析中..."
    p_bar = st.sidebar.progress(0, text=progress_text)
    
    for idx, place in enumerate(ALL_PLACES):
        sheet_name = f"{place}_混合統計"
        df = pd.DataFrame()
        
        # 2つのスプレッドシートから対象のシートを探す
        for ss_id in [SPREADSHEET_ID_1, SPREADSHEET_ID_2]:
            try:
                # 特定のシート名をCSVとして取得するURL形式
                url = f"https://docs.google.com/spreadsheets/d/{ss_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
                tmp_df = pd.read_csv(url)
                if not tmp_df.empty:
                    df = tmp_df
                    break
            except:
                continue
        
        # 読み込めた場合、解析を行う
        if not df.empty:
            # 列名のクリーニング
            df.columns = df.columns.str.strip()
            # 数値変換
            df['着順_num'] = pd.to_numeric(df['着順'], errors='coerce')
            df['展示_num'] = pd.to_numeric(df['展示'], errors='coerce')
            
            # 各レース内での展示順位を算出
            df['展示順位'] = df.groupby(['日付', 'レース番号'])['展示_num'].rank(method='min')
            
            # 統計計算
            top_ex = df[df['展示順位'] == 1]
            win_rate = (top_ex['着順_num'] == 1).mean() * 100 if not top_ex.empty else 35.0
            show_rate = (top_ex['着順_num'] <= 3).mean() * 100 if not top_ex.empty else 65.0
            in_nige = (df[df['艇番'] == 1]['着順_num'] == 1).mean() * 100 if not df[df['艇番'] == 1].empty else 50.0
            
            all_stats[place] = {
                "展示信頼度": round(win_rate, 1),
                "展示貢献度": round(show_rate, 1),
                "イン逃げ率": round(in_nige, 1),
                "サンプル数": len(df)
            }
        
        # 進捗更新
        p_bar.progress((idx + 1) / len(ALL_PLACES), text=f"{place}を解析済み...")
    
    p_bar.empty()
    return all_stats

# 実績解析の実行
ACTUAL_STATS = load_and_analyze_all_places()

# ==========================================
# 3. ユーティリティ
# ==========================================
get_symbol = lambda val: {6: "◎", 5: "○", 4: "▲", 3: "△", 2: "×", 1: "・", 0: "無"}.get(val, "無")
boat_bg = {1: "#ffffff", 2: "#333333", 3: "#e03131", 4: "#1971c2", 5: "#fcc419", 6: "#2f9e44"}
boat_tx = {1: "#000000", 2: "#ffffff", 3: "#ffffff", 4: "#ffffff", 5: "#000000", 6: "#ffffff"}

# ==========================================
# 4. メイン画面
# ==========================================
with st.sidebar:
    st.header("📋 解析設定")
    # 解析に成功した会場のみリストに出す
    found_places = sorted(list(ACTUAL_STATS.keys()))
    r_place = st.selectbox("開催地を選択", found_places if found_places else ["戸田"])
    r_num = st.number_input("レース番号", 1, 12, 1)
    
    # 統計情報の表示
    p_stat = ACTUAL_STATS.get(r_place, {"展示信頼度": 35.0, "展示貢献度": 65.0, "イン逃げ率": 50.0, "サンプル数": 0})
    st.divider()
    st.metric("📊 実績イン逃げ率", f"{p_stat['イン逃げ率']}%")
    st.metric("⏱️ 展示1位の1着率", f"{p_stat['展示信頼度']}%")
    st.caption(f"分析レース数: {p_stat['サンプル数']} 件")
    
    st.write("")
    components.html('<script src="https://adm.shinobi.jp/s/00848ad75df65c15ca7f98de1efcf942"></script>', height=260)

tab1, tab2 = st.tabs(["📝 事前予想", "🔥 実績連動解析"])

with tab2:
    st.subheader(f"🏟️ {r_place} 実績反映シミュレーター")
    
    # 実績に基づく動的ウェイト
    ex_w = min(0.5, p_stat['展示信頼度'] / 100 + 0.1)
    other_w = (1.0 - ex_w) / 3
    weights = {"展示": round(ex_w, 2), "直線": round(other_w, 2), "回り足": round(other_w, 2), "一周": round(other_w, 2)}

    st.plotly_chart(px.pie(values=list(weights.values()), names=list(weights.keys()), hole=0.4, title="この会場の配点バランス"), use_container_width=True)

    with st.form("live_analysis"):
        results = []
        cols = st.columns(2)
        for i in range(1, 7):
            with cols[(i-1)%2]:
                with st.expander(f"{i}号艇の気配入力", expanded=(i==1)):
                    st.markdown(f'<div style="background:{boat_bg[i]}; color:{boat_tx[i]}; padding:5px; border-radius:4px; text-align:center; font-weight:bold;">{i}号艇</div>', unsafe_allow_html=True)
                    f1 = st.select_slider(f"展示_{i}", range(7), 0, get_symbol, key=f"ex_{i}")
                    f2 = st.select_slider(f"直線_{i}", range(7), 0, get_symbol, key=f"st_{i}")
                    f3 = st.select_slider(f"回り足_{i}", range(7), 0, get_symbol, key=f"tu_{i}")
                    f4 = st.select_slider(f"一周_{i}", range(7), 0, get_symbol, key=f"lp_{i}")
                    score = (f1*weights["展示"] + f2*weights["直線"] + f3*weights["回り足"] + f4*weights["一周"])
                    results.append({"艇番": i, "score": score, "展示": get_symbol(f1)})

        if st.form_submit_button("🔥 実績に基づいた最終解析", use_container_width=True, type="primary"):
            df = pd.DataFrame(results).sort_values("score", ascending=False)
            df["期待値"] = (df["score"] / df["score"].sum() * 100).round(1) if df["score"].sum() > 0 else 0
            st.success(f"🥇 推奨：{df.iloc[0]['艇番']}号艇（展示1位の3連対率: {p_stat['展示貢献度']}%）")
            st.dataframe(df[["艇番", "期待値", "展示"]], use_container_width=True, hide_index=True)
