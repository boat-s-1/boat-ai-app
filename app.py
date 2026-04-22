import streamlit as st

def show_ichika_report(field_name, field_avg, current_expectancy, wall_strength):
    diff = current_expectancy - field_avg
    diff_color = "#ff4b4b" if diff >= 0 else "#1f77b4"
    diff_text = f"+{diff}%" if diff >= 0 else f"{diff}%"
    
    # 判定スタンプの決定
    if diff >= 15:
        status = "鬼絞り（鉄板）"
        stamp_color = "#ff0000"
    elif diff >= 5:
        status = "有力"
        stamp_color = "#ff8c00"
    else:
        status = "波乱含み"
        stamp_color = "#707070"

    # HTML/CSSでの新聞風デザイン
    st.markdown(f"""
    <style>
        .report-box {{
            background-color: #ffffff;
            border: 3px solid #333;
            border-radius: 10px;
            padding: 20px;
            font-family: 'Helvetica Neue', Arial, sans-serif;
            max-width: 500px;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #333;
            padding-bottom: 10px;
        }}
        .field-label {{
            background-color: #333;
            color: white;
            padding: 2px 10px;
            border-radius: 5px;
            font-weight: bold;
        }}
        .main-score {{
            text-align: center;
            padding: 20px 0;
        }}
        .diff-value {{
            font-size: 60px;
            font-weight: 900;
            color: {diff_color};
            line-height: 1;
        }}
        .diff-label {{
            font-size: 14px;
            color: #666;
        }}
        .stamp {{
            border: 4px double {stamp_color};
            color: {stamp_color};
            font-size: 24px;
            font-weight: bold;
            padding: 5px 15px;
            transform: rotate(-10deg);
            display: inline-block;
            margin-top: 10px;
        }}
        .comment-box {{
            background-color: #fff0f0;
            border-radius: 5px;
            padding: 10px;
            margin-top: 15px;
            font-size: 14px;
            border-left: 5px solid #ff4b4b;
        }}
    </style>
    
    <div class="report-box">
        <div class="header">
            <span class="field-label">{field_name} {st.session_state.get('race_num', '11')}R</span>
            <span style="font-weight:bold;">一果のイン逃げ判定</span>
        </div>
        
        <div class="main-score">
            <div class="diff-label">場平均（{field_avg}%）より</div>
            <div class="diff-value">{diff_text}</div>
            <div class="diff-label">イン逃げ期待値：{current_expectancy}%</div>
            <div class="stamp">{status}</div>
        </div>

        <div style="display: flex; align-items: flex-start;">
            <div style="width: 60px; height: 60px; background: #ddd; border-radius: 50%; margin-right: 10px; flex-shrink: 0; display:flex; align-items:center; justify-content:center; font-size:10px; text-align:center;">
                一果<br>Icon
            </div>
            <div class="comment-box">
                「{field_name}の平均よりかなり高いね！壁役の{wall_strength}も安定してるし、ここは一果にお任せ！」
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 呼び出し例
show_ichika_report("住之江", 52, 74, "2号艇")
