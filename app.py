import streamlit as st
from groq import Groq

# Page Configuration
st.set_page_config(page_title="Intention", page_icon="🎯", layout="wide")

# Custom CSS for UI
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; }
    .stExpander { border: none !important; }
    </style>
    """, unsafe_allow_html=True)

# Session State Initialization
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'history' not in st.session_state:
    st.session_state.history = []
if 'current_phrase' not in st.session_state:
    st.session_state.current_phrase = ""

# --- LOGIN SCREEN ---
if not st.session_state.logged_in:
    st.title("🎯 Intention")
    user_id = st.text_input("Login (strictly 8 characters):", max_chars=8)
    if st.button("Enter"):
        if len(user_id) == 8:
            st.session_state.username = user_id
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Login must be exactly 8 characters long.")
    st.stop()

# --- MAIN INTERFACE ---
st.title(f"🎯 Intention | User: {st.session_state.username}")

# SIDEBAR: Settings + Progress History
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Groq API Key:", type="password")
    level = st.selectbox("Level:", ["A2", "B1", "B2", "C1"])
    topic = st.selectbox("Topic:", ["Daily Life", "Business", "Academic", "Travel", "Slang"])
    
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
    
    st.write("---")
    st.header("📊 Progress History")
    if not st.session_state.history:
        st.write("No progress yet.")
    else:
        for i, item in enumerate(reversed(st.session_state.history)):
            with st.expander(f"Task #{len(st.session_state.history) - i}"):
                st.caption(f"RU: {item['ru']}")
                st.caption(f"Your EN: {item['en']}")
                if "CORRECT" in item['status']:
                    st.success("Correct")
                else:
                    st.error("Errors found")

# MAIN CONTENT AREA
if not api_key:
    st.warning("👈 Please enter your API Key in the settings on the left.")
else:
    client = Groq(api_key=api_key)

    if st.button("✨ Get New Sentence"):
        prompt = f"Generate one random Russian sentence for translation to English. Level: {level}. Topic: {topic}. Output ONLY the sentence text."
        try:
            res = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant"
            )
            st.session_state.current_phrase = res.choices[0].message.content
        except Exception as e:
            st.error(f"Connection error: {e}")

    if st.session_state.current_phrase:
        st.info(f"Translate to English:\n\n {st.session_state.current_phrase}")
        user_translation = st.text_area("Your translation:", placeholder="Type your English version here...")

        if st.button("🔍 Check"):
            if user_translation:
                # Optimized prompt for the AI Teacher
                check_prompt = f"""
                Act as a strict English teacher. 
                Original Russian: {st.session_state.current_phrase}
                User English Translation: {user_translation}
                
                Analyze ONLY the English translation provided by the user. 
                Explain everything in Russian. 
                Strictly follow this structure (no greeting, no intro, no outro):
                
                VERDICT: [Write only 'CORRECT' if no errors, otherwise 'INCORRECT']
                
                BLOCK 1 (Errors):
                - [List errors in the user's English sentence. Explain grammar/vocab rules in Russian]
                
                BLOCK 2 (Tense):
                - [Identify the tense used in the English sentence. State if it is correct or incorrect for this context]
                
                BLOCK 3 (Native Speaker Version):
                [Provide the most natural English version]
                
                BLOCK 4 (Alternatives):
                [Just list alternative English constructions here, no extra text]
                """
                
                try:
                    res = client.chat.completions.create(
                        messages=[{"role": "user", "content": check_prompt}],
                        model="llama-3.1-8b-instant"
                    )
                    feedback = res.choices[0].message.content
                    
                    is_correct = "VERDICT: CORRECT" in feedback
                    status_label = "✅ CORRECT" if is_correct else "❌ INCORRECT"
                    
                    # Store in history
                    st.session_state.history.append({
                        "ru": st.session_state.current_phrase,
                        "en": user_translation,
                        "status": status_label
                    })
                    
                    # Display Result
                    if is_correct:
                        st.success(status_label)
                    else:
                        st.error(status_label)
                    
                    # Clean feedback and display
                    display_feedback = feedback.replace("VERDICT: CORRECT", "").replace("VERDICT: INCORRECT", "").strip()
                    st.markdown(display_feedback)
                except Exception as e:
                    st.error(f"Error checking translation: {e}")
            else:
                st.warning("Please enter your translation first!")
