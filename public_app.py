import streamlit as st
import os

# 1. 基本設定（必ず一番上に一度だけ）
st.set_page_config(page_title="競艇予想Pro", layout="wide")

# --- カスタムCSS（デザインの調整） ---
st.markdown("""
    <style>
    /* ボタンのスタイル設定 */
    .stButton > button {
        height: 140px !important; 
        border-radius: 12px !important;
        border: 1px solid #d1d5db !important;
        background-color: white !important;
        white-space: pre-wrap !important; 
        line-height: 1.6 !important;
        font-size: 14px !important; /* 「予想データ」の文字サイズ */
        color: #333333 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    /* ボタンにマウスを乗せた時の色 */
    .stButton > button:hover {
        border-color: #2563eb !important;
        background-color: #f8fafc !important;
        transform: translateY(-2px);
        transition: 0.2s;
    }
    </style>
""", unsafe_allow_html=True)

# --- 共通関数：太字（強調）を作る ---
def to_bold(text):
    return f"【{text}】"

# --- 共通関数：ページを安全に登録する ---
def safe_page(path, title, icon="🚤"):
    if os.path.exists(path):
        return st.Page(path, title=title, icon=icon)
    return None

# --- メイン画面（ホーム）の表示内容 ---
def show_main_page():
    st.title("🏁 開催一覧")
    
    # 24会場の定義（表示名, ファイル名, 開催タイプ）
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

    # 4列配置
    for i in range(0, len(all_venues), 4):
        cols = st.columns(4)
        for j in range(4):
            if i + j < len(all_venues):
                name, path, v_type = all_venues[i + j]
                with cols[j]:
                    # 1段目と2段目を強調、3段目は通常の「予想データ」
                    label = f"{to_bold(v_type)}\n{to_bold(name)}\n予想データ"
                    
                    if os.path.exists(path):
                        if st.button(label, use_container_width=True, key=f"btn_{name}"):
                            st.switch_page(path)
                    else:
                        st.button(f"{to_bold(v_type)}\n{to_bold(name)}\n未作成", use_container_width=True, disabled=True)

# --- ページオブジェクトの生成 ---
# ホーム画面（関数をPageとして登録）
home = st.Page(show_main_page, title="ホーム", icon="🏠", default=True)

# 各会場のページ（ファイルが存在する場合のみPageオブジェクトを作る）
p01 = safe_page("pages/01_kiryu.py", "桐生")
p02 = safe_page("pages/02_toda.py", "戸田")
p03 = safe_page("pages/03_edogawa.py", "江戸川")
p04 = safe_page("pages/04_heiwajima.py", "平和島")
p05 = safe_page("pages/05_tamagawa.py", "多摩川")
p06 = safe_page("pages/06_hamanako.py", "浜名湖")
p07 = safe_page("pages/07_gamagori.py", "蒲郡", icon="🏁")
p08 = safe_page("pages/08_tokoname.py", "常滑")
p09 = safe_page("pages/09_tu.py", "津")
p10 = safe_page("pages/10_mikuni.py", "三国")
p11 = safe_page("pages/11_biwako.py", "びわこ")
p12 = safe_page("pages/12_suminoe.py", "住之江")
p13 = safe_page("pages/13_amagasaki.py", "尼崎")
p14 = safe_page("pages/14_naruto.py", "鳴門")
p15 = safe_page("pages/15_marugame.py", "丸亀")
p16 = safe_page("pages/16_kojima.py", "児島")
p17 = safe_page("pages/17_miyajima.py", "宮島")
p18 = safe_page("pages/18_tokuyama.py", "徳山")
p19 = safe_page("pages/19_simonoseki.py", "下関")
p20 = safe_page("pages/20_wakamatu.py", "若松")
p21 = safe_page("pages/21_asiya.py", "芦屋")
p22 = safe_page("pages/22_hukuoka.py", "福岡")
p23 = safe_page("pages/23_karatu.py", "唐津")
p24 = safe_page("pages/24_omura.py", "大村")

# 存在する会場だけをリスト化
all_p = [p01,p02,p03,p04,p05,p06,p07,p08,p09,p10,p11,p12,p13,p14,p15,p16,p17,p18,p19,p20,p21,p22,p23,p24]
valid_venue_pages = [p for p in all_p if p is not None]

# --- ナビゲーションの実行 ---
# 注意：valid_venue_pages をここに含めないと switch_page でエラーになります
pg = st.navigation({
    "メイン": [home],
    "会場一覧": valid_venue_pages
})

# サイドバーに共通情報を表示
with st.sidebar:
    st.markdown("### 🏆 競艇予想Pro")
    st.caption("Premium Edition v1.0")
    st.divider()

pg.run()
