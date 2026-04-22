import streamlit as st

# 新聞全体のスタイル設定
st.markdown("""
<style>
    .newspaper-container {
        background-color: #f9f9f9;
        padding: 10px;
        border: 1px solid #ddd;
    }
    .section-card {
        background: white;
        border: 2px solid #333;
        border-radius: 8px;
        margin-bottom: 15px;
        padding: 15px;
    }
    .kiina-header { background-color: #f1c40f; color: #333; padding: 5px; font-weight: bold; border-radius: 4px; }
    .hatsune-header { background-color: #3498db; color: white; padding: 5px; font-weight: bold; border-radius: 4px; }
    .status-badge { font-size: 20px; font-weight: bold; color: #e67e22; border: 2px solid #e67e22; padding: 2px 10px; transform: rotate(-5deg); display: inline-block; }
</style>
""", unsafe_allow_html=True)

with st.container():
    st.write("### BOAT STRIKE データ新聞（プロトタイプ）")
    
    # 1. 一果セクション (簡略版)
    st.markdown("""
    <div class="section-card">
        <div style="display:flex; justify-content:space-between;"><b>一果のイン逃げ判定</b> <span style="color:red;">住之江 11R</span></div>
        <div style="text-align:center; padding:10px;">
            <div style="font-size:12px;">場平均より</div>
            <div style="font-size:40px; font-weight:bold; color:red;">+22%</div>
            <div class="status-badge">鬼絞り</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. キイナセクション
    st.markdown("""
    <div class="section-card">
        <div class="kiina-header">⚡ キイナの5アタマ穴狙い！</div>
        <div style="display:flex; align-items:center; margin-top:10px;">
            <div style="font-size:30px; font-weight:bold; color:#e67e22; margin-right:15px;">買わなきゃ損！</div>
            <div style="font-size:13px;">「4号艇が凹む予感！5号艇の伸び足なら一気に飲み込めるよ！」</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3. 初音セクション
    st.markdown("""
    <div class="section-card">
        <div class="hatsune-header">📊 初音の客観的数値</div>
        <table style="width:100%; font-size:12px; margin-top:10px; border-collapse:collapse;">
            <tr style="border-bottom:1px solid #eee;"><th>艇</th><th>評価</th><th>補正展示</th><th>配当予測</th></tr>
            <tr style="text-align:center;"><td>1</td><td>◎</td><td>6.62</td><td rowspan="6">中央値:<br>1,190円</td></tr>
            <tr style="text-align:center;"><td>5</td><td>穴</td><td>6.58</td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)
