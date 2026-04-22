import streamlit as st
import datetime

# ページ設定
st.set_page_config(page_title="Birthstones新聞 生成App", layout="wide")

# 今日の日付を取得
today = datetime.date.today()
formatted_date = today.strftime("%Y年%m月%d日")

# --- 1. スタイル定義 (学級新聞風 CSS) ---
# image_9.pngの温かみ、角丸枠、アイコン、2カラムレイアウトを再現
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Kosugi+Maru&display=swap');

    /* 全体のフォントと背景 */
    .stApp {{
        font-family: 'Kosugi Maru', sans-serif; /* 手書きに近い丸文字 */
        background-color: #e2e8f0; /* 机の色 */
        color: #1a1a1a;
    }}

    /* 新聞全体のコンテナ（紙） */
    .paper-container {{
        background-color: #ffffff; /* 紙の色 */
        width: 1000px; /* image_9.pngに近い横幅 */
        margin: 20px auto;
        padding: 30px;
        border-radius: 8px; /* わずかに角丸 */
        box-shadow: 5px 10px 20px rgba(0,0,0,0.15); /* 新聞の影（立体感） */
        position: relative;
    }}

    /* --- ヘッダー（タイトルエリア） --- */
    /* image_9.pngのカラフルな帯と方位磁針アイコンを再現 */
    .header-area {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 25px;
        position: relative;
    }}
    .date-vol {{
        font-size: 14px;
        color: #4b5563;
        text-align: right;
    }}
    .title-banner {{
        background: linear-gradient(90deg, #ff9a9e 0%, #fad0c4 99%, #fad0c4 100%); /* image_9.pngのようなグラデ */
        padding: 10px 30px;
        border-radius: 10px;
        box-shadow: 2px 4px 6px rgba(0,0,0,0.1);
        position: absolute;
        left: 50%;
        transform: translateX(-50%);
        top: -15px;
    }}
    .main-title {{
        font-size: 32px;
        font-weight: bold;
        color: #1a1a1a;
        margin: 0;
        letter-spacing: 2px;
    }}
    .title-decor {{
        font-size: 24px;
        margin: 0 10px;
    }}

    /* --- メインコンテンツ（2カラム） --- */
    /* image_9.pngの左右非対称な配置を再現 */
    .content-columns {{
        display: flex;
        gap: 20px;
    }}
    /* 左側（大きなメインコーナー） */
    .left-column {{
        flex: 2;
        display: flex;
        flex-direction: column;
        gap: 20px;
    }}
    /* 右側（3人の小さなコーナー） */
    .right-column {{
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 20px;
    }}

    /* --- 各コーナーの共通スタイル --- */
    /* image_9.pngの角丸の枠線を再現 */
    .news-box {{
        background-color: #fff;
        border: 2px solid #333; /* 太めの枠線 */
        border-radius: 12px; /* 柔らかい角丸 */
        padding: 20px;
        box-shadow: 2px 2px 4px rgba(0,0,0,0.05);
    }}
    .box-header {{
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 15px;
        padding-bottom: 8px;
        border-bottom: 1px dashed #999; /* 下部の点線 */
    }}
    .box-icon {{
        font-size: 24px;
    }}
    .box-title {{
        font-size: 20px;
        font-weight: bold;
        color: #1a1a1a;
        margin: 0;
    }}

    /* --- 一果コーナー（メイン） --- */
    /* image_9.pngの特集コーナーのような存在感 */
    .ichika-score-box {{
        text-align: center;
        padding: 15px;
        border: 1px solid #ccc;
        border-radius: 8px;
        background-color: #fafafa;
        margin-bottom: 15px;
    }}
    .diff-label {{ font-size: 16px; color: #666; }}
    .diff-value {{ font-size: 50px; font-weight: bold; color: #ef4444; line-height: 1; margin: 10px 0; }}
    .stamp {{
        border: 3px double #ff0000; color: #ff0000;
        font-size: 22px; font-weight: bold;
        padding: 5px 15px; border-radius: 5px;
        transform: rotate(-10deg); display: inline-block;
        margin-top: 10px;
    }}
    .comment-box {{
        display: flex; align-items: flex-start; gap: 10px;
        background-color: #fff0f0; padding: 10px; border-radius: 5px;
        font-size: 14px; border-left: 5px solid #ff4b4b;
    }}
    .reporter-icon {{
        width: 50px; height: 50px; background: #eee; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 10px; text-align: center; color: #666; border: 1px solid #ccc;
    }}

    /* --- 初音・キイナコーナー（右側） --- */
    /* image_9.pngのコンパクトなコーナー表示 */
    .hatsune-box {{
        border-color: #3b82f6; /* コーナーごとの色 */
    }}
    .kiina-box {{
        border-color: #f59e0b; /* コーナーごとの色 */
    }}
    .info-list {{
        list-style: none; padding: 0; margin: 0;
        font-size: 14px; color: #4b5563;
    }}
    .info-list li {{
        margin-bottom: 8px; display: flex; align-items: center; gap: 8px;
    }}
    .list-icon {{ font-size: 16px; }}

</style>
""", unsafe_allow_html=True)

# --- 2. サイドバー (データ入力) ---
st.sidebar.header("📝 新聞記者・データ入力")

with st.sidebar.expander("一果（イン逃げ）の報告", expanded=True):
    # image_9.pngの場所、天気のような基本情報
    i_place = st.text_input("開催場", value="住之江", key="i_p")
    i_race = st.text_input("レース", value="11R", key="i_r")
    i_weather = st.text_input("天気", value="晴れ☀️", key="i_w")
    st.divider()
    # 数値データ
    i_avg_rate = st.number_input("場平均逃げ率(%)", 0, 100, 52, key="i_a")
    i_expect = st.number_input("イン逃げ期待値(%)", 0, 100, 74, key="i_e")
    i_msg = st.text_area("一果の一言コメント", value="住之江の平均よりかなり高いね！壁役の2号艇も安定してるし、ここは一果にお任せ！", key="i_m")

with st.sidebar.expander("初音（客観データ）の報告", expanded=True):
    h_bet = st.text_input("初音の推奨買い目", value="1-4-全", key="h_b")
    h_median = st.number_input("配当中央値(円)", value=1190, key="h_me")
    # image_9.pngのクイズのような箇条書き情報
    h_info = st.text_area("初音のデータ箇条書き", value="・補正展示タイム1位(6.62)\n・当地勝率1位(7.45)\n・女子戦的中率68%", key="h_i")

with st.sidebar.expander("キイナ（穴狙い）の報告", expanded=True):
    k_eval = st.selectbox("キイナの穴判定", ["買わなきゃ損！", "GO", "見（ケン）"], index=0, key="k_v")
    k_msg = st.text_area("キイナの一言コメント", value="4号艇が凹む予感！5号艇の伸び足なら一気に飲み込めるよ！", key="k_m")


# --- 3. メイン画面 (学級新聞風プレビュー生成) ---
st.title("📰 Birthstones新聞 プレビュー画面")
st.write("学級新聞のような、温かみのあるレイアウトにしました（このまま画像出力が可能です）")

# 計算ロジック
diff = i_expect - i_avg_rate
diff_color = "#ef4444" if diff >= 0 else "#1f77b4"
diff_text = f"+{diff}%" if diff >= 0 else f"{diff}%"

# 初音の箇条書きをリストに変換
hatsune_info_list = h_info.split('\n')

# 新聞全体のHTMLを構築
newspaper_html = f"""
<div class="paper-container">
    <div class="header-area">
        <div>✨💎✨</div> <div class="title-banner">
            <span class="title-decor">⚓️</span> <span class="main-title">Birthstones新聞</span>
            <span class="title-decor">🧭</span> </div>
        <div class="date-vol">
            {formatted_date} 第15号
        </div>
    </div>

    <div class="content-columns">
        
        <div class="left-column">
            <div class="news-box">
                <div class="box-header">
                    <span class="box-icon">☀️</span> <span class="box-title">特集：一果のイン逃げ判定</span>
                    <span style="color:#ef4444; margin-left: auto;">{i_place} {i_race}</span>
                </div>
                
                <p style="font-size:14px; color:#4b5563;">
                    場所：{i_place} ボートレース場<br>
                    天気：{i_weather}
                </p>
                
                <div class="ichika-score-box">
                    <div class="diff-label">場平均（{i_avg_rate}%）より</div>
                    <div class="diff-value" style="color:{diff_color};">{diff_text}</div>
                    <div class="diff-label">イン逃げ期待値：{i_expect}%</div>
                    <div class="stamp">鬼絞り（鉄板）</div>
                </div>

                <div class="comment-box">
                    <div class="reporter-icon">一果<br>Icon</div>
                    「{i_msg}」
                </div>
            </div>
        </div>
        
        <div class="right-column">
            <div class="news-box hatsune-box">
                <div class="box-header">
                    <span class="box-icon">📊</span> <span class="box-title" style="color:#3b82f6;">初音の客観的数値</span>
                </div>
                
                <div style="background-color:#1e293b; color:#fff; padding:10px; border-radius:5px; text-align:center; font-size:18px; font-weight:bold; margin-bottom:10px;">
                    買い目：{h_bet}
                </div>
                
                <ul class="info-list">
                    {" ".join([f"<li><span class='list-icon'>📌</span> {info}</li>" for info in hatsune_info_list])}
                    <li style="margin-top:10px; font-weight:bold; color:#1e293b;">
                        配当中央値：{h_median}円
                    </li>
                </ul>
            </div>
            
            <div class="news-box kiina-box">
                <div class="box-header">
                    <span class="box-icon">⚡️</span> <span class="box-title" style="color:#f59e0b;">キイナの5アタマ穴狙い！</span>
                </div>
                
                <div style="text-align:center; margin-bottom:10px;">
                    <div class="stamp" style="border-color:#f59e0b; color:#f59e0b; font-size:18px; transform: rotate(-5deg);">
                        {k_eval}
                    </div>
                </div>
                
                <div class="comment-box" style="background-color:#fffbeb; border-left-color:#f59e0b; font-size:13px;">
                    「{k_m}」
                </div>
            </div>
        </div>
        
    </div>
</div>
"""

# unsafe_allow_html=True を指定して一気に描画
st.markdown(newspaper_html, unsafe_allow_html=True)

st.divider()
st.info("💡 このプレビュー画面を画像保存して、noteやXに投稿できます。")
