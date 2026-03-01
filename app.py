import streamlit as st
from groq import Groq

st.set_page_config(page_title="Intention", page_icon="🎯")
st.title("🎯 Intention")
st.subheader("Твой ИИ-учитель английского")

if "groq_key" not in st.session_state:
    st.session_state.groq_key = ""

with st.sidebar:
st.title("Настройки")
    level = st.selectbox("Ваш уровень:", ["A2", "B1", "B2", "C1"])
    topic = st.selectbox("Тематика:", ["Повседневная жизнь", "Бизнес", "Учеба", "Путешествия", "Сленг"])
    api_key = st.text_input("Вставьте ваш Groq API Key сюда:", type="password")
    if api_key:
        st.session_state.groq_key = api_key

if st.session_state.groq_key:
    client = Groq(api_key=st.session_state.groq_key)
    
    if 'phrase' not in st.session_state:
        st.session_state.phrase = "Нажмите кнопку ниже, чтобы получить фразу"

    if st.button("Дай мне предложение на русском"):
        prompt = f"Сгенерируй одно случайное предложение на русском языке для перевода на английский. Уровень: {level}. Тема: {topic}. В ответе напиши ТОЛЬКО само предложение на русском, без кавычек и лишних слов."
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}]
        )
st.session_state.phrase = completion.choices[0].message.content

    st.info(f"Переведи: {st.session_state.phrase}")
    
    user_translation = st.text_input("Твой перевод на английский:")

    if st.button("Проверить"):
        check_prompt = f"""
        Ты учитель английского языка. 
        Русский оригинал: {st.session_state.phrase}
        Перевод ученика: {user_translation}
        Уровень: {level}

Твоя задача:
        1. Укажи на ошибки (если они есть).
        2. Напиши идеальный вариант, как бы сказал носитель языка.
        3. Объясни грамматику и выбор слов на русском языке.
        """
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": check_prompt}]
        )
        st.write("---")
        st.write(response.choices[0].message.content)
else:
    st.warning("👈 Откройте боковое меню (стрелочка слева сверху) и вставьте ваш API Key, чтобы начать.")
