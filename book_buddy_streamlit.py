"""
کتاب‌یار — دستیار هوش مصنوعی برای پیشنهاد و گفتگو درباره کتاب
اجرا: streamlit run book_buddy_streamlit.py
"""

import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="کتاب‌یار", page_icon="📖")
st.title("📖 کتاب‌یار")
st.caption("همراه هوشمند کتاب‌خوانی شما")

with st.sidebar:
    api_key = st.text_input("Gemini API Key", type="password")
    st.markdown("[ساخت API key رایگان از اینجا](https://aistudio.google.com/app/apikey)")

SYSTEM_PROMPT = """تو «کتاب‌یار» هستی، یک دستیار هوشمند و صمیمی برای کتاب‌خوانی به زبان فارسی.
وظایفت:
- بر اساس سلیقه، ژانر، حال‌وهوا یا کتاب‌های قبلی کاربر، ۲ تا ۳ کتاب پیشنهاد بده (با نام نویسنده).
- اگر کاربر درباره یک کتاب خاص پرسید، درباره‌اش (خلاصه بدون اسپویل مهم، شخصیت‌ها، سبک) گفتگو کن.
- لحن گرم، مختصر و شبیه یک کتاب‌فروش باتجربه باش.
- در پایان هر پاسخ، یک سؤال کوتاه برای ادامه گفتگو بپرس."""

if "display_messages" not in st.session_state:
    st.session_state.display_messages = []

for msg in st.session_state.display_messages:
    shown_role = "assistant" if msg["role"] == "model" else "user"
    with st.chat_message(shown_role):
        st.write(msg["content"])

user_input = st.chat_input("پیام‌تون را بنویسید...")

if user_input:
    if not api_key:
        st.error("لطفاً اول API key خودتون رو در نوار کناری وارد کنید.")
        st.stop()

    st.session_state.display_messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    client = genai.Client(api_key=api_key)

    contents = [
        {"role": m["role"], "parts": [{"text": m["content"]}]}
        for m in st.session_state.display_messages
    ]

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_reply = ""

        for chunk in client.models.generate_content_stream(
            model="gemini-3.8-flash",
            contents=contents,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
        ):
            full_reply += chunk.text or ""
            placeholder.write(full_reply)

    st.session_state.display_messages.append({"role": "model", "content": full_reply})