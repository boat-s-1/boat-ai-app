import streamlit as st
import datetime

# ページ設定
st.set_page_config(page_title="Birthstones新聞 生成App", layout="wide")

# 日付
today = datetime.date.today()
formatted_date = today.strftime("%Y年%m月%d日")

# --- 1. サイドバー：データ入力 ---
st.sidebar.header("📊 新聞データ入力センター")

with st.sidebar.expander("⏱ 左エリア：展示タイム解析", expanded=True):
    i_place = st.text_input("レース場", value="住之江")
    i_race = st.text_input("レース番号", value="12R")
    st.write("【生展示タイム】")
    t_cols = st.columns(3)
    raw_t = [t_cols[i % 3].number_input(f"{i+1}号艇", value=6.50 + (i*0.02), step=0.01, format="%.2f", key=f"r_val_{i}") for i in range(6)]
    st.write("【独自補正値】")
    h_cols = st.columns(3)
    offs = [h_cols[i % 3].number_input(f"{i+1}補正", value=(-0.03 if i == 0 else 0.00), step=0.01, format="%.2f", key=f"o_val_{i}") for i in range(6)]

with st.sidebar.expander("💎 右エリア：3人の個別判定", expanded=True):
    i_exp = st.slider("一果：逃げ期待値 (%)", 30, 100, 78)
    i_text = st.text_area("一果：一言", value="補正タイムが抜群だよ！一果にお任せ！")
    h_eval = st.text_input("初音：格付け", value="1=◯, 4=△, 5=✖️")
    h_text = st.text_area("初音：分析", value="期待配当の歪みは2,500円。4-5の連絡みも。")
    k_eval = st.selectbox("キイナ：穴判定", ["見", "GO", "買わなきゃ損！"], index=2)
    k_text = st.text_area("キイナ：予感", value="4が凹めば5が突き抜ける！")

with st.sidebar.expander("🤝 最下部：3人の合議", expanded=True):
    total_verdict = st.text_input("最終結論タイトル", value="1頭固定の鉄板レース！")
    total_text = st.text_area("合議の詳細", value="3人の見解が一致。イン逃げ確率は極めて高いです！")

# --- 2. ロジック計算 ---
final_t = [round(raw_t[i] + offs[i], 2) for i in range(6)]
sorted_unique = sorted(list(set(final_t)))
best_t = sorted_unique[0]
second_t = sorted_unique[1] if len(sorted_unique) > 1 else None

def get_t_style(t):
    if t == best_t: return "background:#ef4444 !important; color:white !important; border:1px solid #333 !important;"
    if t == second_t: return "background:#fef08a !important; color:#854d0e !important; border:1px solid #333 !important;"
    return "background:white !important; color:#333 !important;"

