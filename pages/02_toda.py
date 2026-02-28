import streamlit as st
import pandas as pd
import os
import gspread  # ← これを追加！
import base64   # (もし画像表示を使うならこれも必要)

# ==============================
# 1. 会場名の固定定義
# ==============================
# 基準となるディレクトリ（フォルダ）の場所を定義
import pathlib
BASE_DIR = pathlib.Path(__file__).parent.parent.resolve()
# 変数を「戸田」に固定します
PLACE_NAME = "戸田"
st.session_state["selected_place"] = PLACE_NAME 

# ページ設定
st.set_page_config(page_title=f"競艇Pro {PLACE_NAME}", layout="wide")

# ==============================
# 2. メインUI
# ======================================
# 1. ページタイトル
# ======================================
st.title(f"🚀 {PLACE_NAME} 解析システム")

# ======================================
# 2. Google接続準備 (gcの定義をここで行う)
# ======================================
from google.oauth2.service_account import Credentials
import gspread

scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

try:
    # secrets から認証情報を取得して gc を作成
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
    gc = gspread.authorize(creds)
except Exception as e:
    st.error(f"Google接続設定エラー: {e}")
    st.stop()

# ======================================
# 3. データ管理エリア（認証が終わったので gc が使えます）
# ======================================
with st.container(border=True): 
    c1, c2, c3 = st.columns([1.5, 2, 2])
    
    with c1:
        race_type_val = st.radio(
            "解析対象を選択", ["混合", "女子"], 
            horizontal=True, key="top_race_type"
        )
    
    with c2:
        target_sheet = f"{PLACE_NAME}_{race_type_val}統計"
        if st.button(f"🔄 {target_sheet} を読み込む", use_container_width=True, key="top_load_btn"):
            with st.spinner("データ取得中..."):
                try:
                    # ここで gc を使用
                    sh = gc.open_by_key("1lN794iGtyGV2jNwlYzUA8wEbhRwhPM7FxDAkMaoJss4")
                    ws = sh.worksheet(target_sheet)
                    data = ws.get_all_records()
                    
                    if data:
                        df = pd.DataFrame(data)
                        # 数値型への変換（念のためここで一括処理）
                        num_cols = ["展示", "直線", "一周", "回り足", "艇番", "ST", "着順"]
                        for c in num_cols:
                            if c in df.columns:
                                df[c] = pd.to_numeric(df[c], errors="coerce")
                        
                        st.session_state["tab2_base_df"] = df
                        st.toast(f"✅ {target_sheet} を適用しました")
                    else:
                        st.error("シートにデータがありません")
                except Exception as e:
                    st.error(f"読込失敗: {e}")

    with c3:
        if "tab2_base_df" in st.session_state:
            count = len(st.session_state["tab2_base_df"])
            st.success(f"適用中: {target_sheet} ({count}件)")
        else:
            st.warning("⚠️ データ未読込です")

