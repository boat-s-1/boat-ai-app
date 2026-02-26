import streamlit as st
import os

# 1. 基本設定
st.set_page_config(page_title="競艇予想Pro", layout="wide")

# --- カスタムCSS（公式アプリの雰囲気に寄せる） ---
st.markdown("""
    <style>
    /* ボタン全体のスタイル */
    .stButton > button {
        height: 120px !important;
        border-radius: 12px !important;
        border: 1px solid #e5e7eb !important;
        background-color: #ffffff !important;
        color: #374151 !important;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        white-space: pre-wrap !important; /* 改行を有効にする */
        line-height: 1.4 !important;
        font-size: 14px !important;
    }
    /* ホバー時の挙動 */
    .stButton > button:hover {
        border-color: #3b82f6 !important;
        background-color: #f8fafc !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    /* タブのスタイル調整 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- メインコンテンツを表示する関数 ---
def show_venue_grid():
    # 会場データ（表示名, パス, ステータス絵文字, クラス, 日数, 時刻）
    # 有料版ではここを自動取得(スクレイピング)にするのが理想です
    venues = [
        ("桐生01", "pages/01_kiryu.py", "🌙", "一般", "3日目", "1R 15:23"),
        ("戸田02", "pages/02_toda.py", "☀️", "一般", "2日目", "1R 10:47"),
        ("江戸川03", "pages/03_edogawa.py", "", "非開催", "--", "--"),
        ("平和島04", "pages/04_heiwajima.py", "☀️", "一般", "最終日", "1R 10:57"),
        ("多摩川05", "pages/05_tamagawa.py", "🌅", "一般", "5日目", "1R 11:09"),
        ("浜名湖06", "pages/06_hamanako.py", "", "非開催", "--", "--"),
        ("蒲郡07", "pages/07_gamagori.py", "", "非開催", "--", "--"),
        ("常滑08", "pages/08_tokoname.py", "☀️", "一般", "初日", "1R 10:18"),
        # 必要に応じて24場分追加
    ]

    # 4列のグリッド表示
    for i in range(0, len(venues), 4):
        cols = st.columns(4)
        for j in range(4):
            if i + j < len(venues):
                name, path, icon, grade, day, time = venues[i + j]
                with cols[j]:
                    if grade == "非開催":
                        # 非開催のデザイン
                        label = f"\n{name}\n\nー ー"
                        st.button(label, use_container_width=True, disabled=True, key=f"dead_{name}")
                    else:
                        # 開催中のデザイン（改行を使って情報を配置）
                        label = f"{icon}  {name}\n{grade}  {day}\n{time}"
                        if os.path.exists(path):
                            if st.button(label, use_container_width=True, key=f"live_{name}"):
                                st.switch_page(path)
                        else:
                            st.button(f"{name}\n準備中", disabled=True, use_container_width=True)

# --- アプリ構成 ---
st.image("https://img.icons8.com/color/96/speed-boat.png", width=50) # ロゴ代わり
st.title("トップ")

# 画像にあった上部メニュー（タブ）
tab1, tab2, tab3, tab4 = st.tabs(["🚩 開催一覧", "⏰ 締切順", "⭐ お気に入り", "📽️ レース映像"])

with tab1:
    show_venue_grid()
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 開催情報更新", use_container_width=True):
        st.toast("情報を更新しました")
        st.rerun()

with tab2:
    st.write("締切が近い順に表示されます（開発中）")

with tab3:
    st.write("お気に入りの会場が表示されます（開発中）")

# サイドバー設定
with st.sidebar:
    st.markdown("## 🏆 競艇予想Pro")
    st.caption("v1.0.0 有料配布版")
    st.divider()
    st.info("ライセンス有効期限:\n2026年12月31日まで")
