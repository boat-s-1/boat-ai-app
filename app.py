import streamlit as st
import datetime

# ページ設定
st.set_page_config(page_title="Birthstones新聞 生成App", layout="wide")

# 日付
today = datetime.date.today()
formatted_date = today.strftime("%Y年%m月%d日")

# --- 1. サイドバー：データ入力 ---
st.sidebar.header("📰 新聞データ入力")

with st.sidebar.expander("⏱ 左：タイム解析データ", expanded=True):
    i_place = st.text_input("レース場", value="住之江")
    i_race = st.text_input("レース番号", value="12R")
    st.write("【生展示タイム】")
    t_cols = st.columns(3)
    raw_t = [t_cols[i % 3].number_input(f"{i+1}号", value=6.50+(i*0.02), step=0.01, format="%.2f", key=f"r_{i}") for i in range(6)]
    st.write("【補正値】")
    o_cols = st.columns(3)
    offs = [o_cols[i % 3].number_input(f"{i+1}補正", value=(-0.03 if i==0 else 0.0), step=0.01, format="%.2f", key=f"o_{i}") for i in range(6)]

with st.sidebar.expander("💎 右：3人の判定", expanded=True):
    i_exp = st.slider("一果：期待値", 30, 100, 78)
    i_msg = st.text_input("一果コメント", value="補正タイム抜群！お任せ！")
    h_eval = st.text_input("初音：格付け", value="1=◯, 4=△, 5=✖️")
    h_msg = st.text_input("初音コメント", value="期待配当の歪みは2,500円。")
    k_eval = st.selectbox("キイナ：穴判定", ["見", "GO", "買わなきゃ損！"], index=2)
    k_msg = st.text_input("キイナコメント", value="4が凹めば5が突き抜ける！")

with st.sidebar.expander("🤝 下：3人の合議", expanded=True):
    total_title = st.text_input("タイトル", value="1頭固定の鉄板レース！")
    total_msg = st.text_area("合議詳細", value="3人の見解が一致。イン逃げ確率は極めて高いです！")

# --- 2. 計算ロジック ---
final_t = [round(raw_t[i] + offs[i], 2) for i in range(6)]
sorted_u = sorted(list(set(final_t)))
best_t = sorted_u[0]
second_t = sorted_u[1] if len(sorted_u) > 1 else None

def get_c(t):
    if t == best_t: return "background:#ef4444; color:white;"
    if t == second_t: return "background:#fef08a; color:#854d0e;"
    return "background:white;"

