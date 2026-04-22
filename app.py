import streamlit as st
import datetime

# ページ設定
st.set_page_config(page_title="Birthstones新聞 生成App", layout="wide")

# 日付
today = datetime.date.today()
formatted_date = today.strftime("%Y年%m月%d日")

# --- 1. サイドバー：データ入力 ---
st.sidebar.header("📊 新聞データ入力")

with st.sidebar.expander("⏱ 展示タイム設定", expanded=True):
    i_place = st.text_input("レース場", value="住之江")
    i_race = st.text_input("レース番号", value="12R")
    st.write("【生展示タイム】")
    t_cols = st.columns(3)
    raw_t = [t_cols[i % 3].number_input(f"{i+1}号艇", value=6.50 + (i*0.02), step=0.01, format="%.2f", key=f"r_raw_{i}") for i in range(6)]
    st.write("【独自補正値】")
    o_cols = st.columns(3)
    offsets = [o_cols[i % 3].number_input(f"{i+1}補正", value=(-0.03 if i == 0 else 0.00), step=0.01, format="%.2f", key=f"r_off_{i}") for i in range(6)]

with st.sidebar.expander("💎 キャラクター判定", expanded=True):
    i_exp = st.slider("一果：期待値 (%)", 30, 100, 78)
    i_text = st.text_area("一果：一言", value="補正タイムが抜群だよ！一果にお任せ！")
    h_eval = st.text_input("初音：格付け", value="1=◯, 4=△, 5=✖️")
    h_text = st.text_area("初音：分析", value="期待配当の歪みは2,500円。")
    k_eval = st.selectbox("キイナ：穴判定", ["見", "GO", "買わなきゃ損！"], index=2)
    k_text = st.text_area("キイナ：予感", value="4が凹めば5が突き抜ける！")

with st.sidebar.expander("🤝 合議（最下部）", expanded=True):
    total_title = st.text_input("最終結論タイトル", value="1頭固定の鉄板レース！")
    total_msg = st.text_area("合議の詳細", value="3人の見解が一致。イン逃げ確率は極めて高いです！")

# --- 2. 計算と色分けロジック ---
final_t = [round(raw_t[i] + offsets[i], 2) for i in range(6)]
sorted_u = sorted(list(set(final_t)))
best_t = sorted_u[0]
second_t = sorted_u[1] if len(sorted_u) > 1 else None

def get_cell_style(t):
    if t == best_t: return 'background-color:#ef4444 !important; color:white !important; border:2px solid #333 !important;'
    if t == second_t: return 'background-color:#fef08a !important; color:#854d0e !important; border:2px solid #333 !important;'
    return 'background-color:white !important; color:#333 !important;'

