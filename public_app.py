import streamlit as st
import os

# 1. 基本設定
st.set_page_config(page_title="競艇予想Pro", layout="wide")

# --- カスタムCSS（スマホでボタンを大きく、文字を中央に） ---
st.markdown("""
    <style>
    .stButton > button {
        height: 120px !important; /* ボタンの高さを出す */
        border-radius: 12px !important;
        border: 1px solid #d1d5db !important;
        background-color: white !important;
        white-space: pre-wrap !important; /* 改行を有効にする */
        line-height: 1.5 !important;
        font-size: 16px !important;
        font-weight: bold !important;
        color: #333333 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    /* ホバー時の色変化 */
    .stButton > button:hover {
        border-color: #2563eb !important;
        background-color: #f8fafc !important;
    }
    </style>
""", unsafe_allow_html=True)

def show_main_page():
    st.title("🚤 開催一覧")
    
    # 24場の設定
    all_venues = [
        ("桐生", "pages/01_kiryu.py", "🌙 ナイター"),
        ("戸田", "pages/02_toda.py", "☀️ 昼開催"),
        ("江戸川", "pages/03_edogawa.py", "☀️ 昼開催"),
        ("平和島", "pages/04_heiwajima.py", "☀️ 昼開催"),
        ("多摩川", "pages/05_tamagawa.py", "☀️ 昼開催"),
        ("浜名湖", "pages/06_hamanako.py", "🌅 モーニング"),
        ("蒲郡", "pages/07_gamagori.py", "🌙 ナイター"),
        ("常滑", "pages/08_tokoname.py", "☀️ 昼開催"),
        ("津", "pages/09_tu.py", "☀️ 昼開催"),
        ("三国", "pages/10_mikuni.py", "🌅 モーニング"),
        ("びわこ", "pages/11_biwako.py", "☀️ 昼開催"),
        ("住之江", "pages/12_suminoe.py", "🌙 ナイター"),
        ("尼崎", "pages/13_amagasaki.py", "☀️ 昼開催"),
        ("鳴門", "pages/14_naruto.py", "🌅 モーニング"),
        ("丸亀", "pages/15_marugame.py", "🌙 ナイター"),
        ("児島", "pages/16_kojima.py", "☀️ 昼開催"),
        ("宮島", "pages/17_miyajima.py", "☀️ 昼開催"),
        ("徳山", "pages/18_tokuyama.py", "🌅 モーニング"),
        ("下関", "pages/19_simonoseki.py", "🌙 ナイター"),
        ("若松", "pages/20_wakamatu.py", "🌙 ナイター"),
        ("芦屋", "pages/21_asiya.py", "🌅 モーニング"),
        ("福岡", "pages/22_hukuoka.py", "☀️ 昼開催"),
        ("唐津", "pages/23_karatu.py", "🌅 モーニング"),
        ("大村", "pages/24_omura.py", "🌙 ナイター"),
    ]

    # スマホで見やすいように2列（または1列）で並べる
    # columns(2) にするとスマホで2つ並び、押しやすくなります
    for i in range(0, len(all_venues), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(all_venues):
                name, path, v_type = all_venues[i + j]
                with cols[j]:
                    # ボタンの中に改行 \n を入れて3段にする
                    label = f"{v_type}\n{name}\n予想データ"
                    
                    if os.path.exists(path):
                        if st.button(label, use_container_width=True, key=f"btn_{name}"):
                            st.switch_page(path)
                    else:
                        st.button(f"{v_type}\n{name}\n準備中", use_container_width=True, disabled=True)

# --- アプリ構造 ---
show_main_page()

# サイドバー
with st.sidebar:
    st.markdown("### 🏆 競艇予想Pro")
    st.caption("Premium Edition")
