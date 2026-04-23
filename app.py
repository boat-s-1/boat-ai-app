import streamlit as st
import datetime

# ページ設定
st.set_page_config(page_title="Birthstones新聞 生成App", layout="wide")

# 日付
today = datetime.date.today()
formatted_date = today.strftime("%Y年%m月%d日")

# --- 1. サイドバー：データ入力（変数名の不一致を完全修正） ---
st.sidebar.header("📰 新聞データ入力")

with st.sidebar.expander("⏱ 左：タイム解析データ", expanded=True):
    i_place = st.text_input("レース場", value="住之江")
    i_race = st.text_input("レース番号", value="12R")
    st.write("各艇の【生展示タイム】")
    t_cols = st.columns(3)
    raw_t = [t_cols[i % 3].number_input(f"{i+1}号", value=6.50+(i*0.01), step=0.01, format="%.2f", key=f"r_v_{i}") for i in range(6)]
    st.write("独自補正（イン/場など）")
    o_cols = st.columns(3)
    offs = [o_cols[i % 3].number_input(f"{i+1}補正", value=(-0.03 if i==0 else 0.0), step=0.01, format="%.2f", key=f"o_v_{i}") for i in range(6)]

with st.sidebar.expander("💎 右：3人の判定", expanded=True):
    i_exp = st.slider("一果：期待値 (%)", 30, 100, 78)
    i_msg = st.text_input("一果コメント", value="補正タイム抜群！一果にお任せ！")
    h_eval = st.text_input("初音：格付け", value="1=◯, 4=△, 5=✖️")
    h_msg = st.text_input("初音コメント", value="期待配当の歪みは2,500円。")
    k_eval = st.selectbox("キイナ：穴判定", ["見", "GO", "買わなきゃ損！"], index=2)
    k_msg = st.text_input("キイナコメント", value="4が凹めば5が突き抜ける！")

with st.sidebar.expander("🤝 下：3人の合議", expanded=True):
    total_title = st.text_input("タイトル", value="1頭固定の鉄板レース！")
    total_text = st.text_area("合議詳細", value="3人の見解が一致しました。イン逃げ確率は極めて高いです！")

# --- 2. 計算ロジック ---
final_t = [round(raw_t[i] + offs[i], 2) for i in range(6)]
sorted_u = sorted(list(set(final_t)))
best_t = sorted_u[0]
second_t = sorted_u[1] if len(sorted_u) > 1 else None

# 色分け用スタイル（タグ漏れ防止のため関数化）
def get_t_css(t):
    if t == best_t: return "background:#ef4444 !important; color:white !important;"
    if t == second_t: return "background:#fef08a !important; color:#854d0e !important;"
    return "background:white !important; color:#333 !important;"