st.divider()
# ======================================
# 3. タブの定義
# ======================================
tab_pre, tab_stat, tab_start, tab_mix_check = st.tabs([
    "🎯 事前簡易予想", 
    "📊 統計解析", 
    "🚀 スタート予想", 
    "📝 スタート指数"
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

    # 1. Google 接続準備（gcの定義） --------------------------------------
    from google.oauth2.service_account import Credentials
    import gspread

    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    
    try:
        # secrets から認証情報を取得
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
        gc = gspread.authorize(creds)
    except Exception as e:
        st.error(f"Google接続エラー: {e}")
        st.stop()
    # --------------------------------------------------------------------

 
    # --- 以降、計算処理 ---
    place_df = st.session_state["tab2_base_df"].copy()

    try:
        place_mean = place_df.groupby("艇番")[["展示", "直線", "一周", "回り足"]].mean()
        overall_mean = place_df[["展示", "直線", "一周", "回り足"]].mean()
        lane_bias = place_mean - overall_mean
        race_count = len(place_df) // 6
        st.caption(f"📊 {PLACE_NAME} ({race_type_val}) 過去約 {race_count} レースより算出")
    except Exception as e:
        st.error(f"計算エラー: シートの列名（展示/直線/一周/回り足）を確認してください。\n{e}")
        st.stop()

    st.divider()
    st.markdown("### 📝 展示タイム入力（当日）")

    # 入力フォーム
    with st.form("toda_input_form_new"):
        input_rows = []
        h = st.columns([1, 2, 2, 2, 2])
        h[0].write("艇番")
        h[1].write("一周")
        h[2].write("回り足")
        h[3].write("直線")
        h[4].write("展示")

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

    # 結果表示
    if "tab2_input_df" in st.session_state:
        input_df = st.session_state["tab2_input_df"]

        def highlight_rank(df):
            def color_col(s):
                s2 = pd.to_numeric(s, errors="coerce")
                rank = s2.rank(method="min")
                return ["background-color:#ff6b6b;color:white;" if r == 1 else "background-color:#ffd43b;" if r == 2 else "" for r in rank]
            return df.style.apply(color_col, axis=0).format("{:.2f}")

        st.markdown("#### ① 公式展示タイム表（入力値）")
        st.dataframe(highlight_rank(input_df), use_container_width=True)

        adj_df = input_df.copy()
        final_df = input_df.copy()
        
        for b in range(1, 7):
            if b in place_mean.index:
                for col in ["展示", "直線", "一周", "回り足"]:
                    if pd.notna(input_df.loc[b, col]):
                        adj_val = input_df.loc[b, col] - place_mean.loc[b, col] + overall_mean[col]
                        adj_df.loc[b, col] = adj_val
                        final_df.loc[b, col] = adj_val - lane_bias.loc[b, col]

        st.markdown("#### ② 場平均補正")
        st.dataframe(highlight_rank(adj_df), use_container_width=True)

        st.markdown("#### ③ 枠番補正込み（最終評価）")
        st.dataframe(highlight_rank(final_df), use_container_width=True)

# --- タブ3：スタート予想 ---
with tab_start:
    st.subheader(f"🚀 スタート予想（{PLACE_NAME} {race_type_val}戦）")

    # 1. データの確認
    if "tab2_base_df" not in st.session_state:
        st.warning("「統計解析」タブでデータを読み込んでください。")
        st.stop()
    
    place_df = st.session_state["tab2_base_df"]
    mean_tenji = place_df["展示"].mean()
    mean_isshu = place_df["一周"].mean()

    st.caption(f"📊 {PLACE_NAME}平均との比較で算出（平均展示: {mean_tenji:.2f} / 平均一周: {mean_isshu:.2f}）")

    # 2. 展示・一周データの引き継ぎ（タブ2からの連動）
    # タブ2で入力があればそれを使い、無ければ 0.00 を初期値にする
    input_defaults = st.session_state.get("tab2_input_df", pd.DataFrame())

    # 3. 入力セクション
    st.markdown("### 📝 ST・評価 入力")
    input_cols = st.columns(6)

    tenji_input = {}
    isshu_input = {}
    st_input    = {}
    eval_input  = {}
    eval_list = ["", "◎", "◯", "△", "×"]

    for i in range(1, 7):
        # 初期値の取得
        def_tenji = input_defaults.loc[i, "展示"] if not input_defaults.empty else 0.0
        def_isshu = input_defaults.loc[i, "一周"] if not input_defaults.empty else 0.0

        with input_cols[i - 1]:
            st.markdown(f"**{i}号艇**")
            tenji_input[i] = st.number_input("展示", value=float(def_tenji), step=0.01, format="%.2f", key=f"st_ten_{i}")
            isshu_input[i] = st.number_input("一周", value=float(def_isshu), step=0.01, format="%.2f", key=f"st_iss_{i}")
            st_input[i] = st.number_input("ST", step=0.01, format="%.2f", key=f"st_st_{i}")
            eval_input[i] = st.selectbox("評価", eval_list, key=f"st_ev_{i}")

    # 4. スコア計算
    eval_map = {"◎": 2.0, "◯": 1.0, "△": 0.5, "×": -1.0}
    rows = []
    for boat in range(1, 7):
        st_score = -st_input[boat] + eval_map.get(eval_input[boat], 0)
        tenji_diff = mean_tenji - tenji_input[boat]
        isshu_diff = mean_isshu - isshu_input[boat]

        # 指数ロジック
        total = st_score + (tenji_diff * 2.0) + (isshu_diff * 0.3)
        rows.append({
            "艇番": boat,
            "展示": tenji_input[boat],
            "一周": isshu_input[boat],
            "ST": st_input[boat],
            "評価": eval_input[boat],
            "start_score": total
        })

    result_df = pd.DataFrame(rows)

    # 5. 表の表示
    st.markdown("### 📊 スタート指数ランキング")
    st.dataframe(result_df.sort_values("start_score", ascending=False), use_container_width=True, hide_index=True)

    # 6. スリット表示（画像変換関数が必要）
    def encode_image(path):
        if os.path.exists(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        return ""

    st.markdown("### 🟦 スリット予想イメージ")
    # CSS定義（デザイン調整用）
    st.markdown("""
        <style>
        .slit-area { background: #1a1a1a; padding: 20px; border-radius: 10px; position: relative; }
        .slit-line { position: absolute; left: 150px; top: 0; bottom: 0; width: 2px; background: #ff4b4b; z-index: 10; }
        .slit-row { height: 60px; display: flex; align-items: center; border-bottom: 1px solid #333; }
        .slit-boat { display: flex; align-items: center; color: white; transition: 0.5s; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="slit-area"><div class="slit-line"></div>', unsafe_allow_html=True)
    for _, r in result_df.iterrows():
        boat_no = int(r["艇番"])
        score = float(r["start_score"])
        # 指数をスリット位置(px)に変換（調整用係数: 50）
        offset = 150 + (score * 50) 
        offset = max(10, min(500, offset)) # 画面外へのはみ出し防止

        img_path = os.path.join(BASE_DIR, "images", f"boat{boat_no}.png")
        img_base64 = encode_image(img_path)

        html = f"""
        <div class="slit-row">
            <div class="slit-boat" style="margin-left:{offset}px;">
                <img src="data:image/png;base64,{img_base64}" height="40">
                <div style="margin-left:10px; font-size:11px;">
                    <b>{boat_no}</b> {r["評価"]}<br>ST {r["ST"]:.2f}
                </div>
            </div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    # --- 検証タブ：スタート指数 精度検証 ---
with tab_mix_check:
    st.subheader(f"📊 {PLACE_NAME}｜スタート指数 精度検証")

    # 1. データの確認（タブ2で読み込んだデータを使用）
    if "tab2_base_df" not in st.session_state:
        st.info("「統計解析」タブで統計データを読み込んでから検証を開始してください。")
        st.stop()
    
    # 統計データをコピーして使用
    df = st.session_state["tab2_base_df"].copy()

    # 必須列のチェック（着順など検証に必要な列があるか）
    need_cols = ["日付", "レース番号", "艇番", "展示", "一周", "ST", "着順"]
    # 統計シートに「着順」がない場合を想定したガード
    if "着順" not in df.columns:
        st.error("統計シートに『着順』列がないため、的中率を計算できません。シートを確認してください。")
        st.stop()

    # 型変換
    for c in ["艇番", "展示", "一周", "ST", "着順"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # 2. スタート指数の再計算ロジック
    # (※評価データが統計シートにある場合のみ加味。ない場合は0として計算)
    eval_col = "スタート評価" if "スタート評価" in df.columns else "評価"
    eval_map = {"◎": 2.0, "◯": 1.0, "△": 0.5, "×": -1.0}
    
    if eval_col in df.columns:
        df["評価補正"] = df[eval_col].map(eval_map).fillna(0)
    else:
        df["評価補正"] = 0

    # 会場平均の算出
    mean_tenji = df["展示"].mean()
    mean_isshu = df["一周"].mean()

    # 指数計算
    df["指数"] = (
        -df["ST"].fillna(0)
        + df["評価補正"]
        + (mean_tenji - df["展示"]) * 2.0
        + (mean_isshu - df["一周"]) * 0.3
    )

    # 3. レース単位で集計（的中判定）
    results = []
    # 日付とレース番号でグループ化
    for (d, r), g in df.groupby(["日付", "レース番号"]):
        if len(g) < 6: continue # 6艇揃っていないレースは除外

        # 指数上位3艇を抽出
        g_sorted = g.sort_values("指数", ascending=False)
        top1 = int(g_sorted.iloc[0]["艇番"])
        top2 = int(g_sorted.iloc[1]["艇番"])
        top3 = int(g_sorted.iloc[2]["艇番"])

        # 実際の着順を取得
        winner_row = g[g["着順"] == 1]
        if winner_row.empty: continue
        
        winner = int(winner_row.iloc[0]["艇番"])
        
        # 的中判定
        results.append({
            "日付": d,
            "R": r,
            "指数1位": top1,
            "指数2位": top2,
            "指数3位": top3,
            "1着艇": winner,
            "1位的中": (top1 == winner),
            "上位2艇内": (winner in [top1, top2]),
            "上位3艇内": (winner in [top1, top2, top3])
        })

    if not results:
        st.warning("検証可能なレースデータ（6艇揃っており着順があるデータ）がありません。")
        st.stop()

    res_df = pd.DataFrame(results)

    # 4. サマリー表示
    total = len(res_df)
    hit1 = res_df["1位的中"].mean() * 100
    hit2 = res_df["上位2艇内"].mean() * 100
    hit3 = res_df["上位3艇内"].mean() * 100

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("検証レース数", f"{total} R")
    c2.metric("指数1位的中率", f"{hit1:.1f}%")
    c3.metric("上位2艇 1着率", f"{hit2:.1f}%")
    c4.metric("上位3艇 1着率", f"{hit3:.1f}%")

    st.divider()

    # 5. 詳細データ表示（色付け）
    def color_hit(val):
        return 'background-color: #d4edda' if val else ''

    st.markdown("### 📋 検証詳細データ")
    st.dataframe(
        res_df.style.applymap(color_hit, subset=["1位的中", "上位2艇内", "上位3艇内"]),
        use_container_width=True,
        hide_index=True
    )
