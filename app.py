import streamlit as st
from app_functions import query_scriptures, create_visual

st.title("The Word of God")

case_sensitive = st.toggle("Case sensitive search", value=False)

word = st.text_input("Enter one or more words/phrases to search (separate with commas):")

if word:
    results = query_scriptures(word, case_sensitive=case_sensitive)
    st.write(f"Found {len(results)} verses containing '{word}':")
    if results:
        fig = create_visual(results)
        st.plotly_chart(fig)
    for volume, book, chapter, verse, text in results:
        st.markdown(f"**{volume} — {book} {chapter}:{verse}** — {text}")
    
else:
    st.info("Type a word above to search the scriptures.")
