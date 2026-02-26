# ==============================
# ここから本体処理
# ==============================

place = st.session_state.selected_place
st.caption(f"選択中の会場：{place}")

SHEET_MAP = {
    "蒲郡混合戦": {
        "sheet1": "蒲郡混合_統計シート",
        "sheet2": "蒲郡混合_統計シート②"
    },
    "蒲郡女子戦": {
        "sheet1": "蒲郡女子_統計シート",
        "sheet2": "蒲郡女子_統計シート②"
    },
}

gc = get_gsheet_client()

if gc is None:
    st.error("Google認証に失敗しました")
    st.stop()

# ★ ここだけ1回だけ
try:
    sh = gc.open_by_key("1lN794iGtyGV2jNwlYzUA8wEbhRwhPM7FxDAkMaoJss4")

    ws1_name = SHEET_MAP[place]["sheet1"]
    ws2_name = SHEET_MAP[place]["sheet2"]

    ws1 = sh.worksheet(ws1_name)
    ws2 = sh.worksheet(ws2_name)

    rows1 = ws1.get_all_records()
    rows2 = ws2.get_all_records()

    st.write("DEBUG rows1:", len(rows1))
    st.write("DEBUG rows2:", len(rows2))

    df = pd.DataFrame(rows1 + rows2)

except Exception as e:
    st.error("シート読み込みエラー")
    st.exception(e)
    st.stop()


# ← ここに必ず来るか確認
st.title("予想ツール")
st.write("ここまで来ています")
