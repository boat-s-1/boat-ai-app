import streamlit as st
import datetime

# ページ設定
st.set_page_config(page_title="Birthstones新聞 生成App", layout="wide")

# 今日の日付を取得
today = datetime.date.today()
formatted_date = today.strftime("%Y年%m月%d日")

# --- 1. サイドバー：データ入力 ---
st.sidebar.header("📝 記事の内容を書こう！")

with st.sidebar.expander("一果の「特集」記事", expanded=True):
    i_place = st.text_input("レース場", value="住之江", key="i_p")
    i_race = st.text_input("レース番号", value="11R", key="i_r")
    i_avg = st.number_input("場平均(%)", 0, 100, 52, key="i_a")
    i_exp = st.number_input("期待値(%)", 0, 100, 74, key="i_e")
    i_text = st.text_area("一果のメッセージ", value="平均よりかなり高いよ！壁役も安定してるし、ここは一果にお任せ！", key="i_t")

with st.sidebar.expander("初音の「お役立ち」コーナー", expanded=True):
    h_bet = st.text_input("推奨買い目", value="1-4-全", key="h_b")
    h_data = st.text_area("データ箇条書き", value="・補正タイム1位\n・当地勝率No.1\n・期待値MAX", key="h_d")

with st.sidebar.expander("キイナの「一撃」クイズ", expanded=True):
    k_eval = st.selectbox("穴判定", ["買わなきゃ損！", "GO", "見（ケン）"], key="k_e")
    k_text = st.text_area("キイナのメッセージ", value="4号艇が凹む予感！5号艇の伸び足なら一気に飲み込めるよ！", key="k_t")

# --- 2. スタイル定義 (学級新聞風 CSS) ---
css_style = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Kosugi+Maru&display=swap');
    .stApp { font-family: 'Kosugi Maru', sans-serif; background-color: #f0f4f8; }
    
    .paper {
        background-color: white; width: 950px; margin: 0 auto; padding: 30px;
        border: 2px solid #333; border-radius: 5px;
        box-shadow: 10px 10px 0px #cbd5e0; position: relative;
    }
    
    /* ヘッダー：お手本の虹色帯とアイコンを再現 */
    .newspaper-header {
        display: flex; justify-content: space-between; align-items: center;
        border-bottom: 3px double #333; padding-bottom: 10px; margin-bottom: 20px;
    }
    .title-banner {
        background: linear-gradient(to right, #ffecd2 0%, #fcb69f 100%);
        padding: 5px 40px; border: 2px solid #333; border-radius: 50px;
        font-size: 32px; font-weight: bold; position: relative;
    }
    
    /* 2カラムレイアウト */
    .main-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; }
    
    /* コーナー共通枠 */
    .box {
        border: 2px solid #4a5568; border-radius: 15px; padding: 15px;
        margin-bottom: 15px; position: relative; background: #fff;
    }
    .box-title {
        background: #edf2f7; border: 1px solid #333; border-radius: 5px;
        display: inline-block; padding: 2px 12px; font-weight: bold;
        margin-bottom: 10px; font-size: 18px;
    }
    
    /* 特集エリア（左） */
    .tokushu { background-color: #fffaf0; border: 3px solid #f6ad55; }
    .score-circle {
        border: 2px dashed #f6ad55; border-radius: 50%; width: 150px; height: 150px;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        margin: 10px auto; background: #fff;
    }
    
    /* キャラクターの吹き出し */
    .fukidashi {
        display: flex; align-items: center; gap: 10px;
        background: #fefcbf; border-radius: 10px; padding: 10px; font-size: 14px;
    }
    .char-icon {
        width: 50px; height: 50px; border-radius: 50%; background: #fff;
        border: 1px solid #333; flex-shrink: 0; font-size: 10px;
        display: flex; align-items: center; justify-content: center;
    }
</style>
"""

# --- 3. メイン描画 ---
st.title("📰 Birthstones新聞 プレビュー")
st.write("お手本 の配置を参考に、3人のコーナーを右側にまとめました。")

diff = i_exp - i_avg
diff_text = f"+{diff}%" if diff >= 0 else f"{diff}%"

content_html = f"""
<div class="paper">
    <div class="newspaper-header">
        <div style="font-size: 24px;">⚓️ ✨</div>
        <div class="title-banner">Birthstones新聞</div>
        <div style="text-align: right; font-size: 14px;">
            {formatted_date} 第15号<br>🧭 3年1組 きずな班
        </div>
    </div>

    <div class="main-grid">
        <div class="tokushu box">
            <div class="box-title">🚩 特集：一果のイン逃げ判定</div>
            <p style="font-size: 14px;">場所：ボートレース{i_place} ({i_race}) / 天気：晴れ☀️</p>
            
            <div style="display: flex; align-items: center; justify-content: space-around;">
                <div class="score-circle">
                    <span style="font-size: 12px;">場平均より</span>
                    <span style="font-size: 32px; font-weight: bold; color: #e53e3e;">{diff_text}</span>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 14px;">期待値：{i_exp}%</div>
                    <div style="border: 2px solid red; color: red; padding: 5px; font-weight: bold; transform: rotate(-5deg); margin-top: 10px;">鬼絞り確定！</div>
                </div>
            </div>
            
            <div class="fukidashi" style="margin-top: 20px;">
                <div class="char-icon">一果</div>
                <div>「{i_text}」</div>
            </div>
        </div>

        <div>
            <div class="box" style="border-color: #4299e1;">
                <div class="box-title" style="background: #ebf8ff;">📝 初音のデータメモ</div>
                <div style="background: #2d3748; color: white; padding: 5px; text-align: center; border-radius: 5px; margin-bottom: 10px;">
                    {h_bet}
                </div>
                <div style="font-size: 13px; line-height: 1.6;">
                    {h_data.replace('\n', '<br>')}
                </div>
            </div>

            <div class="box" style="border-color: #f6e05e;">
                <div class="box-title" style="background: #fffff0;">⚡️ キイナの一撃！</div>
                <div style="text-align: center; font-weight: bold; color: #d69e2e; margin-bottom: 10px;">
                    判定：{k_eval}
                </div>
                <div class="fukidashi" style="background: #fffaf0;">
                    <div class="char-icon">キイナ</div>
                    <div>「{k_text}」</div>
                </div>
            </div>
        </div>
    </div>
</div>
"""

st.markdown(css_style, unsafe_allow_html=True)
st.markdown(content_html, unsafe_allow_html=True)

st.divider()
st.caption("サイドバーの入力を変えると、リアルタイムで新聞が書き換わります。")
