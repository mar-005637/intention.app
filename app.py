completion = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[{"role": "user", "content": prompt}]
                )
                st.session_state.phrase = completion.choices[0].message.content
        with col2:
            if st.button("⏭ Пропустить"):
                st.rerun()

        st.info(f"Переведи на английский:\n\n### {st.session_state.phrase}")
        
        user_translation = st.text_area("Твой вариант:", placeholder="Type your translation here...")

        if st.button("🔍 Проверить мой перевод"):
            if user_translation:
                with st.spinner('Учитель проверяет...'):
                    check_prompt = f"""
                    Ты носитель языка и учитель. 
                    Оригинал: {st.session_state.phrase}
                    Перевод ученика: {user_translation}
                    
                    Дай ответ в формате:
                    1. Исправленный вариант (как сказал бы носитель).
                    2. Список ошибок (если есть).
                    3. Короткое объяснение правил на русском.
                    """
                    response = client.chat.completions.create(
                        model="llama3-8b-8192",
                        messages=[{"role": "user", "content": check_prompt}]
                    )
                    st.success("Готово! Разбор ниже:")
                    st.markdown(response.choices[0].message.content)
            else:
                st.warning("Сначала напиши перевод!")
                
    except Exception as e:
        st.error(f"Произошла ошибка связи с ИИ. Проверь API ключ. Ошибка: {e}")
else:
    st.warning("👈 Пожалуйста, введи API Key в меню слева, чтобы приложение ожило.")
