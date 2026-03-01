import streamlit as st
from groq import Groq

# Настройки страницы
st.set_page_config(page_title="Intention App", page_icon="🎯")

st.title("🎯 Intention: Твой ИИ-Учитель")

# Боковое меню
with st.sidebar:
    st.header("Настройки")
    api_key = st.text_input("Вставь свой Groq API Key:", type="password")
    level = st.selectbox("Уровень:", ["A2", "B1", "B2", "C1"])
    topic = st.selectbox("Тема:", ["Жизнь", "Работа", "Путешествия", "Сленг"])

# Проверка ключа
if not api_key:
    st.warning("👈 Пожалуйста, вставь API ключ в меню слева (он начинается на gsk_...)")
else:
    try:
        client = Groq(api_key=api_key)

        if 'russian_text' not in st.session_state:
            st.session_state.russian_text = ""

        if st.button("✨ Получить новое предложение"):
            # Мы обновили модель здесь на llama-3.1-8b-instant
            prompt = f"Write one random sentence in Russian for translation to English. Level {level}, topic {topic}. Write ONLY the sentence."
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",
            )
            st.session_state.russian_text = chat_completion.choices[0].message.content

        if st.session_state.russian_text:
            st.info(f"Переведи это: {st.session_state.russian_text}")
            
            user_answer = st.text_input("Твой перевод:")
            
            if st.button("🔍 Проверить"):
                # И здесь тоже обновили модель
                check_prompt = f"Russian: {st.session_state.russian_text}. User English: {user_answer}. Correct it, explain mistakes in Russian, and show how a native would say it."
                check_res = client.chat.completions.create(
                    messages=[{"role": "user", "content": check_prompt}],
                    model="llama-3.1-8b-instant",
                )
                st.success("Разбор полетов:")
                st.write(check_res.choices[0].message.content)

    except Exception as e:
        st.error(f"Ой! Что-то не так. Проверь ключ. Ошибка: {e}")
