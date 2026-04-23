import streamlit as st
import datetime

# 1. ページ設定（これを最初に行う）
st.set_page_config(page_title="Birthstones新聞 生成App", layout="wide")

# 2. 変数準備
today = datetime.date.today()
formatted_date = today.strftime("%Y年%m月%d日")

# サイドバー入力
st.sidebar.header("📰 新聞データ入力")
with st.sidebar.expander("⏱ 左：タイム解析", expanded=True):
    i_place = st.text_input("レース場", value="住之江")
    i_race = st.text_input("レース番号", value="12R")
    t_cols = st.columns(3)
    raw_t = [t_cols[i%3].number_input(f"{i+1}号", 6.0, 7.0, 6.50+(i*0.01), 0.01, format="%.2f", key=f"r{i}") for i in range(6)]
    o_cols = st.columns(3)
    offs = [o_cols[i%3].number_input(f"{i+1}補正", -0.5, 0.5, (-0.03 if i==0 else 0.0), 0.01, format="%.2f", key=f"o{i}") for i in range(6)]

with st.sidebar.expander("💎 右：3人の判定", expanded=True):
    i_exp = st.slider("一果期待値", 30, 100, 78)
    i_msg = st.text_input("一果コメント", "補正タイム抜群！")
    h_eval = st.text_input("初音格付け", "1=◯, 4=△")
    h_msg = st.text_input("初音コメント", "期待配当の歪みあり。")
    k_eval = st.selectbox("キイナ穴", ["見", "GO", "買わなきゃ損！"], index=2)
    k_msg = st.text_input("キイナコメント", "4が凹めば5が来る！")

with st.sidebar.expander("🤝 下：合議", expanded=True):
    total_title = st.text_input("タイトル", "1頭固定の鉄板！")
    total_msg = st.text_area("詳細", "3人の見解が一致しました。")

# 3. 計算
final_t = [round(raw_t[i] + offs[i], 2) for i in range(6)]
sorted_u = sorted(list(set(final_t)))
best_t = sorted_u[0]
second_t = sorted_u[1] if len(sorted_u) > 1 else best_t

def get_style(t):
    if t == best_t: return "background:#ef4444; color:white;"
    if t == second_t: return "background:#fef08a; color:#854d0e;"
    return "background:white; color:#333;"