# --- 3. CSS定義 ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Kosugi+Maru&family=Yomogi&display=swap');
    .stApp { background-color: #f0f4f8; }
    
    /* 新聞の紙 */
    .paper {
        background: white !important; width: 900px !important; margin: 0 auto !important;
        padding: 40px !important; border: 2px solid #333 !important;
        box-shadow: 10px 10px 0px #cbd5e0 !important; font-family: 'Kosugi Maru', sans-serif;
    }

    /* 各種装飾 */
    .news-box { border: 2px solid #333 !important; border-radius: 10px; padding: 15px; background: #fff; margin-bottom: 20px; }
    .box-title { font-weight: bold; border-bottom: 2px dashed #333; margin-bottom: 12px; font-size: 17px; }
    .data-table { width: 100%; border-collapse: collapse; text-align: center; font-weight: bold; }
    .data-table th { background: #edf2f7; border: 1px solid #333; padding: 4px; font-size: 11px; }
    .data-table td { border: 1px solid #333; padding: 8px; font-size: 16px; }
    
    .fukidashi { display: flex; gap: 8px; background: #fefce8; padding: 8px; border-radius: 8px; border: 1px solid #fef08a; font-family: 'Yomogi', cursive; font-size: 13px; margin-bottom: 5px; }
    .char-mini { width: 35px; height: 35px; border-radius: 50%; border: 1px solid #333; background: #fff; display: flex; align-items: center; justify-content: center; font-size: 9px; flex-shrink: 0; }
</style>
""", unsafe_allow_html=True)

# --- 4. HTML構築 ---
needle = (i_exp - 50) * 1.8
raw_tds = "".join([f"<td>{t:.2f}</td>" for t in raw_t])
final_tds = "".join([f'<td style="{get_c(t)}">{t:.2f}</td>' for t in final_t])

html = f"""
<div class="paper">
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 4px double #333; padding-bottom: 15px; margin-bottom: 25px;">
        <div style="font-size: 11px; line-height: 1.2;">3年1組<br>BOAT STRIKE! 係</div>
        <div style="background: linear-gradient(to right, #ffecd2, #fcb69f); padding: 5px 40px; border: 2px solid #333; border-radius: 50px; font-size: 34px; font-weight: bold; color:#1a1a1a;">Birthstones新聞</div>
        <div style="text-align: right; font-size: 11px;">{formatted_date} 第29号</div>
    </div>

    <div style="display: flex; gap: 20px;">
        <div style="flex: 1.7;">
            <div class="news-box" style="background: #f8fafc; height: 100%; margin-bottom: 0;">
                <div class="box-title">📊 解析：展示タイム生データ</div>
                <p style="font-size: 12px; margin-bottom: 5px;">会場：ボートレース{i_place} {i_race}</p>
                <table class="data-table">
                    <tr><th>1号</th><th>2号</th><th>3号</th><th>4号</th><th>5号</th><th>6号</th></tr>
                    <tr>{raw_tds}</tr>
                </table>
                <div style="margin-top: 30px;" class="box-title">🔍 独自：補正展示タイム</div>
                <div style="background: #fff; border: 2px solid #333; border-radius: 8px; padding: 15px;">
                    <table class="data-table">
                        <tr><th>1号</th><th>2号</th><th>3号</th><th>4号</th><th>5号</th><th>6号</th></tr>
                        <tr>{final_tds}</tr>
                    </table>
                </div>
                <p style="font-size: 11px; color: #64748b; margin-top: 20px;">※1位：赤、2位：黄で自動色分けしています。</p>
            </div>
        </div>

        <div style="flex: 1.3;">
            <div class="news-box" style="height: 100%; margin-bottom: 0; background: #fffdf5;">
                <div class="box-title" style="border-color:#f59e0b;">💬 3人の放課後トーク</div>
                
                <div style="display: flex; align-items: center; justify-content: space-around; margin-bottom: 10px; border: 1px solid #fef08a; padding: 5px; border-radius: 10px; background: white;">
                    <div style="position: relative; width: 80px; height: 45px; border-bottom: 2px solid #333; overflow: hidden;">
                        <div style="width: 80px; height: 80px; border-radius: 50%; border: 8px solid #e2e8f0; border-bottom-color: transparent; border-left-color: #f87171; transform: rotate(45deg);"></div>
                        <div style="position: absolute; bottom: 0; left: 50%; width: 2px; height: 35px; background: #1a1a1a; transform-origin: bottom center; transform: translateX(-50%) rotate({needle}deg);"></div>
                    </div>
                    <div style="font-size: 18px; font-weight: bold; color: #ef4444;">一果:{i_exp}%</div>
                </div>
                <div class="fukidashi"><div class="char-mini">一果</div>{i_msg}</div>

                <div style="background: #1e293b; color: white; padding: 2px; text-align: center; border-radius: 4px; font-size: 12px; margin: 10px 0 5px 0;">初音判定：{h_eval}</div>
                <div class="fukidashi" style="background:#f0f9ff; border-color:#3b82f6;"><div class="char-mini">初音</div>{h_msg}</div>

                <div style="background: #ef4444; color: white; padding: 2px; text-align: center; border-radius: 4px; font-size: 12px; margin: 10px 0 5px 0;">キイナ穴狙い：{k_eval}</div>
                <div class="fukidashi" style="background:#fff;"><div class="char-mini">キイナ</div>{k_msg}</div>
            </div>
        </div>
    </div>

    <div class="news-box" style="background: #f8fafc; border: 3px double #333; margin-top: 20px;">
        <div class="box-title">🤝 結論：3人の合議メモ</div>
        <div style="padding: 15px; background: white; border: 1.5px dashed #333; border-radius: 8px;">
            <div style="font-weight: bold; color: #dc2626; margin-bottom: 5px; font-size: 16px;">{total_title}</div>
            <div style="font-size: 14px; line-height: 1.6; font-family: 'Yomogi', cursive;">{total_msg}</div>
        </div>
    </div>
</div>
"""

st.markdown(html, unsafe_allow_html=True)
