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
    k_eval = st.selectbox("穴判定", ["見", "GO", "買わなきゃ損！"], index=2)
    k_text = st.text_area("キイナ：予感", value="4が凹めば5が突き抜ける！")

with st.sidebar.expander("🤝 合議（最下部）", expanded=True):
    total_title = st.text_input("最終結論タイトル", value="1頭固定の鉄板レース！")
    total_msg = st.text_area("合議の詳細", value="3人の見解が一致。イン逃げ確率は極めて高いです！")

# --- 2. 計算ロジック ---
final_t = [round(raw_t[i] + offsets[i], 2) for i in range(6)]
sorted_u = sorted(list(set(final_t)))
best_t = sorted_u[0]
second_t = sorted_u[1] if len(sorted_u) > 1 else None

def get_t_style(t):
    if t == best_t: return 'background-color:#ef4444; color:white; border:2px solid #333;'
    if t == second_t: return 'background-color:#fef08a; color:#854d0e; border:2px solid #333;'
    return 'background-color:white; color:#333;'

# --- 3. CSS定義（デザインの骨格） ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Kosugi+Maru&family=Yomogi&display=swap');
    .stApp { font-family: 'Kosugi Maru', sans-serif; background-color: #f0f4f8; }
    .news-box { border: 2px solid #333 !important; border-radius: 10px; padding: 15px; background: #fff; margin-bottom: 20px; }
    .box-header { font-weight: bold; border-bottom: 2px dashed #333; margin-bottom: 15px; font-size: 18px; display: flex; align-items: center; gap: 8px; }
    .data-table { width: 100%; border-collapse: collapse; text-align: center; }
    .data-table th { background: #edf2f7; border: 1px solid #333; padding: 5px; font-size: 11px; }
    .data-table td { border: 1px solid #333; padding: 8px; font-size: 18px; font-weight: bold; }
    .voice-bubble { display: flex; gap: 10px; background: #fefce8; padding: 10px; border-radius: 12px; border: 1px solid #fef08a; font-family: 'Yomogi', cursive; font-size: 14px; }
    .char-icon { width: 42px; height: 42px; border-radius: 50%; border: 1.5px solid #333; background: #fff; display: flex; align-items: center; justify-content: center; font-size: 10px; flex-shrink: 0; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 4. 描画（一括HTMLをやめ、パーツごとに描画） ---

# 全体を囲う枠
st.markdown('<div style="background-color: white; max-width: 950px; margin: 0 auto; padding: 40px; border: 2px solid #333; box-shadow: 12px 12px 0px #cbd5e0;">', unsafe_allow_html=True)

# ヘッダー
st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 4px double #333; padding-bottom: 15px; margin-bottom: 30px;">
        <div style="font-size: 12px;">3年1組 BOAT STRIKE!</div>
        <div style="background: linear-gradient(to right, #ffecd2, #fcb69f); padding: 8px 60px; border: 2px solid #333; border-radius: 50px; font-size: 38px; font-weight: bold; color: #1a1a1a;">Birthstones新聞</div>
        <div style="text-align: right; font-size: 12px;">{formatted_date} 第28号</div>
    </div>
""", unsafe_allow_html=True)

# 2カラムレイアウト
col_l, col_r = st.columns([1.7, 1.3])

with col_l:
    # 展示タイム生データ
    raw_tds = "".join([f"<td>{t:.2f}</td>" for t in raw_t])
    st.markdown(f"""
        <div class="news-box" style="background: #f8fafc; min-height: 520px;">
            <div class="box-header">📊 公式：展示タイム生データ</div>
            <table class="data-table">
                <tr><th>1号</th><th>2号</th><th>3号</th><th>4号</th><th>5号</th><th>6号</th></tr>
                <tr>{raw_tds}</tr>
            </table>
    """, unsafe_allow_html=True)
    
    # 補正タイム
    f_tds = "".join([f'<td style="{get_t_style(t)}">{t:.2f}</td>' for t in final_t])
    st.markdown(f"""
            <div style="margin-top: 40px;" class="box-header">🔍 独自：補正展示タイム解析</div>
            <table class="data-table">
                <tr><th>1号</th><th>2号</th><th>3号</th><th>4号</th><th>5号</th><th>6号</th></tr>
                <tr>{f_tds}</tr>
            </table>
            <p style="font-size: 11px; color: #64748b; margin-top: 20px;">※1位：赤、2位：黄で自動色分けしています。</p>
        </div>
    """, unsafe_allow_html=True)

with col_r:
    # 右側の3人
    needle = (i_exp - 50) * 1.8
    st.markdown(f"""
        <div class="news-box" style="border-color: #f59e0b; background: #fffcf5;">
            <div class="box-header" style="color: #f59e0b;">🚩 一果の判定</div>
            <div style="display: flex; align-items: center; justify-content: space-around; margin: 5px 0;">
                <div style="position: relative; width: 110px; height: 60px; border-bottom: 2px solid #333; overflow: hidden;">
                    <div style="width: 110px; height: 110px; border-radius: 50%; border: 10px solid #e2e8f0; border-bottom-color: transparent; border-left-color: #f87171; transform: rotate(45deg);"></div>
                    <div style="position: absolute; bottom: 0; left: 50%; width: 3px; height: 50px; background: #1a1a1a; transform-origin: bottom center; transform: translateX(-50%) rotate({needle}deg);"></div>
                </div>
                <div style="font-size: 28px; font-weight: bold; color: #ef4444;">{i_exp}%</div>
            </div>
            <div class="voice-bubble"><div class="char-icon">一果</div><div>「{i_text}」</div></div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class="news-box" style="border-color: #3b82f6; background: #f0f9ff;">
            <div class="box-header" style="color: #3b82f6;">📚 初音の分析</div>
            <div style="background: #1e293b; color: white; padding: 4px; text-align: center; border-radius: 5px; font-weight: bold;">{h_eval}</div>
            <div class="voice-bubble" style="background: #f8fafc;"><div class="char-icon">初音</div><div>「{h_text}」</div></div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class="news-box" style="border-color: #eab308; background: #fffdf0;">
            <div class="box-header" style="color: #854d0e;">⚡ キイナの穴</div>
            <div style="background: #ef4444; color: white; padding: 4px; text-align: center; border-radius: 5px; font-weight: bold;">判定：{k_eval}</div>
            <div class="voice-bubble" style="background: white;"><div class="char-icon">キイナ</div><div>「{k_text}」</div></div>
        </div>
    """, unsafe_allow_html=True)

# 最下部
st.markdown(f"""
    <div class="news-box" style="background: #f8fafc; border: 3px double #333; margin-top: 10px;">
        <div class="box-header">🤝 3人の放課後ミーティング</div>
        <div style="padding: 15px; background: white; border: 1.5px dashed #333; border-radius: 8px;">
            <div style="font-weight: bold; color: #dc2626; margin-bottom: 5px; font-size: 16px;">{total_title}</div>
            <div style="font-size: 14px; line-height: 1.6; font-family: 'Yomogi', cursive;">{total_msg}</div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
