import streamlit as st
import os

# 1. 基本設定
st.set_page_config(page_title="競艇予想Pro", layout="wide")

# --- カスタムCSS（ボタン装飾 + ニュースティッカー + タブの装飾） ---
st.markdown("""
    <style>
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
    /* タブの文字を少し大きくする */
    .stTabs [data-baseweb="tab"] {
        font-size: 18px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

def show_main_page():
    st.title("🏆 競艇予想Pro メインメニュー")

    # --- ニュースティッカー ---
    news_message = "📢 只今、蒲郡無料公開中！ ｜ 2/26 桐生データ大量更新！ ｜ 本日の勝負レースは下関12R！ ｜ 公式LINEにて予想配信中！"
    st.markdown(f'<div class="ticker-wrapper"><div class="ticker-text">{news_message}</div></div>', unsafe_allow_html=True)

    # --- タブメニューの作成 ---
    tab1, tab2, tab3, tab4 = st.tabs(["🚩 開催一覧", "🔰 使い方", "📱 SNS・問合せ", "📈 的中実績"])

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
        st.subheader("🔰 ツールの使い方")
        st.info("本ツールは過去10年のデータからAIが勝率を算出しています。")
        st.markdown("""
        1. **会場を選択**: 開催一覧から勝負したい会場をタップ。
        2. **指数を確認**: 1R〜12RまでのAI予想スコアを確認。
        3. **買い目を選ぶ**: 指数80以上の選手を軸にするのがおすすめです！
        """)

    # --- TAB3: SNS ---
    with tab3:
        st.subheader("📱 公式リンク")
        col_sns1, col_sns2 = st.columns(2)
        with col_sns1:
            st.link_button("公式LINEで無料予想を受け取る", "https://line.me/...", use_container_width=True)
        with col_sns2:
            st.link_button("公式X (旧Twitter) をフォロー", "https://x.com/...", use_container_width=True)

    # --- TAB4: 的中実績 ---
    with tab4:
        st.subheader("📈 最新の的中報告")
        st.success("2/25 桐生12R：3連単 1-2-4 的中！ (1,240円)")
        st.success("2/25 蒲郡8R：3連単 4-1-2 的中！ (15,400円) 🔥")

# --- ページ管理 (以前と同じ) ---
def safe_page(path, title, icon="🚤"):
    if os.path.exists(path):
        return st.Page(path, title=title, icon=icon)
    return None

home = st.Page(show_main_page, title="ホーム", icon="🏠", default=True)
# (会場ページの登録は省略：以前のコードをそのまま使ってください)
all_p = [safe_page(f"pages/{str(i).zfill(2)}_{n}.py", t) for i, n, t in [(1, "kiryu", "桐生"), (2, "toda", "戸田"), (3, "edogawa", "江戸川"), (4, "heiwajima", "平和島"), (5, "tamagawa", "多摩川"), (6, "hamanako", "浜名湖"), (7, "gamagori", "蒲郡"), (8, "tokoname", "常滑"), (9, "tu", "津"), (10, "mikuni", "三国"), (11, "biwako", "びわこ"), (12, "suminoe", "住之江"), (13, "amagasaki", "尼崎"), (14, "naruto", "鳴門"), (15, "marugame", "丸亀"), (16, "kojima", "児島"), (17, "miyajima", "宮島"), (18, "tokuyama", "徳山"), (19, "simonoseki", "下関"), (20, "wakamatu", "若松"), (21, "asiya", "芦屋"), (22, "hukuoka", "福岡"), (23, "karatu", "唐津"), (24, "omura", "大村")]]
valid_venue_pages = [p for p in all_p if p is not None]

pg = st.navigation({"メイン": [home], "会場一覧": valid_venue_pages})
pg.run()
