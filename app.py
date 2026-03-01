import streamlit as st
from groq import Groq

# 1. Настройка внешнего вида
st.set_page_config(page_title="Intention", page_icon="🎯", layout="centered")

# Кастомный стиль для красоты
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; }
    .reportview-container .main .block-container { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# 2. Инициализация памяти приложения (Session State)
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'history' not in st.session_state:
    st.session_state.history = []
if 'current_phrase' not in st.session_state:
    st.session_state.current_phrase = ""

# --- ЭКРАН ЛОГИНА ---
if not st.session_state.logged_in:
    st.title("🎯 Intention")
    st.subheader("Твой путь к автоматизму в английском")
    
    with st.container():
        st.write("Создайте свой уникальный идентификатор для входа.")
        user_id = st.text_input("Введите логин (ровно 8 символов):", placeholder="Например: User7777")
        
        if st.button("Войти в систему"):
            if len(user_id) == 8:
                st.session_state.username = user_id
                st.session_state.logged_in = True
                st.success("Успешный вход!")
                st.rerun()
            else:
                st.error("Ошибка: Логин должен содержать ровно 8 символов. Сейчас у вас: " + str(len(user_id)))
    st.stop()

# --- ОСНОВНОЙ ИНТЕРФЕЙС (после входа) ---
st.title(f"🎯 Intention | {st.session_state.username}")

# Боковое меню
with st.sidebar:
    st.header("⚙️ Настройки")
    api_key = st.text_input("Ваш Groq API Key:", type="password")
    level = st.selectbox("Уровень:", ["A2", "B1", "B2", "C1"])
    topic = st.selectbox("Тема:", ["Повседневная жизнь", "Бизнес/Работа", "Учеба", "Путешествия", "Сленг"])
    
    st.write("---")
    if st.button("Выйти"):
        st.session_state.logged_in = False
        st.rerun()

# Проверка API ключа
if not api_key:
    st.warning("👈 Вставьте ваш API Key в боковом меню, чтобы начать обучение.")
else:
    client = Groq(api_key=api_key)

    # Блок кнопок управления
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✨ Новое предложение"):
            try:
                prompt = f"Generate one random Russian sentence for translation. Level: {level}. Topic: {topic}. Output ONLY the sentence text, no quotes."
                res = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.1-8b-instant"
                )
                st.session_state.current_phrase = res.choices[0].message.content
            except Exception as e:
                st.error(f"Ошибка связи: {e}")

    with col2:
        if st.button("⏭ Пропустить"):
            st.session_state.current_phrase = ""
            st.rerun()

    # Поле задания
    if st.session_state.current_phrase:
        st.info(f"Переведи на английский:\n\n### {st.session_state.current_phrase}")
        
        user_translation = st.text_area("Ваш перевод:", placeholder="Введите английский текст здесь...")

        if st.button("🔍 Проверить"):
            if user_translation:
                with st.spinner('Учитель проверяет ваш английский...'):
                    check_prompt = f"""
                    Ты — опытный учитель английского (носитель языка). 
                    Русское предложение: {st.session_state.current_phrase}
                    Перевод ученика: {user_translation}
                    
                    Твоя задача:
                    1. Проверь английский текст ученика на наличие ошибок (времена, артикли, порядок слов, лексика).
                    2. Объясни каждую ошибку ПО-РУССКИ максимально подробно.
                    3. Напиши 'Как скажет носитель' (самый естественный вариант).
                    4. Предложи более продвинутые конструкции для улучшения предложения.
                    """
                    
                    try:
                        res = client.chat.completions.create(
                            messages=[{"role": "user", "content": check_prompt}],
                            model="llama-3.1-8b-instant"
                        )
                        feedback = res.choices[0].message.content
                        
                        # Сохраняем в историю
                        st.session_state.history.append({
                            "ru": st.session_state.current_phrase,
                            "en": user_translation,
                            "feedback": feedback
                        })
                        
                        st.markdown("---")
                        st.subheader("Разбор учителя:")
                        st.write(feedback)
                    except Exception as e:
                        st.error(f"Ошибка проверки: {e}")
            else:
                st.warning("Поле перевода пустое!")

    # --- ИСТОРИЯ (ПРОГРЕСС) ---
    if st.session_state.history:
        st.write("---")
        st.subheader("📚 Мой прогресс")
        for i, item in enumerate(reversed(st.session_state.history)):
            with st.expander(f"Задание №{len(st.session_state.history) - i}"):
                st.write(f"RU: {item['ru']}")
                st.write(f"Ваш вариант: {item['en']}")
                st.write(f"Разбор:\n{item['feedback']}")