# --- 3. CSS定義 ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Kosugi+Maru&family=Yomogi&display=swap');
    .stApp { font-family: 'Kosugi Maru', sans-serif; background-color: #f0f4f8; }
    .paper-frame { background-color: white !important; max-width: 950px !important; margin: 0 auto !important; padding: 40px !important; border: 2px solid #333 !important; box-shadow: 12px 12px 0px #cbd5e0 !important; }
    .news-box { border: 2px solid #333 !important; border-radius: 10px !important; padding: 15px !important; background: #fff !important; margin-bottom: 20px !important; }
    .box-header { font-weight: bold !important; border-bottom: 2px dashed #333 !important; margin-bottom: 15px !important; font-size: 18px !important; display: flex; align-items: center; gap: 8px; }
    .data-table { width: 100%; border-collapse: collapse; text-align: center; }
    .data-table th { background: #edf2f7; border: 1px solid #333; padding: 5px; font-size: 12px; }
    .data-table td { border: 1px solid #333; padding: 10px; font-size: 18px; font-weight: bold; }
    .voice-bubble { display: flex; gap: 10px; background: #fefce8; padding: 10px; border-radius: 12px; border: 1px solid #fef08a; font-family: 'Yomogi', cursive; font-size: 15px; margin-top: 10px; }
    .char-icon { width: 45px; height: 45px; border-radius: 50%; border: 1.5px solid #333; background: #fff; display: flex; align-items: center; justify-content: center; font-size: 10px; flex-shrink: 0; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 4. 描画（完全分割方式） ---

# 紙の枠
st.markdown('<div class="paper-frame">', unsafe_allow_html=True)

# ヘッダー
st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 4px double #333; padding-bottom: 15px; margin-bottom: 30px;">
        <div style="font-size: 12px; line-height: 1.4;">3年1組<br>BOAT STRIKE! 係</div>
        <div style="background: linear-gradient(to right, #ffecd2, #fcb69f); padding: 8px 60px; border: 2px solid #333; border-radius: 50px; font-size: 38px; font-weight: bold; color: #1a1a1a;">Birthstones新聞</div>
        <div style="text-align: right; font-size: 12px;">{formatted_date} 第26号</div>
    </div>
""", unsafe_allow_html=True)

col_l, col_r = st.columns([1.7, 1.3])

with col_l:
    # 展示タイム生データ（1つずつ確実に閉じる）
    raw_cells = "".join([f"<td>{t:.2f}</td>" for t in raw_t])
    st.markdown(f"""
        <div class="news-box" style="background: #f8fafc; min-height: 550px;">
            <div class="box-header">📊 公式：展示タイム生データ</div>
            <p style="font-size: 13px; margin-left: 5px;">会場：ボートレース{i_place} {i_race}</p>
            <table class="data-table">
                <tr><th>1号</th><th>2号</th><th>3号</th><th>4号</th><th>5号</th><th>6号</th></tr>
                <tr>{raw_cells}</tr>
            </table>
    """, unsafe_allow_html=True)
    
    # 独自補正タイム（ここが漏れていたので完全に独立させて描画）
    final_cells = "".join([f'<td style="{get_cell_style(t)}">{t:.2f}</td>' for t in final_t])
    st.markdown(f"""
            <div style="margin-top: 40px;" class="box-header">🔍 独自：補正展示タイム解析</div>
            <div style="background: white; border: 2px solid #333; border-radius: 8px; padding: 15px;">
                <table class="data-table">
                    <tr><th>1号</th><th>2号</th><th>3号</th><th>4号</th><th>5号</th><th>6号</th></tr>
                    <tr>{final_cells}</tr>
                </table>
                <div style="margin-top: 12px; display: flex; gap: 20px; font-size: 12px; font-weight: bold;">
                    <span><b style="color:#ef4444;">■</b> 1番時計</span>
                    <span><b style="color:#d69e2e;">■</b> 2番時計</span>
                </div>
            </div>
            <p style="font-size: 11px; color: #64748b; margin-top: 20px; font-style: italic;">※過去データに基づき算出。</p>
        </div>
    """, unsafe_allow_html=True)

with col_r:
    # 3人の個別判定
    needle_deg = (i_exp - 50) * 1.8
    st.markdown(f"""
        <div class="news-box" style="border-color: #f59e0b; background: #fffcf5;">
            <div class="box-header" style="color: #f59e0b;">🚩 一果のイン判定</div>
            <div style="display: flex; align-items: center; justify-content: space-around; margin: 5px 0;">
                <div style="position: relative; width: 120px; height: 65px; border-bottom: 2px solid #333; overflow: hidden; margin: 0 auto;">
                    <div style="width: 120px; height: 120px; border-radius: 50%; border: 10px solid #e2e8f0; border-bottom-color: transparent; border-left-color: #f87171; border-top-color: #fca5a5; transform: rotate(45deg);"></div>
                    <div style="position: absolute; bottom: 0; left: 50%; width: 3px; height: 50px; background: #1a1a1a; transform-origin: bottom center; transform: translateX(-50%) rotate({needle_deg}deg);"></div>
                </div>
                <div style="font-size: 32px; font-weight: bold; color: #ef4444;">{i_exp}%</div>
            </div>
            <div class="voice-bubble"><div class="char-icon">一果</div><div>「{i_text}」</div></div>
        </div>
        <div class="news-box" style="border-color: #3b82f6; background: #f0f9ff;">
            <div class="box-header" style="color: #3b82f6;">📚 初音の精密分析</div>
            <div style="background: #1e293b; color: white; padding: 4px; text-align: center; border-radius: 5px; font-weight: bold; margin-bottom: 8px;">{h_eval}</div>
            <div class="voice-bubble" style="background: #f8fafc; border-color: #cbd5e0;"><div class="char-icon">初音</div><div>「{h_text}」</div></div>
        </div>
        <div class="news-box" style="border-color: #eab308; background: #fffdf0; margin-bottom: 0px !important;">
            <div class="box-header" style="color: #854d0e;">⚡ キイナの穴狙い</div>
            <div style="background: #ef4444; color: white; padding: 4px; text-align: center; border-radius: 5px; font-weight: bold; margin-bottom: 8px;">判定：{k_eval}</div>
            <div class="voice-bubble" style="background: white;"><div class="char-icon">キイナ</div><div>「{k_text}」</div></div>
        </div>
    """, unsafe_allow_html=True)

# 合議エリア
st.markdown(f"""
    <div class="news-box" style="background: #f8fafc; border: 3px double #333; margin-top: 20px;">
        <div class="box-header" style="border-bottom-style: solid;">🤝 3人の放課後ミーティング</div>
        <div style="padding: 15px; background: white; border: 1.5px dashed #333; border-radius: 8px;">
            <div style="font-weight: bold; color: #dc2626; margin-bottom: 8px; font-size: 18px;">{total_title}</div>
            <div style="font-size: 15px; line-height: 1.6; font-family: 'Yomogi', cursive;">{total_msg}</div>
        </div>
    </div>
    </div>
""", unsafe_allow_html=True)
