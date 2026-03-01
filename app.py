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

    # ---ИСТОРИЯ (ПРОГРЕСС) ---
    if st.session_state.history:
        st.write("---")
        st.subheader("📚 Мой прогресс")
        for i, item in enumerate(reversed(st.session_state.history)):
            with st.expander(f"Задание №{len(st.session_state.history) - i}"):
                st.write(f"RU: {item['ru']}")
                st.write(f"Ваш вариант: {item['en']}")
                st.write(f"Разбор:\n{item['feedback']}")
