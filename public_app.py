import os

if st.button("蒲郡", use_container_width=True):
    # 候補となるパスをすべて試す
    targets = [
        "pages/07_gamagori.py",        # 本来の場所
        "pages/pages/07_gamagori.py",  # 二重フォルダの場合
        "07_gamagori.py",              # 階層がズレている場合
        "pages/07_蒲郡.py"              # 日本語に戻った場合
    ]
    
    found = False
    for path in targets:
        if os.path.exists(path):
            st.switch_page(path)
            found = True
            break
            
    if not found:
        st.error("ファイルが見つかりません。現在のフォルダの中身:")
        st.write(os.listdir(".")) # どこに何があるか画面に表示させる
        if os.path.exists("pages"):
            st.write("pagesフォルダの中身:", os.listdir("pages"))












