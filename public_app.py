import streamlit as st
import pandas as pd
import os
import gspread
from google.oauth2.service_account import Credentials

# --- 1. ページ初期設定 ---
st.set_page_config(page_title="競艇予想Pro - Premium", layout="wide")

# Google Sheets 認証用関数
@st.cache_resource
def get_gspread_client():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        return gspread.authorize(creds)
    except Exception:
        return None

# クライアントの初期化
gc = get_gspread_client()

# --- 2. 会場リスト（ナビゲーションとボタン共通） ---
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

# --- 3. メインページの表示関数 ---
def show_main_page():
    # 高級感CSS
    st.markdown("""
        <style>
        .main { background-color: #f4f7f9; }
        h1 { color: #1e293b; border-left: 8px solid #bda06d; padding-left: 15px; margin-bottom: 25px; }
        .ticker-wrapper {
            width: 100%; background: linear-gradient(90deg, #1e3a8a 0%, #bda06d 100%);
            color: white; padding: 12px 0; overflow: hidden; border-radius: 50px; margin-bottom: 25px;
        }
        .ticker-text { display: inline-block; white-space: nowrap; padding-left: 100%; font-weight: bold; animation: ticker 25s linear infinite; }
        @keyframes ticker { 0% { transform: translateX(0); } 100% { transform: translateX(-100%); } }
        .guide-card { background: white; border-radius: 15px; padding: 20px; border: 1px solid #e2e8f0; box-shadow: 0 10px 25px rgba(0,0,0,0.05); }
        </style>
    """, unsafe_allow_html=True)

    st.title("🏆 競艇予想Pro メインメニュー")

    # ニュースティッカー
    st.markdown('<div class="ticker-wrapper"><div class="ticker-text">📢 只今、蒲郡無料公開中！ ｜ 2/26 桐生データ大量更新！ ｜ 本日の勝負レースは下関12R！ ｜ 公式Xにて的中速報配信中！</div></div>', unsafe_allow_html=True)

    # ガイド枠（スプレッドシート連動）
    st.markdown("### 💎 本日のプレミアム・ガイド")
    if gc:
        try:
            sh = gc.open_by_key("1lN794iGtyGV2jNwlYzUA8wEbhRwhPM7FxDAkMaoJss4")
            ws_guide = sh.worksheet("ガイド枠")
            guide_df = pd.DataFrame(ws_guide.get_all_records())
            if not guide_df.empty:
                g_cols = st.columns(len(guide_df))
                for i, row in guide_df.iterrows():
                    with g_cols[i]:
                        with st.container(border=True):
                            color = "#ef4444" if row['信頼度'] == "S" else "#3b82f6" if row['信頼度'] == "A" else "#10b981"
                            st.markdown(f"#### ⚓ {row['会場']} {row['レース番号']}")
                            st.markdown(f"<span style='color:{color}; font-weight:bold;'>【信頼度：{row['信頼度']}】</span>", unsafe_allow_html=True)
                            st.write(row['コメント'])
                            if st.button(f"✨ {row['会場']}データへ", key=f"guide_btn_{i}", use_container_width=True):
                                st.switch_page(row['ページパス'])
            else:
                st.info("🌙 現在、次節のデータを精査中です。")
        except Exception:
            st.error("ガイド枠の読み込みに失敗しました。")

    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs(["🚩 開催一覧", "🔰 使い方", "📱 公式SNS", "📈 的中実績"])

    with tab1:
        for i in range(0, len(all_venues), 4):
            cols = st.columns(4)
            for j in range(4):
                if i + j < len(all_venues):
                    name, path, v_type = all_venues[i + j]
                    with cols[j]:
                        if os.path.exists(path):
                            if st.button(f"{v_type}\n【{name}】\n予想データ", use_container_width=True, key=f"btn_{name}"):
                                st.switch_page(path)
                        else:
                            st.button(f"{v_type}\n【{name}】\n未作成", use_container_width=True, disabled=True)

    with tab2:
        st.header("📖 攻略マニュアル")
        st.write("各解析ツールの使い方を学び、的中率を最大化しましょう。")
        # 以前の使い方コンテンツをここに配置

    with tab3:
        st.subheader("📱 公式リンク")
        st.link_button("公式X (@bort_strike) をフォロー", "https://x.com/bort_strike", use_container_width=True)

# --- 4. ナビゲーションの設定 ---
home_page = st.Page(show_main_page, title="ホーム", icon="🏠", default=True)

venue_pages = []
for name, path, v_type in all_venues:
    if os.path.exists(path):
        venue_pages.append(st.Page(path, title=name, icon="🚤"))

# ナビゲーションの実行（サイドバーに会場一覧を表示）
pg = st.navigation({
    "メインメニュー": [home_page],
    "会場別データ": venue_pages
})

if __name__ == "__main__":
    pg.run()