# --- 3. CSSスタイル定義（完全に分離して先に読み込み） ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Kosugi+Maru&family=Yomogi&display=swap');
    .stApp { font-family: 'Kosugi Maru', sans-serif; background-color: #f0f4f8; }
    
    .paper-frame {
        background-color: white !important; width: 920px !important; margin: 0 auto !important;
        padding: 40px !important; border: 2px solid #333 !important;
        box-shadow: 12px 12px 0px #cbd5e0 !important; color: #1a1a1a !important;
    }
    
    .news-grid { display: flex !important; gap: 20px !important; margin-bottom: 20px !important; }
    .news-box { border: 2px solid #333 !important; border-radius: 12px !important; padding: 15px !important; background: #fff !important; position: relative; }
    .box-title { font-weight: bold; border-bottom: 2px dashed #333; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; font-size: 17px; }
    
    .data-table { width: 100%; border-collapse: collapse; margin-top: 10px; }
    .data-table th { background: #edf2f7; border: 1px solid #333; padding: 4px; font-size: 11px; }
    .data-table td { border: 1px solid #333; padding: 6px; text-align: center; font-weight: bold; font-size: 15px; }

    .meter-box { position: relative; width: 110px; height: 60px; border-bottom: 2px solid #333; overflow: hidden; margin: 0 auto; }
    .fukidashi { display: flex; gap: 10px; background: #fefce8; padding: 10px; border-radius: 10px; border: 1px solid #fef08a; font-family: 'Yomogi', cursive; font-size: 14px; margin-top: 10px; }
    .char-circle { width: 40px; height: 40px; border-radius: 50%; border: 1.5px solid #333; background: #fff; display: flex; align-items: center; justify-content: center; font-size: 10px; flex-shrink: 0; }
</style>
""", unsafe_allow_html=True)

# --- 4. HTML構築（各パーツを安全に組み立て） ---
needle_deg = (i_exp - 50) * 1.8
raw_tds = "".join([f"<td>{t:.2f}</td>" for t in raw_t])
final_tds = "".join([f'<td style="{get_t_style(t)}">{t:.2f}</td>' for t in final_t])

html_body = f"""
<div class="paper-frame">
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 4px double #333; padding-bottom: 15px; margin-bottom: 25px;">
        <div style="font-size: 12px;">3年1組<br>BOAT STRIKE! 係</div>
        <div style="background: linear-gradient(to right, #ffecd2, #fcb69f); padding: 5px 40px; border: 2px solid #333; border-radius: 50px; font-size: 36px; font-weight: bold;">Birthstones新聞</div>
        <div style="text-align: right; font-size: 12px;">{formatted_date} 第21号<br>🧭 きずな班 編集</div>
    </div>

    <div class="news-grid">
        <div style="flex: 1.7;">
            <div class="news-box" style="background: #f8fafc; min-height: 520px;">
                <div class="box-title">📊 公式：展示タイム生データ</div>
                <p style="font-size: 12px; margin-bottom: 5px;">会場：ボートレース{i_place} {i_race}</p>
                <table class="data-table">
                    <tr><th>1号</th><th>2号</th><th>3号</th><th>4号</th><th>5号</th><th>6号</th></tr>
                    <tr>{raw_tds}</tr>
                </table>
                <div style="margin-top: 30px;" class="box-title">🔍 独自：補正展示タイム解析</div>
                <div style="background: #fff; border: 2px solid #333; border-radius: 8px; padding: 15px;">
                    <table class="data-table">
                        <tr><th>1号</th><th>2号</th><th>3号</th><th>4号</th><th>5号</th><th>6号</th></tr>
                        <tr>{final_tds}</tr>
                    </table>
                    <div style="margin-top: 10px; display: flex; gap: 15px; font-size: 11px; font-weight: bold;">
                        <span><b style="color:#ef4444;">■</b> 1番時計</span><span><b style="color:#eab308;">■</b> 2番時計</span>
                    </div>
                </div>
                <p style="font-size: 11px; color: #64748b; margin-top: 15px;">※独自のイン補正・場補正を加味した実戦タイムです。</p>
            </div>
        </div>

        <div style="flex: 1.3;">
            <div class="news-box" style="border-color: #f59e0b; background: #fffcf5;">
                <div class="box-title" style="color: #f59e0b;">🚩 一果のイン判定</div>
                <div style="display: flex; align-items: center; justify-content: space-around; margin: 5px 0;">
                    <div class="meter-box">
                        <div style="width: 110px; height: 110px; border-radius: 50%; border: 10px solid #e2e8f0; border-bottom-color: transparent; border-left-color: #f87171; border-top-color: #fca5a5; transform: rotate(45deg);"></div>
                        <div style="position: absolute; bottom: 0; left: 50%; width: 3px; height: 50px; background: #1a1a1a; transform-origin: bottom center; transform: translateX(-50%) rotate({needle_deg}deg);"></div>
                    </div>
                    <div style="text-align: center; font-size: 26px; font-weight: bold; color: #ef4444;">{i_exp}%</div>
                </div>
                <div class="fukidashi"><div class="char-circle">一果</div><div>「{i_text}」</div></div>
            </div>
            <div class="news-box" style="border-color: #3b82f6; background: #f0f9ff;">
                <div class="box-title" style="color: #3b82f6;">📚 初音の精密分析</div>
                <div style="background: #1e293b; color: white; padding: 3px; text-align: center; border-radius: 4px; font-size: 14px; font-weight: bold;">{h_eval}</div>
                <div class="fukidashi" style="background: #f8fafc;"><div class="char-circle">初音</div><div>「{h_text}」</div></div>
            </div>
            <div class="news-box" style="border-color: #eab308; background: #fffdf0;">
                <div class="box-title" style="color: #854d0e;">⚡ キイナの穴狙い</div>
                <div style="text-align: center; background: #ef4444; color: white; padding: 3px; border-radius: 4px; font-weight: bold;">{k_eval}</div>
                <div class="fukidashi" style="background: #fff;"><div class="char-circle">キイナ</div><div>「{k_text}」</div></div>
            </div>
        </div>
    </div>

    <div class="news-box" style="background: #f8fafc; border: 3px double #333;">
        <div class="box-title">🤝 3人の放課後ミーティング</div>
        <div style="margin-top: 5px; padding: 15px; background: white; border: 1.5px dashed #333; border-radius: 8px;">
            <div style="font-weight: bold; color: #dc2626; margin-bottom: 5px; font-size: 16px;">{total_verdict}</div>
            <div style="font-size: 14px; line-height: 1.6; font-family: 'Yomogi', cursive;">{total_text}</div>
        </div>
    </div>
</div>
"""

st.markdown(html_body, unsafe_allow_html=True)
