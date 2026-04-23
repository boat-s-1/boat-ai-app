import streamlit as st
import datetime

# ページ設定
st.set_page_config(page_title="Birthstones新聞 生成App", layout="wide")

# 日付
today = datetime.date.today()
formatted_date = today.strftime("%Y年%m月%d日")

# --- 1. サイドバー：入力センター（ここですべての値を制御します） ---
st.sidebar.header("📊 新聞データ入力")

with st.sidebar.expander("⏱ 左：展示タイム解析", expanded=True):
    i_place = st.text_input("レース場", value="住之江")
    i_race = st.text_input("レース番号", value="12R")
    st.write("【生展示タイム】")
    t_cols = st.columns(3)
    raw_times = [t_cols[i % 3].number_input(f"{i+1}号艇", value=6.50 + (i*0.02), step=0.01, format="%.2f", key=f"raw_{i}") for i in range(6)]
    st.write("【独自補正値】")
    h_cols = st.columns(3)
    offsets = [h_cols[i % 3].number_input(f"{i+1}補正", value=(-0.03 if i == 0 else 0.00), step=0.01, format="%.2f", key=f"off_{i}") for i in range(6)]

with st.sidebar.expander("💎 右：3人の判定", expanded=True):
    i_exp = st.slider("一果：期待値 (%)", 30, 100, 78)
    i_text = st.text_area("一果：判定", value="補正タイムが抜群です！一果にお任せ！")
    h_eval = st.text_input("初音：格付け", value="1=◯, 4=△, 5=✖️")
    h_text = st.text_area("初音：分析", value="タイム通り1号艇が軸。")
    k_eval = st.selectbox("キイナ：穴判定", ["見", "GO", "買わなきゃ損！"], index=2)
    k_text = st.text_area("キイナ：予感", value="4が凹めば5が突き抜ける！")

with st.sidebar.expander("🤝 下：トータル意見（3人の合議）", expanded=True):
    total_verdict = st.text_input("結論タイトル", value="1頭固定の鉄板レース！")
    total_text = st.text_area("合議の詳細", value="3人の見解が一致しました。イン逃げ確率は極めて高いです！")

# --- 2. 計算ロジック ---
final_times = [round(raw_times[i] + offsets[i], 2) for i in range(6)]
sorted_unique = sorted(list(set(final_times)))
best_time = sorted_unique[0]
second_best = sorted_unique[1] if len(sorted_unique) > 1 else None

def get_t_style(t):
    if t == best_time: return "background:#ef4444; color:white; border:1px solid #333;" # 1位（赤）
    if t == second_best: return "background:#fef08a; color:#854d0e; border:1px solid #333;" # 2位（黄）
    return "background:white; color:#333;"

