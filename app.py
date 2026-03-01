import streamlit as st
from groq import Groq

# Page Configuration
st.set_page_config(page_title="Intention", page_icon="🎯", layout="wide")

# Session State
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'history' not in st.session_state:
    st.session_state.history = []
if 'current_phrase' not in st.session_state:
    st.session_state.current_phrase = ""

# --- LOGIN ---
if not st.session_state.logged_in:
    st.title("🎯 Intention")
    user_id = st.text_input("Login (8 characters):", max_chars=8)
    if st.button("Enter"):
        if len(user_id) == 8:
            st.session_state.username = user_id
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Login must be exactly 8 characters.")
    st.stop()

# --- INTERFACE ---
st.title(f"🎯 Intention | {st.session_state.username}")

with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Groq API Key:", type="password")
    level = st.selectbox("Level:", ["A2", "B1", "B2", "C1"])
    topic = st.selectbox("Topic:", ["Daily Life", "Business", "Academic", "Travel", "Slang"])
    
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
    
    st.write("---")
    st.header("📊 Progress")
    for i, item in enumerate(reversed(st.session_state.history)):
        status_color = "✅" if "CORRECT" in item['status'] else "❌"
        with st.expander(f"{status_color} Task #{len(st.session_state.history) - i}"):
            st.caption(f"RU: {item['ru']}")
            st.caption(f"EN: {item['en']}")

# MAIN CONTENT
if not api_key:
    st.warning("👈 Enter API Key in settings.")
else:
    client = Groq(api_key=api_key)

    if st.button("✨ Get New Sentence"):
        prompt = f"Generate 1 random Russian sentence for translation. Level: {level}. Topic: {topic}. Output ONLY the text."
        res = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant"
        )
        st.session_state.current_phrase = res.choices[0].message.content

    if st.session_state.current_phrase:
        st.info(f"Translate: {st.session_state.current_phrase}")
        user_translation = st.text_area("Your translation:")

        if st.button("🔍 Check"):
            if user_translation:
                # Ultra-strict prompt
                check_prompt = f"""
                You are a strict English corrector. Analyze the translation.
                Source RU: {st.session_state.current_phrase}
                User EN: {user_translation}
                Level: {level}

                Rules:
                1. If the user's translation is grammatically correct and keeps the meaning, VERDICT must be CORRECT.
                2. Explain errors ONLY in the user's English text.
                3. Language of explanations: Russian.
                4. NO intro, NO outro, NO "here is the analysis".

                Format:
                VERDICT: [CORRECT or INCORRECT]

                BLOCK 1 (Errors):
                Ошибка: [error] - Почему: [why] - Исправлено: [fix]
                (If no errors, write "Ошибок нет")

                BLOCK 2 (Tense):
                Время [tense name] употреблено [верно/неверно].

                BLOCK 3 (Native Version):
                [One sentence only, matching {level}]

                BLOCK 4 (Alternatives):
                - [Alternative 1]
                - [Alternative 2]
                """
                
                res = client.chat.completions.create(
                    messages=[{"role": "user", "content": check_prompt}],
                    model="llama-3.1-8b-instant"
                )
                feedback = res.choices[0].message.content
                
                is_correct = "VERDICT: CORRECT" in feedback
                status_label = "✅ CORRECT" if is_correct else "❌ INCORRECT"
                
                st.session_state.history.append({
                    "ru": st.session_state.current_phrase,
                    "en": user_translation,
                    "status": status_label
                })
                
                if is_correct:
                    st.success(status_label)
                else:
                    st.error(status_label)
                
                display_feedback = feedback.replace("VERDICT: CORRECT", "").replace("VERDICT: INCORRECT", "").strip()
                st.markdown(display_feedback)
