
import streamlit as st
import streamlit.components.v1 as components
import base64

st.set_page_config(layout="wide")

IMAGE_PATH = "mark_sheet_base.png"   # ←今回のマークシート画像

with open(IMAGE_PATH, "rb") as f:
    b64 = base64.b64encode(f.read()).decode()

html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
#container {{
  position: relative;
  display: inline-block;
}}
#container img {{
  max-width: 100%;
}}
#pos {{
  font-size: 18px;
  margin-top: 10px;
}}
</style>
</head>
<body>

<div id="container">
  <img id="img" src="data:image/png;base64,{b64}">
</div>

<div id="pos">click position</div>

<script>
const img = document.getElementById("img");
const pos = document.getElementById("pos");

img.addEventListener("click", function(e){{
  const rect = img.getBoundingClientRect();
  const x = Math.round(e.clientX - rect.left);
  const y = Math.round(e.clientY - rect.top);
  pos.innerText = "x=" + x + " , y=" + y;
}});
</script>

</body>
</html>
"""

components.html(html, height=900)