# 4. デザイン (CSS)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Kosugi+Maru&family=Yomogi&display=swap');
    .stApp { background-color: #f0f4f8; }
    .paper { background: white !important; width: 920px !important; margin: 0 auto; padding: 30px; border: 2px solid #333; box-shadow: 10px 10px 0px #cbd5e0; color: #333; }
    .n-grid { display: flex !important; flex-wrap: nowrap !important; gap: 15px !important; align-items: stretch !important; }
    .n-box { border: 2px solid #333 !important; border-radius: 8px; padding: 12px; background: #fff; margin-bottom: 15px; }
    .n-title { font-weight: bold; border-bottom: 2px dashed #333; margin-bottom: 10px; font-size: 16px; }
    .n-table { width: 100%; border-collapse: collapse; text-align: center; font-size: 14px; }
    .n-table th { background: #edf2f7; border: 1px solid #333; padding: 3px; font-size: 10px; }
    .n-table td { border: 1px solid #333; padding: 6px; font-weight: bold; }
    .talk { display: flex; gap: 8px; background: #fefce8; padding: 8px; border-radius: 8px; border: 1px solid #fef08a; font-family: 'Yomogi', cursive; font-size: 13px; margin-bottom: 5px; }
    .face { width: 32px; height: 32px; border-radius: 50%; border: 1px solid #333; background: #fff; display: flex; align-items: center; justify-content: center; font-size: 8px; flex-shrink: 0; font-family: 'Kosugi Maru'; }
</style>
""", unsafe_allow_html=True)

# 5. HTML構築
needle = (i_exp - 50) * 1.8
raw_tds = "".join(["<td>{:.2f}</td>".format(t) for t in raw_t])
final_tds = "".join(['<td style="{}">{:.2f}</td>'.format(get_style(t), t) for t in final_t])

full_html = """
<div class="paper">
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 4px double #333; padding-bottom: 10px; margin-bottom: 20px;">
        <div style="font-size: 10px;">3年1組<br>BOAT STRIKE!</div>
        <div style="background: linear-gradient(to right, #ffecd2, #fcb69f); padding: 5px 30px; border: 2px solid #333; border-radius: 40px; font-size: 30px; font-weight: bold;">Birthstones新聞</div>
        <div style="text-align: right; font-size: 10px;">{date} 第33号</div>
    </div>

    <div class="n-grid">
        <div style="width: 530px;">
            <div class="n-box" style="background: #f8fafc; height: 100%;">
                <div class="n-title">📊 解析：展示タイム生データ</div>
                <p style="font-size: 11px; margin-bottom: 4px;">会場：{place} {race}</p>
                <table class="n-table">
                    <tr><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th></tr>
                    <tr>{raw}</tr>
                </table>
                <div style="margin-top: 25px;" class="n-title">🔍 独自：補正タイム解析</div>
                <div style="background: white; border: 2px solid #333; border-radius: 6px; padding: 10px;">
                    <table class="n-table">
                        <tr><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th></tr>
                        <tr>{final}</tr>
                    </table>
                    <div style="margin-top: 8px; font-size: 10px;">
                        <span style="color:#ef4444;">■</span>1番時計 <span style="color:#d69e2e;">■</span>2番時計
                    </div>
                </div>
            </div>
        </div>

        <div style="width: 330px;">
            <div class="n-box" style="background: #fffdf5; border-color: #f59e0b; height: 100%;">
                <div class="n-title" style="color: #854d0e;">💬 放課後トーク</div>
                <div style="display: flex; align-items: center; justify-content: center; gap: 10px; margin-bottom: 10px; background:white; border:1px solid #fef08a; border-radius:8px; padding:5px;">
                    <div style="position: relative; width: 80px; height: 45px; border-bottom: 2px solid #333; overflow: hidden;">
                        <div style="width: 80px; height: 80px; border-radius: 50%; border: 8px solid #e2e8f0; border-bottom-color: transparent; border-left-color: #f87171; transform: rotate(45deg);"></div>
                        <div style="position: absolute; bottom: 0; left: 50%; width: 2px; height: 35px; background: #1a1a1a; transform-origin: bottom center; transform: translateX(-50%) rotate({needle}deg);"></div>
                    </div>
                    <div style="font-size: 20px; font-weight: bold; color: #ef4444;">{exp}%</div>
                </div>
                <div class="talk"><div class="face">一果</div>{i_msg}</div>
                <div style="background: #1e293b; color: white; padding: 2px; text-align: center; border-radius: 4px; font-size: 11px; margin: 8px 0 4px 0;">初音：{h_eval}</div>
                <div class="talk" style="background:#f0f9ff;"><div class="face">初音</div>{h_msg}</div>
                <div style="background: #ef4444; color: white; padding: 2px; text-align: center; border-radius: 4px; font-size: 11px; margin: 8px 0 4px 0;">キイナ：{k_eval}</div>
                <div class="talk" style="background:white;"><div class="face">キイナ</div>{k_msg}</div>
            </div>
        </div>
    </div>

    <div class="n-box" style="background: #f8fafc; border: 3px double #333; margin-top: 15px;">
        <div class="n-title">🤝 結論：合議メモ</div>
        <div style="padding: 12px; background: white; border: 1.5px dashed #333; border-radius: 6px;">
            <div style="font-weight: bold; color: #dc2626; font-size: 15px;">{title}</div>
            <div style="font-size: 13px; line-height: 1.5; font-family: 'Yomogi', cursive;">{msg}</div>
        </div>
    </div>
</div>
""".format(
    date=formatted_date, place=i_place, race=i_race, raw=raw_tds, 
    final=final_tds, needle=needle, exp=i_exp, i_msg=i_msg, 
    h_eval=h_eval, h_msg=h_msg, k_eval=k_eval, k_msg=k_msg, 
    title=total_title, msg=total_text
)

st.markdown(full_html, unsafe_allow_html=True)