# --- 3. CSSスタイル定義（分離して安全に読み込み） ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Kosugi+Maru&family=Yomogi&display=swap');
    .stApp { font-family: 'Kosugi Maru', sans-serif; background-color: #f0f4f8; }
    
    /* 新聞の紙 */
    .newspaper-sheet {
        background-color: white !important;
        width: 920px !important; margin: 0 auto !important;
        padding: 40px !important; border: 2px solid #333 !important;
        box-shadow: 12px 12px 0px #cbd5e0 !important; color: #1a1a1a !important;
    }
    
    /* メイングリッド（左解析・右キャラ並列） */
    .news-grid { display: flex !important; gap: 20px !important; margin-bottom: 20px !important; }
    .col-left { flex: 1.7 !important; }
    .col-right { flex: 1.3 !important; }
    
    /* ボックス装飾 */
    .memo-box { border: 2px solid #333 !important; border-radius: 12px !important; padding: 15px !important; background: #fff !important; margin-bottom: 15px !important; }
    .box-title { font-weight: bold; border-bottom: 2px dashed #333; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; font-size: 17px; }
    
    /* テーブル */
    .data-table { width: 100%; border-collapse: collapse; margin-top: 10px; }
    .data-table th { background: #edf2f7; border: 1px solid #333; padding: 6px; font-size: 11px; }
    .data-table td { border: 1px solid #333; padding: 8px; text-align: center; font-weight: bold; font-size: 16px; }

    /* 吹き出し */
    .voice-bubble { display: flex; gap: 10px; background: #fefce8; padding: 10px; border-radius: 10px; border: 1px solid #fef08a; font-family: 'Yomogi', cursive; font-size: 14px; margin-top: 10px; }
    .char-badge { width: 40px; height: 40px; border-radius: 50%; border: 1.5px solid #333; background: #fff; display: flex; align-items: center; justify-content: center; font-size: 10px; flex-shrink: 0; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 4. HTML構築（これが「しょぼさ」を消す鍵です） ---
needle_deg = (i_exp - 50) * 1.8
raw_tds = "".join([f"<td>{t:.2f}</td>" for t in raw_times])
final_tds = "".join([f'<td style="{get_t_style(t)}">{t:.2f}</td>' for t in final_times])

full_html = f"""
<div class="newspaper-sheet">
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 4px double #333; padding-bottom: 15px; margin-bottom: 25px;">
        <div style="font-size: 12px;">3年1組<br>BOAT STRIKE! 係</div>
        <div style="background: linear-gradient(to right, #ffecd2, #fcb69f); padding: 5px 40px; border: 2px solid #333; border-radius: 50px; font-size: 36px; font-weight: bold; color: #1a1a1a;">Birthstones新聞</div>
        <div style="text-align: right; font-size: 12px;">{formatted_date} 第22号<br>🧭 きずな班 編集</div>
    </div>

    <div class="news-grid">
        <div class="col-left">
            <div class="memo-box" style="background: #f8fafc; height: 100%; margin-bottom: 0;">
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
                    <div style="margin-top: 10px; display: flex; gap: 15px; font-size: 11px; font-weight: bold;">
                        <span><b style="color:#ef4444;">■</b> 1番時計</span><span><b style="color:#d69e2e;">■</b> 2番時計</span>
                    </div>
                </div>
                <p style="font-size: 11px; color: #64748b; margin-top: 15px;">※場別・風速データを考慮した独自解析値</p>
            </div>
        </div>

        <div class="col-right">
            <div class="memo-box" style="background: #fffdf5; border-color: #f59e0b; height: 100%; margin-bottom: 0;">
                <div class="box-title" style="color: #854d0e;">💬 3人の放課後メモ</div>
                
                <div style="display: flex; align-items: center; justify-content: space-around; margin-bottom: 12px; border: 1px solid #fef08a; padding: 8px; border-radius: 12px; background: white;">
                    <div style="position: relative; width: 110px; height: 60px; border-bottom: 2px solid #333; overflow: hidden;">
                        <div style="width: 110px; height: 110px; border-radius: 50%; border: 10px solid #e2e8f0; border-bottom-color: transparent; border-left-color: #f87171; border-top-color: #fca5a5; transform: rotate(45deg);"></div>
                        <div style="position: absolute; bottom: 0; left: 50%; width: 3px; height: 50px; background: #1a1a1a; transform-origin: bottom center; transform: translateX(-50%) rotate({needle_deg}deg);"></div>
                    </div>
                    <div style="font-size: 28px; font-weight: bold; color: #ef4444;">一果:{i_exp}%</div>
                </div>
                <div class="voice-bubble"><div class="char-badge">一果</div>「{i_text}」</div>

                <div style="background: #1e293b; color: white; padding: 3px; text-align: center; border-radius: 4px; font-size: 13px; font-weight: bold; margin: 12px 0 6px 0;">初音格付け：{h_eval}</div>
                <div class="voice-bubble" style="background:#f0f9ff; border-color:#3b82f6;"><div class="char-circle">初音</div>「{h_text}」</div>

                <div style="background: #ef4444; color: white; padding: 3px; text-align: center; border-radius: 4px; font-size: 13px; font-weight: bold; margin: 12px 0 6px 0;">キイナ判定：{k_eval}</div>
                <div class="voice-bubble" style="background:white;"><div class="char-circle">キイナ</div>「{k_text}」</div>
            </div>
        </div>
    </div>

    <div class="memo-box" style="background: #f8fafc; border: 3px double #333; margin-top: 20px;">
        <div class="box-title">🤝 结论：3人のトータル意見</div>
        <div style="padding: 15px; background: white; border: 1.5px dashed #333; border-radius: 8px;">
            <div style="font-weight: bold; color: #dc2626; margin-bottom: 5px; font-size: 16px;">{total_verdict}</div>
            <div style="font-size: 14px; line-height: 1.6; font-family: 'Yomogi', cursive;">{total_text}</div>
        </div>
    </div>
</div>
"""

# 全体を一括描画（隙間をゼロにします）
st.markdown(full_html, unsafe_allow_html=True)
