import streamlit as st
import streamlit.components.v1 as components
import os

# 1. 基本設定
st.set_page_config(page_title="競艇予想Pro", layout="wide")

# --- カスタムCSS ---
st.markdown("""
    <style>
    /* トップボタンのデザイン */
    div.top-button > div.stButton > button {
        height: 140px !important; 
        border-radius: 12px !important;
        border: 1px solid #d1d5db !important;
        background-color: white !important;
        white-space: pre-wrap !important; 
        line-height: 1.4 !important;
        font-size: 15px !important;
        color: #333333 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    div.top-button > div.stButton > button:hover {
        border-color: #2563eb !important;
        background-color: #f8fafc !important;
        transform: translateY(-2px);
        transition: 0.2s;
    }
    /* ニュースティッカー */
    .ticker-wrapper {
        width: 100%;
        background-color: #1e3a8a;
        color: white;
        padding: 10px 0;
        overflow: hidden;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    .ticker-text {
        display: inline-block;
        white-space: nowrap;
        padding-left: 100%;
        font-weight: bold;
        animation: ticker 25s linear infinite;
    }
    @keyframes ticker {
        0% { transform: translateX(0); }
        100% { transform: translateX(-100%); }
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 18px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

def show_main_page():
    st.title("🏆 競艇予想Pro メインメニュー")

    # --- ニュースティッカー ---
    news_message = "📢 只今、蒲郡無料公開中！ ｜ 2/26 桐生データ大量更新！ ｜ 本日の勝負レースは下関12R！ ｜ 公式Xにて的中速報配信中！"
    st.markdown(f'<div class="ticker-wrapper"><div class="ticker-text">{news_message}</div></div>', unsafe_allow_html=True)

    # --- タブメニュー ---
    tab1, tab2, tab3, tab4 = st.tabs(["🚩 開催一覧", "🔰 使い方", "📱 公式SNS", "📈 的中実績"])

    # --- TAB1: 開催一覧 ---
    with tab1:
        all_venues = [
            ("桐生", "pages/01_kiryu.py", "🌙ナイター"), ("戸田", "pages/02_toda.py", "☀️昼開催"),
            ("江戸川", "pages/03_edogawa.py", "☀️昼開催"), ("平和島", "pages/04_heiwajima.py", "☀️昼開催"),
            ("多摩川", "pages/05_tamagawa.py", "☀️昼開催"), ("浜名湖", "pages/06_hamanako.py", "🌅モーニング"),
            ("蒲郡", "pages/07_gamagori.py", "🌙ナイター"), ("常滑", "pages/08_tokoname.py", "☀️昼開催"),
            ("津", "pages/09_tu.py", "☀️昼開催"), ("三国", "pages/10_mikuni.py", "🌅モーニング"),
            ("びわこ", "pages/11_biwako.py", "☀️昼開催"), ("住之江", "pages/12_suminoe.py", "🌙ナイター"),
            ("尼崎", "pages/13_amagasaki.py", "☀️昼開催"), ("鳴門", "pages/14_naruto.py", "🌅モーニング"),
            ("丸亀", "pages/15_marugame.py", "🌙ナイター"), ("児島", "pages/16_kojima.py", "☀️昼開催"),
            ("宮島", "pages/17_miyajima.py", "☀️昼開催"), ("徳山", "pages/18_tokuyama.py", "🌅モーニング"),
            ("下関", "pages/19_simonoseki.py", "🌙ナイター"), ("若松", "pages/20_wakamatu.py", "🌙ナイター"),
            ("芦屋", "pages/21_asiya.py", "🌅モーニング"), ("福岡", "pages/22_hukuoka.py", "☀️昼開催"),
            ("唐津", "pages/23_karatu.py", "🌅モーニング"), ("大村", "pages/24_omura.py", "🌙ナイター"),
        ]
        for i in range(0, len(all_venues), 4):
            cols = st.columns(4)
            for j in range(4):
                if i + j < len(all_venues):
                    name, path, v_type = all_venues[i + j]
                    with cols[j]:
                        label = f"{v_type}\n【{name}】\n予想データ"
                        st.markdown('<div class="top-button">', unsafe_allow_html=True)
                        if os.path.exists(path):
                            if st.button(label, use_container_width=True, key=f"btn_{name}"):
                                st.switch_page(path)
                        else:
                            st.button(f"{v_type}\n【{name}】\n未作成", use_container_width=True, disabled=True)
                        st.markdown('</div>', unsafe_allow_html=True)

           # --- TAB2: 使い方 ---
    with tab2:
        st.header("📖 競艇予想Pro 攻略マニュアル")
        st.write("3つの強力な解析ツールを使いこなし、勝利への期待値を最大化しましょう。")

        # --- ステップ1: 事前簡易予想 ---
        with st.expander("🎯 STEP1：事前簡易予想（地力の把握）", expanded=False):
            st.markdown("""
            **展示航走の前に、出走表のデータから「期待値」を可視化します。**
            
            * **入力項目**: モーター、当地勝率、枠番勝率、枠番スタート(ST)の4つ。
            * **評価基準**: 独自の重み付け（枠番勝率30%、モーター25%など）を行い、全6艇の勝機を100%に配分します。
            * **狙い目**: 1位の％が圧倒的に高い（25%以上）場合は、鉄板の軸。横並びの場合は高配当のチャンスです。
            """)

        # --- ステップ2: 統計解析 ---
        with st.expander("📊 STEP2：統計解析シート（タイム補正）", expanded=False):
            st.markdown("""
            **会場ごとのクセを排除し、真の「足の良さ」を導き出します。**
            
            * **3つの表の意味**:
                1. **公式展示タイム**: 入力された生のデータ。
                2. **場平均補正**: 「桐生の6.80秒」と「戸田の6.80秒」の価値を統一。
                3. **枠番補正込み**: コース有利を差し引いた、純粋な機力の差。
            * **狙い目**: 表1（公式）では平凡なのに、表3（枠番補正）で上位に浮上する艇は、**「隠れた実力艇」**です。
            """)

        # --- ステップ3: スタート予想 ---
        with st.expander("🚀 STEP3：スタート指数（スリット攻防）", expanded=False):
            st.markdown("""
            **「ST」「展示」「一周」の3要素に「目視評価」を加え、スタート付近の強さを数値化。**
            
            * **会場別補正**: 過去データ平均との差から、その日のスリット付近の「伸び」を解析します。
            * **目視評価の活用**:
                - **◎**: スリットから明らかに出ている
                - **×**: 届いていない、または行き足に不安
            * **スタート指数(start_score)**:
                数値が高いほど、1マークで先手を取れる確率がアップ。**「STEP1の1位」と「STEP3の指数1位」が一致すれば、まさに鬼に金棒です。**
            """)

        st.divider()
 # --- ステップ4: 条件補正 ---
        with st.expander("🌊 STEP4：条件補正（水面状況の分析）", expanded=False):
            st.markdown("""
            **「風・波」がタイムに与える影響を解析し、荒れる条件を特定します。**
            
            * **主な設定項目**: 会場、風向き、風速、波高の4つを、今の水面状況に合わせてスライダーで調整。
            * **艇番別・平均タイム**:
                その特定の条件下において、過去に各コースが「平均どれくらいのタイムで走れていたか」を表示します。
            * **条件平均との差（補正の正体）**:
                全体の平均からどれほどズレているかを算出。**数値がマイナスに大きいほど、その条件において「そのコースが本来の実力以上に速く走れる」**ことを示しています。
                
            **💡 活用のコツ:**
            「追い風5m・波高5cm」など、荒れた条件を入力してみましょう。特定のコースの数値が極端に良くなっていれば、そこが**「高配当の使者」**になる可能性大です！
            """)

        st.divider()
        # --- (以前のフローチャートへ続く) ---
        # --- 全体の活用チャート（これがあると親切！） ---
        st.markdown("### 🏆 勝利への勝利へのフローチャート")
        st.info("""
        1️⃣ **朝一〜直前まで**: **STEP1**でレースの「格」をチェック。
        2️⃣ **展示航走後**: **STEP2**で「回り足」「伸び」を補正。
        3️⃣ **スタート特訓後**: **STEP3**で「スリット攻防」を確信。
        👉 全ての指数が揃ったときが、最大の勝負どころです！
        """)

        st.link_button("最新の的中報告をチェック（公式X）", "https://x.com/bort_strike", use_container_width=True)
    # --- TAB3: SNS ---
    with tab3:
        st.subheader("📱 公式リンク")
        st.link_button("公式X (@bort_strike) をフォロー", "https://x.com/bort_strike", use_container_width=True)
        st.info("※最新の予想配信や、ツールのアップデート情報をお届けします。")

    # --- TAB4: 的中実績 (Xタイムライン埋め込み) ---
    with tab4:
        st.subheader("📈 リアルタイム的中報告")
        st.write("公式Xでの最新ポストを表示しています。")
        
        # X(Twitter)の埋め込みHTML
        twitter_html = """
        <a class="twitter-timeline" 
           data-height="800" 
           data-theme="light" 
           href="https://twitter.com/bort_strike?ref_src=twsrc%5Etfw">
           Tweets by bort_strike
        </a> 
        <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
        """
        # HTMLコンポーネントとして表示
        components.html(twitter_html, height=800, scrolling=True)

# --- ページ管理ロジック ---
def safe_page(path, title, icon="🚤"):
    if os.path.exists(path):
        return st.Page(path, title=title, icon=icon)
    return None

home = st.Page(show_main_page, title="ホーム", icon="🏠", default=True)

# 24場の登録
all_p = [
    safe_page(f"pages/{str(i).zfill(2)}_{n}.py", t) for i, n, t in [
        (1, "kiryu", "桐生"), (2, "toda", "戸田"), (3, "edogawa", "江戸川"), (4, "heiwajima", "平和島"),
        (5, "tamagawa", "多摩川"), (6, "hamanako", "浜名湖"), (7, "gamagori", "蒲郡"), (8, "tokoname", "常滑"),
        (9, "tu", "津"), (10, "mikuni", "三国"), (11, "biwako", "びわこ"), (12, "suminoe", "住之江"),
        (13, "amagasaki", "尼崎"), (14, "naruto", "鳴門"), (15, "marugame", "丸亀"), (16, "kojima", "児島"),
        (17, "miyajima", "宮島"), (18, "tokuyama", "徳山"), (19, "simonoseki", "下関"), (20, "wakamatu", "若松"),
        (21, "asiya", "芦屋"), (22, "hukuoka", "福岡"), (23, "karatu", "唐津"), (24, "omura", "大村")
    ]
]
valid_venue_pages = [p for p in all_p if p is not None]

pg = st.navigation({"メイン": [home], "会場一覧": valid_venue_pages})
pg.run()




