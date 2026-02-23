import streamlit as st

# ページ設定
st.set_page_config(page_title="診断用パネル", layout="wide")

# 1. ログイン機能を一時的にパスワードなしで通す
st.session_state["pwd_ok"] = True 

st.title("デバッグモード：タブ表示テスト")

# タブ構成
tabs = st.tabs(["⭐ 簡易予想", "📊 統計解析", "スタート予想", "混合戦スタート精度", "風・波補正", "女子戦", "女子戦補正閲覧", "女子戦補正入力", "女子戦スタート予想", "女子戦スタート精度"])

# 各タブに中身を入れる
for i, tab in enumerate(tabs):
    with tab:
        st.subheader(f"タブ {i+1} の中身")
        st.write("この文字が見えていれば、タブの構造は正常です。")
        if i == 2: # スタート予想タブ
            st.write("ここがTab5（スタート予想）です。")
