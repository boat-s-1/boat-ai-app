import streamlit as st
import os

st.set_page_config(page_title="競艇Pro", layout="wide")

# ファイルが存在するか確認してページを作る関数
def create_page(file_path, title, icon):
    if os.path.exists(file_path):
        return st.Page(file_path, title=title, icon=icon)
    return None

# 各ページを定義（存在しないファイルは None になる）
p01 = create_page("pages/01_kiryu.py", "桐生", "🚤")
p02 = create_page("pages/02_toda.py", "戸田", "🚤")
p03 = create_page("pages/03_edogawa.py", "江戸川", "🚤")
p04 = create_page("pages/04_heiwajima.py", "平和島", "🚤")
p07 = create_page("pages/07_gamagori.py", "蒲郡", "🏁")

# 存在するページだけをリストに入れる
main_pages = [st.Page("public_app.py", title="ホーム", icon="🏠", default=True)]
kanto_pages = [p for p in [p01, p02, p03, p04] if p is not None]
tokai_pages = [p for p in [p07] if p is not None]

# ナビゲーション作成
nav_dict = {"メイン": main_pages}
if kanto_pages: nav_dict["関東地区"] = kanto_pages
if tokai_pages: nav_dict["東海地区"] = tokai_pages

pg = st.navigation(nav_dict)
pg.run()

# --- ここから下は「ホーム画面」に表示される内容 ---
# pg.run() が home (public_app.py) を実行している時だけ表示されます
st.title("🏁 会場を選択")

# 会場ボタン（見やすく4列×6段に配置）
venue_list = [
    ("桐生01", "pages/01_kiryu.py"), ("戸田02", "pages/02_toda.py"), ("江戸川03", "pages/03_edogawa.py"), ("平和島04", "pages/04_heiwajima.py"),
    ("多摩川05", "pages/05_tamagawa.py"), ("浜名湖06", "pages/06_hamanako.py"), ("蒲郡07", "pages/07_gamagori.py"), ("常滑08", "pages/08_tokoname.py"),
    ("津09", "pages/09_tu.py"), ("三国10", "pages/10_mikuni.py"), ("びわこ11", "pages/11_biwako.py"), ("住之江12", "pages/12_suminoe.py"),
    ("尼崎13", "pages/13_amagasaki.py"), ("鳴門14", "pages/14_naruto.py"), ("丸亀15", "pages/15_marugame.py"), ("児島16", "pages/16_kojima.py"),
    ("宮島17", "pages/17_miyajima.py"), ("徳山18", "pages/18_tokuyama.py"), ("下関19", "pages/19_simonoseki.py"), ("若松20", "pages/20_wakamatu.py"),
    ("芦屋21", "pages/21_asiya.py"), ("福岡22", "pages/22_hukuoka.py"), ("唐津23", "pages/23_karatu.py"), ("大村24", "pages/24_omura.py")
]

for i in range(0, len(venue_list), 4):
    cols = st.columns(4)
    for j in range(4):
        if i + j < len(venue_list):
            name, path = venue_list[i + j]
            with cols[j]:
                if st.button(name, use_container_width=True):
                    st.switch_page(path)

