import html
import json
import re

import streamlit as st
from ai_helper import ask_ai


st.set_page_config(page_title="나의 운세 & 별자리", page_icon="🔮", layout="centered")

SIGN_SYMBOLS = {
    "물병": "♒", "물고기": "♓", "양": "♈", "황소": "♉",
    "쌍둥이": "♊", "게": "♋", "사자": "♌", "처녀": "♍",
    "천칭": "♎", "전갈": "♏", "궁수": "♐", "염소": "♑",
}

CSS = """
.stApp {
    background: radial-gradient(circle at top, #2a1f4d 0%, #120e26 45%, #0b0a18 100%);
}
.title {
    text-align: center; font-size: 2.4rem; font-weight: 800; margin-bottom: 0;
    background: linear-gradient(90deg, #ffb88c, #ff7eb6);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.subtitle {
    text-align: center; color: #a9a3c9; font-size: 0.9rem;
    margin: 0.25rem 0 2rem 0;
}
label p { color: #e6e1ff !important; font-size: 0.85rem !important; }
div[data-baseweb="input"], div[data-baseweb="select"] > div {
    background: #1c1738 !important;
    border: 1px solid #6c5ce7 !important; border-radius: 10px !important;
}
div[data-baseweb="input"] input, div[data-baseweb="select"] input {
    background: transparent !important; color: #f1eeff !important;
}
div.stButton > button {
    background: linear-gradient(135deg, #ffd166, #ffb347) !important;
    color: #1a1433 !important; border: none !important; border-radius: 12px !important;
    font-weight: 700 !important; padding: 0.6rem 1.6rem !important;
    box-shadow: 0 0 18px rgba(255, 209, 102, 0.45) !important;
}
div[data-testid="stSpinner"] * {
    color: #f1eeff !important;
}
.card {
    background: #1a1536; border: 1px solid #3d3470; border-radius: 18px;
    padding: 24px; margin-top: 24px; box-shadow: 0 8px 30px rgba(0, 0, 0, 0.35);
}
.card-title {
    display: inline-block; font-weight: 700; color: #ffd27a;
    background: #2a2050; border: 1px solid #4a3d80; border-radius: 999px;
    padding: 6px 14px; margin-bottom: 16px;
}
.message { color: #e6e1ff; line-height: 1.8; margin: 0 0 20px 0; }
.meter-head {
    display: flex; justify-content: space-between; color: #e6e1ff;
    font-size: 0.85rem; font-weight: 600; margin-bottom: 6px;
}
.meter { height: 8px; background: #2a2450; border-radius: 8px; overflow: hidden; }
.meter-fill {
    height: 100%; background: linear-gradient(90deg, #7aa2ff, #ff7eb6, #ffd166);
}
.tiles { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 20px; }
.tile { background: #15112d; border: 1px solid #3d3470; border-radius: 12px; padding: 14px; }
.tile-label { color: #a9a3c9; font-size: 0.75rem; margin-bottom: 6px; }
.tile-value { color: #ffffff; font-weight: 700; }
.dot {
    display: inline-block; width: 12px; height: 12px; border-radius: 50%;
    margin-right: 6px; vertical-align: middle;
}
"""

st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
st.markdown('<h1 class="title">🔮 오늘의 운세 & 별자리</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">이름 · 생년월일 · 별자리로 오늘 하루의 기운을 봐 드려요</p>',
    unsafe_allow_html=True,
)

name = st.text_input("이름을 입력하세요")
birth = st.date_input("생년월일을 입력하세요")
sign = st.selectbox("나의 별자리", list(SIGN_SYMBOLS), index=6)


def parse_json(raw):
    # AI가 ```json 코드블록으로 감싸도 읽을 수 있게 걷어내요
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())
    return json.loads(text)


def render_card(data, name, sign):
    luck = max(0, min(100, int(data.get("luck", 50))))
    color_hex = data.get("color_hex", "")
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", color_hex):
        color_hex = "#ffd166"

    st.markdown(f"""
<div class="card">
  <div class="card-title">{SIGN_SYMBOLS[sign]} {html.escape(sign)}자리 · {html.escape(name)}님</div>
  <p class="message">{html.escape(data.get("message", ""))}</p>
  <div class="meter-head"><span>오늘의 행운 지수</span><span>{luck}%</span></div>
  <div class="meter"><div class="meter-fill" style="width: {luck}%"></div></div>
  <div class="tiles">
    <div class="tile">
      <div class="tile-label">행운의 색</div>
      <div class="tile-value"><span class="dot" style="background: {color_hex}"></span>{html.escape(data.get("color_name", ""))}</div>
    </div>
    <div class="tile">
      <div class="tile-label">행운의 아이템</div>
      <div class="tile-value">{html.escape(data.get("item", ""))}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


if st.button("오늘의 운세 보기"):
    if not name:
        st.warning("이름을 입력해 주세요.")
    else:
        prompt = f"{name}님은 {birth}에 태어난 {sign}자리예요.\n"
        prompt += "오늘의 운세를 아래 JSON 형식으로만 답해주세요. 다른 설명은 붙이지 마세요.\n"
        prompt += '{"message": "운세 본문을 4~5문장으로 재미있게", "luck": 0~100 사이 정수, '
        prompt += '"color_name": "행운의 색 이름(한글)", "color_hex": "#RRGGBB", '
        prompt += '"item": "행운의 아이템(한글 2~4글자)"}'

        with st.spinner("별들의 기운을 읽는 중..."):
            raw = ask_ai(prompt)

        try:
            render_card(parse_json(raw), name, sign)
        except (json.JSONDecodeError, KeyError, ValueError):
            st.write(raw)
