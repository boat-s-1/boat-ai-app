import streamlit as st
import os

# 1. 基本設定
st.set_page_config(page_title="競艇予想Pro", layout="wide")

# --- カスタムCSS（カードのデザインを細かく設定） ---
st.markdown("""
    <style>
    /* 全体背景 */
    .stApp { background-color: #F3F4F6; }
    
    /* カードの枠組み */
    .venue-card {
        border-radius: 12px;
        padding: 10px;
        margin-bottom: 10px;
        border: 1px solid #E5E7EB;
        text-align: center;
        background-color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* 開催タイプ別のヘッダー色 */
    .type-nighter { color: #1E40AF; font-weight: bold; font-size: 0.8em; } /* 青 */
    .type-morning { color: #EA580C; font-weight: bold; font-size: 0.8em; } /* オレンジ */
    .type-day { color: #111827; font-weight: bold; font-size: 0.8em; }
    
    /* 会場名 */
    .venue-name { font-size: 1.2em; font-weight: bold; margin: 5px 0; color: #111827; }

    /* ボタンの透明化とカードフィット */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        border: 1px solid #D1D5DB;
        background-color: white;
        height: 40px;
    }
    </style>
""", unsafe_allow_html=True)

def draw_venue_card(name, path, venue_type):
    """
    会場ごとのカードを描画する関数
    venue_type: "🌙 ナイター", "☀️ モーニング", "昼開催"
    """
    with st.container():
        # HTMLで見た目を整える
        type_class = "type-nighter" if "ナイター" in venue_type else "type-morning" if "モーニング" in venue_type else "type-day"
        
        st.markdown(f"""
            <div class="venue-card">
                <div class="{type_class}">{venue_type}</div>
                <div class="venue-name">{name}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # カードのすぐ下にボタンを配置
        if os.path.exists(path):
            if st.button("予想データ", key=f"btn_{name}", use_container_width=True):
                st.switch_page(path)
        else:
            st.button("準備中", key=f"btn_{name}", use_container_width=True, disabled=True)

def show_main_page():
    st.title("🚤 開催一覧")
    
    # 24場の設定（会場名, パス, タイプ）
    # 実際の開催に合わせてここを書き換えるだけでデザインが変わります
    all_venues = [
        ("桐生", "pages/01_kiryu.py", "🌙 ナイター"),
        ("戸田", "pages/02_toda.py", "昼開催"),
        ("江戸川", "pages/03_edogawa.py", "昼開催"),
        ("平和島", "pages/04_heiwajima.py", "昼開催"),
        ("多摩川", "pages/05_tamagawa.py", "昼開催"),
        ("浜名湖", "pages/06_hamanako.py", "☀️ モーニング"),
        ("蒲郡", "pages/07_gamagori.py", "🌙 ナイター"),
        ("常滑", "pages/08_tokoname.py", "昼開催"),
        ("津", "pages/09_tu.py", "昼開催"),
        ("三国", "pages/10_mikuni.py", "☀️ モーニング"),
        ("びわこ", "pages/11_biwako.py", "昼開催"),
        ("住之江", "pages/12_suminoe.py", "🌙 ナイター"),
        ("尼崎", "pages/13_amagasaki.py", "昼開催"),
        ("鳴門", "pages/14_naruto.py", "☀️ モーニング"),
        ("丸亀", "pages/15_marugame.py", "🌙 ナイター"),
        ("児島", "pages/16_kojima.py", "昼開催"),
        ("宮島", "pages/17_miyajima.py", "昼開催"),
        ("徳山", "pages/18_tokuyama.py", "☀️ モーニング"),
        ("下関", "pages/19_simonoseki.py", "🌙 ナイター"),
        ("若松", "pages/20_wakamatu.py", "🌙 ナイター"),
        ("芦屋", "pages/21_asiya.py", "☀️ モーニング"),
        ("福岡", "pages/22_hukuoka.py", "昼開催"),
        ("唐津", "pages/23_karatu.py", "☀️ モーニング"),
        ("大村", "pages/24_omura.py", "🌙 ナイター"),
    ]

    # 4列で表示
    for i in range(0, len(all_venues), 4):
        cols = st.columns(4)
        for j in range(4):
            if i + j < len(all_venues):
                name, path, v_type = all_venues[i + j]
                with cols[j]:
                    draw_venue_card(name, path, v_type)

# --- アプリ構造 ---
tab1, tab2 = st.tabs(["🚩 開催一覧", "⭐ お気に入り"])

with tab1:
    show_main_page()

# サイドバー
with st.sidebar:
    st.markdown("### 🏆 競艇予想Pro")
    st.caption("Premium Edition")
