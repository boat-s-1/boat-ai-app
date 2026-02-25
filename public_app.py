import streamlit as st
import os

# 1. 最初に必ず実行（鉄則！）
st.set_page_config(page_title="競艇Pro", layout="wide")

# 2. ページの定義
# ファイル名が正しいか、os.path.existsでチェックしながら作成します
def create_page(path, title, icon):
    if os.path.exists(path):
        return st.Page(path, title=title, icon=icon)
    return None

p01 = create_page("pages/01_kiryu.py", "桐生競艇場", "🚤")
p02 = create_page("pages/02_toda.py", "戸田競艇場", "🌊")
p07 = create_page("pages/07_gamagori.py", "蒲郡競艇場", "🏁")

# 存在するページだけをリストにする
valid_pages = [p for p in [p01, p02, p07] if p is not None]

# 3. ナビゲーションの設定
if valid_pages:
    # ページ定義がある場合はナビゲーションを実行
    pg = st.navigation(valid_pages)
    # pg.run() を呼ぶと、現在のページの内容が表示されます
    # ※ ボタンを表示させたいメインページ自体も navigation に含めるのが本来の形です
    pg.run()
else:
    # ページが見つからない場合のデバッグ表示
    st.error("ページファイルが見つかりません。")
    if os.path.exists("pages"):
        st.write("pagesフォルダ内のファイル:", os.listdir("pages"))

# --- 注意：pg.run() を使うと、以下のボタンコードは「メインページ」として 
# navigation に登録したファイル内に書く必要があります ---

st.set_page_config(page_title="競艇Pro", layout="wide")

st.title("🏁 会場を選択")

col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

with col1:
    if st.button("桐生01", use_container_width=True):
        st.switch_page("pages/01_kiryu.py")

with col2:
    if st.button("戸田02", use_container_width=True):
        st.switch_page("pages/02_toda.py")

with col3:
    if st.button("江戸川03", use_container_width=True):
        st.switch_page("pages/03_edogawa.py")

with col4:
    if st.button("平和島04", use_container_width=True):
        st.switch_page("pages/04_heiwajima.py")

with col5:
    if st.button("多摩川05", use_container_width=True):
        st.switch_page("pages/05_tamagawa.py")

with col6:
    if st.button("浜名湖06", use_container_width=True):
        st.switch_page("pages/06_hamanako.py")

with col7:
    if st.button("蒲郡07", use_container_width=True):
        st.switch_page("pages/07_gamagori.py")



