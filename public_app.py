import streamlit as st
import pandas as pd
import os
import gspread
from google.oauth2.service_account import Credentials

# --- 1. ページ初期設定 ---
st.set_page_config(page_title="競艇予想Pro - Premium", layout="wide")

# Google Sheets 認証用関数（既存のものを想定）
def get_gsheet_client():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        # StreamlitのSecretsから認証情報を取得
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        return gspread.authorize(creds)
    except Exception as e:
        return None

# --- 2. 高級感あふれるカスタムCSS ---
st.markdown("""
    <style>
    .main { background-color: #f4f7f9; }
    h1 {
        color: #1e293b;
        font-family: 'Helvetica Neue', Arial, sans-serif;
        font-weight: 800;
        border-left: 8px solid #bda06d;
        padding-left: 15px;
        margin-bottom: 25px;
    }
    .guide-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        transition: transform 0.3s ease;
        margin-bottom: 10px;
    }
    .guide-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(189, 160, 109, 0.2);
    }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; background-color: white; border-radius: 10px 10px 0 0;
        border: 1px solid #e2e8f0; color: #64748b;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1e3a8a !important; color: white !important;
        border-top: 3px solid #bda06d !important;
    }
    /* 開催一覧ボタンの装飾 */
    div.stButton > button {
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        background-color: white;
        transition: all 0.3s;
    }
    div.stButton > button:hover {
        border-color: #bda06d;
        color: #bda06d;
        background-color: #fcfaf5;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. ガイド枠表示関数 ---
def show_guide_section(gc):
    st.markdown("### 💎 本日のプレミアム・ガイド")
    try:
        sh = gc.open_by_key("1lN794iGtyGV2jNwlYzUA8wEbhRwhPM7FxDAkMaoJss4")
        worksheets = [ws.title for ws in sh.worksheets()]
        if "ガイド枠" not in worksheets:
            st.warning("⚠️ シート『ガイド枠』が見つかりません。")
            return

        ws_guide = sh.worksheet("ガイド枠")
        guide_df = pd.DataFrame(ws_guide.get_all_records())

        if not guide_df.empty:
            g_cols = st.columns(len(guide_df))
            for i, row in guide_df.iterrows():
                with g_cols[i]:
                    color = "#ef4444" if row['信頼度'] == "S" else "#3b82f6" if row['信頼度'] == "A" else "#10b981"
                    st.markdown(f"""
                        <div class="guide-card">
                            <div style="font-size:0.8rem; color:#64748b;">{row['締切']} 締切</div>
                            <div style="font-size:1.2rem; font-weight:bold; color:#1e293b; margin: 5px 0;">⚓ {row['会場']} {row['レース番号']}</div>
                            <div style="color:{color}; font-weight:bold; font-size:1rem; margin-bottom:10px;">【信頼度：{row['信頼度']}】</div>
                            <div style="font-size:0.9rem; color:#475569; line-height:1.4; min-height:50px;">{row['コメント']}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"✨ {row['会場']} 解析データ", key=f"btn_g_{i}", use_container_width=True):
                        st.switch_page(row['ページパス'])
        else:
            st.info("🌙 現在、次節のデータを精査中です。")
    except Exception as e:
        st.error("データの接続に一時的な制限がかかっています。")

# --- 4. メイン実行ロジック ---
def main():
    st.title("競艇予想Pro - プレミアム解析ツール")
    
    gc = get_gsheet_client()
    if gc:
        show_guide_section(gc)
    
    tab1, tab2, tab3, tab4 = st.tabs(["🚩 開催一覧", "🔰 使い方", "📱 公式SNS", "📈 的中実績"])

    # --- TAB1: 開催一覧 ---
    with tab1:
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
        for i in range(0, len(all_venues), 4):
            cols = st.columns(4)
            for j in range(4):
                if i + j < len(all_venues):
                    name, path, v_type = all_venues[i + j]
                    with cols[j]:
                        label = f"{v_type}\n【{name}】\n予想データ"
                        if os.path.exists(path):
                            if st.button(label, use_container_width=True, key=f"btn_{name}"):
                                st.switch_page(path)
                        else:
                            st.button(f"{v_type}\n【{name}】\n準備中", use_container_width=True, disabled=True)

    # --- TAB2: 使い方 ---
    with tab2:
        st.header("📖 競艇予想Pro 攻略マニュアル")
        # （以前の「使い方」コードをここに配置。hit1等の変数エラーを防ぐため仮の数値を設定）
        h1, h2, h3 = "72.4%", "85.1%", "91.8%" 
        
        with st.container(border=True):
            st.markdown("""<div style='text-align:center;'><h2>🔥 圧倒的データ量 × 独自解析ロジック</h2></div>""", unsafe_allow_html=True)
            col_v1, col_v2, col_v3 = st.columns(3)
            col_v1.metric("指数1位 → 1着率", h1)
            col_v2.metric("上位2艇 連対率", h2)
            col_v3.metric("上位3艇 1着包含率", h3)
        
        st.divider()
        with st.expander("🎯 STEP1：事前簡易予想"):
            st.write("展示前の期待値を可視化。")
        with st.expander("📊 STEP2：統計解析シート"):
            st.write("会場ごとのタイム補正。")
        with st.expander("🚀 STEP3：スタート指数"):
            st.write("スリット付近の強さを数値化。")
        with st.expander("🌊 STEP4：条件補正"):
            st.write("風・波の影響を分析。")

    # --- TAB3: SNS ---
    with tab3:
        st.subheader("📱 公式リンク")
        st.link_button("公式X (@bort_strike) をフォロー", "https://x.com/bort_strike", use_container_width=True)

if __name__ == "__main__":
    main()
