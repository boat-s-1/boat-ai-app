import streamlit as st
import os

# 1. 基本設定（必ず一番上）
st.set_page_config(page_title="競艇Pro", layout="wide")

# 2. ページ一覧の定義
# 注意：メインの public_app.py は navigation に含めないか、
# もしくは「実行専用の関数」を呼び出す形にします。
def show_main_page():
    st.title("🏁 会場を選択")
    
    # 会場リスト（作成済みのファイルのみ表示されます）
    venue_list = [
        ("桐生01", "pages/01_kiryu.py"), ("戸田02", "pages/02_toda.py"), 
        ("江戸川03", "pages/03_edogawa.py"), ("平和島04", "pages/04_heiwajima.py"),
        ("多摩川05", "pages/05_tamagawa.py"), ("浜名湖06", "pages/06_hamanako.py"), 
        ("蒲郡07", "pages/07_gamagori.py"), ("常滑08", "pages/08_tokoname.py"),
        # ... 以下、他の会場も同様
    ]

    # 4列ずつ表示
    for i in range(0, len(venue_list), 4):
        cols = st.columns(4)
        for j in range(4):
            if i + j < len(venue_list):
                name, path = venue_list[i + j]
                with cols[j]:
                    # ファイルが存在する場合のみボタンを表示
                    if os.path.exists(path):
                        if st.button(name, use_container_width=True, key=name):
                            st.switch_page(path)

# 3. ページの定義
# ファイルが存在するものだけをサイドバーに出す
p01 = st.Page("pages/01_kiryu.py", title="桐生", icon="🚤")
p02 = st.Page("pages/02_toda.py", title="戸田", icon="🚤")
p03 = st.Page("pages/03_edogawa.py", title="江戸川", icon="🚤")
p04 = st.Page("pages/04_heiwajima.py", title="平和島", icon="🚤")
p05 = st.Page("pages/05_tamagawa.py", title="多摩川", icon="🚤")
p06 = st.Page("pages/06_hamanako.py", title="浜名湖", icon="🚤")
p07 = st.Page("pages/07_gamagori.py", title="蒲郡", icon="🏁")

# 4. ナビゲーション
# 最初のページは st.Page ではなく「関数」を渡すことで無限ループを回避します
main_page = st.Page(show_main_page, title="ホーム", icon="🏠", default=True)

pg = st.navigation({
    "メイン": [main_page],
    "関東・東海地区": [p01, p02, p03, p04, p05, p06, p07]
})

# 5. サイドバーの設定
with st.sidebar:
    st.markdown("### 🏆 競艇予想Pro")

# 6. 実行
pg.run()
