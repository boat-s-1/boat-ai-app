import streamlit as st

# 1. 基本設定（必ず一番上に一度だけ）
st.set_page_config(page_title="競艇Pro", layout="wide")

# 2. 各ページの設定（サイドバーの表示名、アイコン、セクションを指定）
# ホーム画面
home = st.Page("public_app.py", title="ホーム (会場選択)", icon="🏠", default=True)

# 関東地区
p01 = st.Page("pages/01_kiryu.py", title="桐生", icon="🚤")
p02 = st.Page("pages/02_toda.py", title="戸田", icon="🚤")
p03 = st.Page("pages/03_edogawa.py", title="江戸川", icon="🚤")
p04 = st.Page("pages/04_heiwajima.py", title="平和島", icon="🚤")
p05 = st.Page("pages/05_tamagawa.py", title="多摩川", icon="🚤")

# 東海地区
p06 = st.Page("pages/06_hamanako.py", title="浜名湖", icon="🚤")
p07 = st.Page("pages/07_gamagori.py", title="蒲郡", icon="🚤")
p08 = st.Page("pages/08_tokoname.py", title="常滑", icon="🚤")
p09 = st.Page("pages/09_tu.py", title="津", icon="🚤")

# 北陸・近畿地区
p10 = st.Page("pages/10_mikuni.py", title="三国", icon="🚤")
p11 = st.Page("pages/11_biwako.py", title="びわこ", icon="🚤")
p12 = st.Page("pages/12_suminoe.py", title="住之江", icon="🚤")
p13 = st.Page("pages/13_amagasaki.py", title="尼崎", icon="🚤")

# 四国・中国地区
p14 = st.Page("pages/14_naruto.py", title="鳴門", icon="🚤")
p15 = st.Page("pages/15_marugame.py", title="丸亀", icon="🚤")
p16 = st.Page("pages/16_kojima.py", title="児島", icon="🚤")
p17 = st.Page("pages/17_miyajima.py", title="宮島", icon="🚤")
p18 = st.Page("pages/18_tokuyama.py", title="徳山", icon="🚤")
p19 = st.Page("pages/19_simonoseki.py", title="下関", icon="🚤")

# 九州地区
p20 = st.Page("pages/20_wakamatu.py", title="若松", icon="🚤")
p21 = st.Page("pages/21_asiya.py", title="芦屋", icon="🚤")
p22 = st.Page("pages/22_hukuoka.py", title="福岡", icon="🚤")
p23 = st.Page("pages/23_karatu.py", title="唐津", icon="🚤")
p24 = st.Page("pages/24_omura.py", title="大村", icon="🚤")

# 3. サイドバーのナビゲーションをエリア別に整理
pg = st.navigation({
    "メイン": [home],
    "関東地区": [p01, p02, p03, p04, p05],
    "東海地区": [p06, p07, p08, p09],
    "北陸・近畿地区": [p10, p11, p12, p13],
    "四国・中国地区": [p14, p15, p16, p17, p18, p19],
    "九州地区": [p20, p21, p22, p23, p24]
})

# 4. サイドバーにロゴなどの共通パーツを追加（任意）
with st.sidebar:
    st.markdown("### 🏆 競艇予想Pro")
    st.caption("会場名を選択してください")

# 5. 実行
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
