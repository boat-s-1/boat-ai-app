import streamlit as st

st.set_page_config(page_title="競艇Pro", layout="wide")

st.title("🏁 会場を選択")

# --- 1段目 (01-06) ---
col = st.columns(6)
with col[0]:
    if st.button("桐生01", use_container_width=True): st.switch_page("pages/01_kiryu.py")
with col[1]:
    if st.button("戸田02", use_container_width=True): st.switch_page("pages/02_toda.py")
with col[2]:
    if st.button("江戸川03", use_container_width=True): st.switch_page("pages/03_edogawa.py")
with col[3]:
    if st.button("平和島04", use_container_width=True): st.switch_page("pages/04_heiwajima.py")
with col[4]:
    if st.button("多摩川05", use_container_width=True): st.switch_page("pages/05_tamagawa.py")
with col[5]:
    if st.button("浜名湖06", use_container_width=True): st.switch_page("pages/06_hamanako.py")

# --- 2段目 (07-12) ---
col = st.columns(6)
with col[0]:
    if st.button("蒲郡07", use_container_width=True): st.switch_page("pages/07_gamagori.py")
with col[1]:
    if st.button("常滑08", use_container_width=True): st.switch_page("pages/08_tokoname.py")
with col[2]:
    if st.button("津09", use_container_width=True): st.switch_page("pages/09_tu.py")
with col[3]:
    if st.button("三国10", use_container_width=True): st.switch_page("pages/10_mikuni.py")
with col[4]:
    if st.button("びわこ11", use_container_width=True): st.switch_page("pages/11_biwako.py")
with col[5]:
    if st.button("住之江12", use_container_width=True): st.switch_page("pages/12_suminoe.py")

# --- 3段目 (13-18) ---
col = st.columns(6)
with col[0]:
    if st.button("尼崎13", use_container_width=True): st.switch_page("pages/13_amagasaki.py")
with col[1]:
    if st.button("鳴門14", use_container_width=True): st.switch_page("pages/14_naruto.py")
with col[2]:
    if st.button("丸亀15", use_container_width=True): st.switch_page("pages/15_marugame.py")
with col[3]:
    if st.button("児島16", use_container_width=True): st.switch_page("pages/16_kojima.py")
with col[4]:
    if st.button("宮島17", use_container_width=True): st.switch_page("pages/17_miyajima.py")
with col[5]:
    if st.button("徳山18", use_container_width=True): st.switch_page("pages/18_tokuyama.py")

# --- 4段目 (19-24) ---
col = st.columns(6)
with col[0]:
    if st.button("下関19", use_container_width=True): st.switch_page("pages/19_simonoseki.py")
with col[1]:
    if st.button("若松20", use_container_width=True): st.switch_page("pages/20_wakamatu.py")
with col[2]:
    if st.button("芦屋21", use_container_width=True): st.switch_page("pages/21_asiya.py")
with col[3]:
    if st.button("福岡22", use_container_width=True): st.switch_page("pages/22_hukuoka.py")
with col[4]:
    if st.button("唐津23", use_container_width=True): st.switch_page("pages/23_karatu.py")
with col[5]:
    if st.button("大村24", use_container_width=True): st.switch_page("pages/24_omura.py")
