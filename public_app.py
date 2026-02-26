import streamlit as st
import os

# 1. 基本設定
st.set_page_config(page_title="競艇Pro", layout="wide")

# --- メイン画面の処理（ホーム画面） ---
def show_main_page():
    st.title("🏁 会場を選択")
    
    # 全24会場のリスト
    all_venues = [
        ("桐生01", "pages/01_kiryu.py"), ("戸田02", "pages/02_toda.py"), ("江戸川03", "pages/03_edogawa.py"), ("平和島04", "pages/04_heiwajima.py"),
        ("多摩川05", "pages/05_tamagawa.py"), ("浜名湖06", "pages/06_hamanako.py"), ("蒲郡07", "pages/07_gamagori.py"), ("常滑08", "pages/08_tokoname.py"),
        ("津09", "pages/09_tu.py"), ("三国10", "pages/10_mikuni.py"), ("びわこ11", "pages/11_biwako.py"), ("住之江12", "pages/12_suminoe.py"),
        ("尼崎13", "pages/13_amagasaki.py"), ("鳴門14", "pages/14_naruto.py"), ("丸亀15", "pages/15_marugame.py"), ("児島16", "pages/16_kojima.py"),
        ("宮島17", "pages/17_miyajima.py"), ("徳山18", "pages/18_tokuyama.py"), ("下関19", "pages/19_simonoseki.py"), ("若松20", "pages/20_wakamatu.py"),
        ("芦屋21", "pages/21_asiya.py"), ("福岡22", "pages/22_hukuoka.py"), ("唐津23", "pages/23_karatu.py"), ("大村24", "pages/24_omura.py")
    ]
    
    # 4列ずつ表示
    for i in range(0, len(all_venues), 4):
        cols = st.columns(4)
        for j in range(4):
            if i + j < len(all_venues):
                name, path = all_venues[i + j]
                with cols[j]:
                    if os.path.exists(path):
                        if st.button(name, use_container_width=True, key=f"main_{name}"):
                            st.switch_page(path)
                    else:
                        # ファイルがない場合はグレーのボタンで表示
                        st.button(f"未作成:{name}", disabled=True, use_container_width=True, key=f"main_{name}")

# --- ページ登録用の関数（ファイルチェック付き） ---
def safe_page(path, title, icon="🚤"):
    if os.path.exists(path):
        return st.Page(path, title=title, icon=icon)
    return None

# 各エリアのページ定義
home = st.Page(show_main_page, title="ホーム", icon="🏠", default=True)

# 関東
kanto = [
    safe_page("pages/01_kiryu.py", "桐生"), safe_page("pages/02_toda.py", "戸田"),
    safe_page("pages/03_edogawa.py", "江戸川"), safe_page("pages/04_heiwajima.py", "平和島"),
    safe_page("pages/05_tamagawa.py", "多摩川")
]
# 東海
tokai = [
    safe_page("pages/06_hamanako.py", "浜名湖"), safe_page("pages/07_gamagori.py", "蒲郡", icon="🏁"),
    safe_page("pages/08_tokoname.py", "常滑"), safe_page("pages/09_tu.py", "津")
]
# 近畿・北陸
kinki = [
    safe_page("pages/10_mikuni.py", "三国"), safe_page("pages/11_biwako.py", "びわこ"),
    safe_page("pages/12_suminoe.py", "住之江"), safe_page("pages/13_amagasaki.py", "尼崎")
]
# 中国・四国
chugoku_shikoku = [
    safe_page("pages/14_naruto.py", "鳴門"), safe_page("pages/15_marugame.py", "丸亀"),
    safe_page("pages/16_kojima.py", "児島"), safe_page("pages/17_miyajima.py", "宮島"),
    safe_page("pages/18_tokuyama.py", "徳山"), safe_page("pages/19_simonoseki.py", "下関")
]
# 九州
kyushu = [
    safe_page("pages/20_wakamatu.py", "若松"), safe_page("pages/21_asiya.py", "芦屋"),
    safe_page("pages/22_hukuoka.py", "福岡"), safe_page("pages/23_karatu.py", "唐津"),
    safe_page("pages/24_omura.py", "大村")
]

# --- ナビゲーション構築 ---
nav_dict = {"メイン": [home]}

# Noneを除外して、エリアにページがある場合だけサイドバーに追加
def add_section(name, pages):
    valid_pages = [p for p in pages if p is not None]
    if valid_pages:
        nav_dict[name] = valid_pages

add_section("関東地区", kanto)
add_section("東海地区", tokai)
add_section("北陸・近畿地区", kinki)
add_section("中国・四国地区", chugoku_shikoku)
add_section("九州地区", kyushu)

pg = st.navigation(nav_dict)

# 共通のサイドバー表示
with st.sidebar:
    st.markdown("### 🏆 競艇予想Pro")
    st.divider()

pg.run()
