import streamlit as st
from groq import Groq

# Настройки страницы
st.set_page_config(page_title="Intention", page_icon="🎯", layout="wide")

# Кастомные стили
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; }
    .stExpander { border: none !important; box-shadow: none !important; }
    </style>
    """, unsafe_allow_html=True)

# Инициализация сессии
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'history' not in st.session_state:
    st.session_state.history = []
if 'current_phrase' not in st.session_state:
    st.session_state.current_phrase = ""

# --- ЛОГИН ---
if not st.session_state.logged_in:
    st.title("🎯 Intention")
    user_id = st.text_input("Логин (8 символов):", max_chars=8)
    if st.button("Войти"):
        if len(user_id) == 8:
            st.session_state.username = user_id
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Логин должен быть ровно 8 символов.")
    st.stop()

# --- ИНТЕРФЕЙС ---
st.title(f"🎯 Intention | {st.session_state.username}")

# БОКОВАЯ ПАНЕЛЬ: Настройки + История
with st.sidebar:
    st.header("⚙️ Настройки")
    api_key = st.text_input("Groq API Key:", type="password")
    level = st.selectbox("Уровень:", ["A2", "B1", "B2", "C1"])
    topic = st.selectbox("Тема:", ["Повседневная жизнь", "Бизнес", "Учеба", "Путешествия", "Сленг"])
    
    if st.button("Выйти"):
        st.session_state.logged_in = False
        st.rerun()
    
    st.write("---")
    st.header("📊 История прогресса")
    if not st.session_state.history:
        st.write("Здесь будет ваш прогресс")
    else:
        for i, item in enumerate(reversed(st.session_state.history)):
            with st.expander(f"Задание #{len(st.session_state.history) - i}"):
                st.caption(f"RU: {item['ru']}")
                st.caption(f"EN: {item['en']}")
                if "ПРАВИЛЬНО" in item['status']:
                    st.success("Верно")
                else:
                    st.error("Есть ошибки")

# ОСНОВНАЯ ЗОНА
if not api_key:
    st.warning("👈 Введите API Key в настройках слева.")
else:
    client = Groq(api_key=api_key)

    if st.button("✨ Получить новое предложение"):
        prompt = f"Generate one random Russian sentence for translation. Level: {level}. Topic: {topic}. ONLY text."
        res = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant"
        )
        st.session_state.current_phrase = res.choices[0].message.content

    if st.session_state.current_phrase:
        st.info(f"Переведи: {st.session_state.current_phrase}")
        user_translation = st.text_area("Ваш перевод:", placeholder="Введите текст...")

        if st.button("🔍 Проверить"):
            if user_translation:
                # Жесткий промпт для ИИ
                check_prompt = f"""
                Act as a strict English teacher. 
                Source Russian: {st.session_state.current_phrase}
                User English: {user_translation}
                
                Provide feedback in Russian. Strictly follow this format, no intros or outros:
                
                VERDICT: [Write only 'ПРАВИЛЬНО' if no major errors, otherwise 'НЕПРАВИЛЬНО']
                
                БЛОК 1 (Ошибки):
                - [Bullet points of errors and rules in Russian]
                
                БЛОК 2 (Время):
                - [Check if tense is correct, mention which tense it is. Highlight if correct/incorrect]
                
                БЛОК 3 (Как скажет носитель):
                [Natural version]
                
                БЛОК 4 (Альтернативы):
                [Advanced options]
                """
                
                res = client.chat.completions.create(
                    messages=[{"role": "user", "content": check_prompt}],
                    model="llama-3.1-8b-instant"
                )
                feedback = res.choices[0].message.content
                
                # Определяем цвет (зеленый/красный)
                is_correct = "VERDICT: ПРАВИЛЬНО" in feedback
                status_label = "✅ ПРАВИЛЬНО" if is_correct else "❌ НЕПРАВИЛЬНО"
                
                # Сохраняем
                st.session_state.history.append({
                    "ru": st.session_state.current_phrase,
                    "en": user_translation,
                    "status": status_label
                })
                
                # Вывод результата
                if is_correct:
                    st.success(status_label)
                else:
                    st.error(status_label)
                
                # Убираем техническую строку VERDICT из вывода пользователю
                display_feedback = feedback.replace("VERDICT: ПРАВИЛЬНО", "").replace("VERDICT: НЕПРАВИЛЬНО", "").strip()
                st.markdown(display_feedback)
            else:
                st.warning("Введите перевод!")
