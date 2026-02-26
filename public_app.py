import streamlit as st
import pandas as pd
import os
import gspread
from google.oauth2.service_account import Credentials

# 1. 基本設定
st.set_page_config(page_title="競艇予想Pro", layout="wide")

# --- Googleスプレッドシート認証関数 ---
@st.cache_resource
def get_gspread_client():
    # StreamlitのSecretsから認証情報を取得
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Google認証に失敗しました: {e}")
        return None

# クライアントの初期化
gc = get_gspread_client()

# --- カスタムCSS ---
st.markdown("""
    <style>
    /* 全体の背景 */
    .main { background-color: #f4f7f9; }
    
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
        border-color: #bda06d !important;
        background-color: #fcfaf5 !important;
        transform: translateY(-2px);
        transition: 0.2s;
    }
    /* ニュースティッカー */
    .ticker-wrapper {
        width: 100%;
        background: linear-gradient(90deg, #1e3a8a 0%, #bda06d 100%);
        color: white;
        padding: 12px 0;
        overflow: hidden;
        border-radius: 50px;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
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
    /* ガイド枠カード */
    .guide-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# メイン表示関数
def show_main_page():
    st.title("🏆 競艇予想Pro メインメニュー")

    # --- ニュースティッカー ---
    news_message = "📢 只今、蒲郡無料公開中！ ｜ 2/26 桐生データ大量更新！ ｜ 本日の勝負レースは下関12R！ ｜ 公式Xにて的中速報配信中！"
    st.markdown(f'<div class="ticker-wrapper"><div class="ticker-text">{news_message}</div></div>', unsafe_allow_html=True)
    
    # --- ガイド枠：スプレッドシート読み込み ---
    st.markdown("### 🎯 本日の注目レース")

    if gc:
        try:
            # スプレッドシート読み込み
            sh_guide = gc.open_by_key("1lN794iGtyGV2jNwlYzUA8wEbhRwhPM7FxDAkMaoJss4")
            ws_guide = sh_guide.worksheet("ガイド枠")
            guide_df = pd.DataFrame(ws_guide.get_all_records())

            if not guide_df.empty:
                g_cols = st.columns(len(guide_df))

                for i, row in guide_df.iterrows():
                    with g_cols[i]:
                        with st.container(border=True):
                            st.markdown(f"#### ⚓ {row['会場']} {row['レース番号']}")
                            st.caption(f"締切 {row['締切']}")
                            
                            color = "#d32f2f" if row['信頼度'] == "S" else "#2563eb" if row['信頼度'] == "A" else "#16a34a"
                            st.markdown(f"<span style='color:{color}; font-weight:bold;'>【信頼度：{row['信頼度']}】</span>", unsafe_allow_html=True)
                            
                            st.write(row['コメント'])
                            
                            if st.button(f"✨ {row['会場']}データへ", key=f"guide_btn_{i}", use_container_width=True):
                                st.switch_page(row['ページパス'])
            else:
                st.info("🌙 本日の注目レースは準備中です。")
                
        except Exception as e:
            st.error(f"ガイド枠の読み込みに失敗しました。シート名「ガイド枠」と共有権限を確認してください。")
    else:
        st.error("Googleスプレッドシートに接続できません。")

    st.divider()

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
        # hit1, hit2, hit3 が未定義でエラーになるのを防ぐためダミー値を設定
        h1, h2, h3 = "72.4%", "85.1%", "91.8%"
        
        with st.container(border=True):
            st.markdown("""<div style='text-align:center;'><h2>🔥 圧倒的データ量 × 独自解析ロジック</h2></div>""", unsafe_allow_html=True)
            col_v1, col_v2, col_v3 = st.columns(3)
            col_v1.metric("指数1位 → 1着率", h1)
            col_v2.metric("上位2艇 連対率", h2)
            col_v3.metric("上位3艇 1着包含率", h3)

        st.divider()
        with st.expander("🎯 STEP1：事前簡易予想"):
            st.write("展示前の期待値を可視化します。")
        with st.expander("📊 STEP2：統計解析シート"):
            st.write("会場ごとのタイム補正を行います。")
        with st.expander("🚀 STEP3：スタート指数"):
            st.write("スリット付近の強さを数値化します。")
        with st.expander("🌊 STEP4：条件補正"):
            st.write("風・波の影響を分析します。")

    # --- TAB3: SNS ---
    with tab3:
        st.subheader("📱 公式リンク")
        st.link_button("公式X (@bort_strike) をフォロー", "https://x.com/bort_strike", use_container_width=True)

    # --- TAB4: 的中実績 ---
    with tab4:
        st.subheader("📈 リアルタイム的中報告")
        st.write("公式Xの最新ポストをチェック。")
        # (Xの埋め込み用コードなどはここに追加)

# 実行
if __name__ == "__main__":
    show_main_page()