# --- 3. CSS定義（デザインの骨格を先に読み込み） ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Kosugi+Maru&family=Yomogi&display=swap');
    .stApp { background-color: #f0f4f8; }
    
    .paper-frame {
        background-color: white !important; width: 920px !important; margin: 0 auto !important;
        padding: 40px !important; border: 2px solid #333 !important;
        box-shadow: 12px 12px 0px #cbd5e0 !important; font-family: 'Kosugi Maru', sans-serif;
    }
    .box-title { font-weight: bold; border-bottom: 2px dashed #333; margin-bottom: 12px; font-size: 18px; display: flex; align-items: center; gap: 8px; }
    .data-table { width: 100%; border-collapse: collapse; text-align: center; }
    .data-table th { background: #edf2f7; border: 1px solid #333; padding: 4px; font-size: 11px; }
    .data-table td { border: 1px solid #333; padding: 8px; font-size: 16px; font-weight: bold; }
    .voice-area { display: flex; gap: 10px; background: #fefce8; padding: 10px; border-radius: 10px; border: 1px solid #fef08a; font-family: 'Yomogi', cursive; font-size: 14px; margin-bottom: 8px; }
    .face-badge { width: 40px; height: 40px; border-radius: 50%; border: 1.5px solid #333; background: #fff; display: flex; align-items: center; justify-content: center; font-size: 10px; flex-shrink: 0; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 4. HTML構築（各パーツを安全に結合） ---
needle_angle = (i_exp - 50) * 1.8
raw_tds = "".join([f"<td>{t:.2f}</td>" for t in raw_t])
final_tds = "".join([f'<td style="{get_t_css(t)}">{t:.2f}</td>' for t in final_t])

# 全体を一つの巨大なHTMLにまとめ、パーツ間の隙間を物理的に消します
full_html = f"""
<div class="paper-frame">
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 4px double #333; padding-bottom: 15px; margin-bottom: 25px;">
        <div style="font-size: 12px; line-height: 1.4;">3年1組<br>BOAT STRIKE! 係</div>
        <div style="background: linear-gradient(to right, #ffecd2, #fcb69f); padding: 8px 60px; border: 2px solid #333; border-radius: 50px; font-size: 38px; font-weight: bold; color: #1a1a1a;">Birthstones新聞</div>
        <div style="text-align: right; font-size: 12px;">{formatted_date} 第32号</div>
    </div>

    <div style="display: flex; gap: 20px; align-items: stretch;">
        <div style="flex: 1.7; border: 2px solid #333; border-radius: 12px; padding: 15px; background: #f8fafc;">
            <div class="box-title">📊 公式：展示タイム生データ</div>
            <table class="data-table">
                <tr><th>1号</th><th>2号</th><th>3号</th><th>4号</th><th>5号</th><th>6号</th></tr>
                <tr>{raw_tds}</tr>
            </table>
            <div style="margin-top: 40px;" class="box-title">🔍 独自：補正展示タイム解析</div>
            <div style="background: white; border: 2px solid #333; border-radius: 8px; padding: 20px;">
                <table class="data-table">
                    <tr><th>1号</th><th>2号</th><th>3号</th><th>4号</th><th>5号</th><th>6号</th></tr>
                    <tr>{final_tds}</tr>
                </table>
                <div style="margin-top: 15px; display: flex; gap: 20px; font-size: 11px; font-weight: bold;">
                    <span><b style="color:#ef4444;">■</b> 1番時計</span><span><b style="color:#d69e2e;">■</b> 2番時計</span>
                </div>
            </div>
        </div>

        <div style="flex: 1.3; border: 2px solid #333; border-radius: 12px; padding: 15px; background: #fffdf5;">
            <div class="box-title" style="color: #854d0e;">💬 3人の放課後トーク</div>
            <div style="display: flex; align-items: center; justify-content: space-around; margin-bottom: 15px; border: 1.5px solid #fef08a; padding: 10px; border-radius: 12px; background: white;">
                <div style="position: relative; width: 100px; height: 55px; border-bottom: 2px solid #333; overflow: hidden;">
                    <div style="width: 100px; height: 100px; border-radius: 50%; border: 10px solid #e2e8f0; border-bottom-color: transparent; border-left-color: #f87171; transform: rotate(45deg);"></div>
                    <div style="position: absolute; bottom: 0; left: 50%; width: 3px; height: 45px; background: #1a1a1a; transform-origin: bottom center; transform: translateX(-50%) rotate({needle_angle}deg);"></div>
                </div>
                <div style="font-size: 26px; font-weight: bold; color: #ef4444;">一果:{i_exp}%</div>
            </div>
            <div class="voice-area"><div class="face-badge">一果</div>「{i_msg}」</div>
            <div style="background: #1e293b; color: white; padding: 3px; text-align: center; border-radius: 4px; font-size: 13px; font-weight: bold; margin: 15px 0 8px 0;">初音判定：{h_eval}</div>
            <div class="voice-area" style="background:#f0f9ff; border-color:#3b82f6;"><div class="face-badge">初音</div>「{h_msg}」</div>
            <div style="background: #ef4444; color: white; padding: 4px; text-align: center; border-radius: 4px; font-size: 13px; font-weight: bold; margin: 15px 0 8px 0;">キイナ判定：{k_eval}</div>
            <div class="voice-area" style="background:white; border-color:#eab308;"><div class="face-badge">キイナ</div>「{k_msg}」</div>
        </div>
    </div>

    <div style="border: 3px double #333; border-radius: 12px; padding: 15px; background: #f8fafc; margin-top: 25px;">
        <div class="box-title">🤝 結論：3人のトータル意見</div>
        <div style="padding: 20px; background: white; border: 1.5px dashed #333; border-radius: 8px;">
            <div style="font-weight: bold; color: #dc2626; margin-bottom: 8px; font-size: 20px;">{total_title}</div>
            <div style="font-size: 16px; line-height: 1.6; font-family: 'Yomogi', cursive;">{total_text}</div>
        </div>
    </div>
</div>
"""

# 全体を一括表示
st.markdown(full_html, unsafe_allow_html=True)
