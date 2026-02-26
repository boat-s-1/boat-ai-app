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
        st.header("🔰 統計解析ツールの活用ガイド")
        st.write("当アプリ最大の特徴である『会場別統計解析』を使いこなすための公式マニュアルです。")

        # 1. 統計データの重要性
        st.markdown("### 📊 なぜ『補正』が必要なのか？")
        st.info("""
        競艇場のタイムは、水質（海水・淡水）、気温、気圧、そして各会場の計測位置によって大きく異なります。
        例えば、**『桐生の6.80秒』と『戸田の6.80秒』では、その価値（速さの意味）が全く違います。**
        当ツールは、過去数千レースの平均値と比較し、その『差』を自動で埋めて評価します。
        """)

        # 2. 3つの表の意味を解説
        st.markdown("### 🔍 3つの解析ステップ")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**① 公式展示タイム表**")
            st.caption("会場で発表された生のタイムです。まずはここを入力します。")
            
        with col2:
            st.markdown("**② 場平均補正タイム**")
            st.caption("その会場の平均と比較し、水面コンディションの差を排除した『真の実力値』です。")
            
        with col3:
            st.markdown("**③ 枠番補正込みタイム**")
            st.caption("インが有利なコース特性まで加味。この表で1位（赤色）なら信頼度大です。")

        # 3. 具体的な狙い目
        st.divider()
        st.markdown("### 🎯 ここを見れば勝率アップ！")
        
        with st.container(border=True):
            st.markdown("""
            **✅ 逆転現象を見つける**
            公式タイム（表1）では負けているのに、**枠番補正（表3）で1位に浮上した艇**は、数値に現れない『隠れた優出機』です。
            
            **✅ 回り足の赤色（1位）に注目**
            展示タイムよりも『回り足』の補正後タイムが1位の艇は、道中の逆転や、2マークでの粘りが期待できる実戦向きの艇です。
            
            **✅ オールマイティな艇**
            4つの項目（一周・回り足・直線・展示）のうち、3つ以上で黄色以上の色がついている艇は、軸としての安定感が抜群です。
            """)

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

