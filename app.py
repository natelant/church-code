import streamlit as st
from app_functions import query_scriptures, create_visual

st.title("The Word of God")

case_sensitive = st.toggle("Case sensitive search", value=False)

word = st.text_input("Enter one or more words/phrases to search (separate with commas):")

comparison = st.checkbox("Make comparison", help="If checked, the search will perform a comparison between the words/phrases.")

if word:
    if comparison:
        results = query_scriptures(word, case_sensitive=case_sensitive, return_per_word=True)
        # Compute and display count for each word
        word_counts = {w: len(v) for w, v in results.items()}
        total_count = sum(word_counts.values())
        counts_str = ", ".join([f"'{w}': {c}" for w, c in word_counts.items()])
        st.write(f"Found {total_count} verses in total. Counts per word: {counts_str}")
        if total_count:
            # Get unique volumes for dropdown
            all_verses = [row for verses in results.values() for row in verses]
            volumes = sorted(set(row[0] for row in all_verses))
            selected_volume = st.selectbox(
                "Drill down by volume (optional):",
                ["All Volumes"] + volumes
            )
            if selected_volume == "All Volumes":
                fig = create_visual(results, comparison=True)
            else:
                fig = create_visual(results, comparison=True, volume=selected_volume)
            st.plotly_chart(fig)
        # Show results grouped by word (header) and volume (expander)
        for w, verses in results.items():
            st.markdown(f"### Results for '{w}' ({len(verses)})")
            # Group verses by volume
            from collections import defaultdict
            volume_dict = defaultdict(list)
            for volume, book, chapter, verse, text in verses:
                volume_dict[volume].append((book, chapter, verse, text))
            for volume, v_verses in volume_dict.items():
                with st.expander(f"{volume} ({len(v_verses)})"):
                    for book, chapter, verse, text in v_verses:
                        st.markdown(f"**{book} {chapter}:{verse}** — {text}")
    else:
        results = query_scriptures(word, case_sensitive=case_sensitive)
        st.write(f"Found {len(results)} verses containing '{word}':")
        if results:
            # Get unique volumes for dropdown
            volumes = sorted(set(row[0] for row in results))
            selected_volume = st.selectbox(
                "Drill down by volume (optional):",
                ["All Volumes"] + volumes
            )
            if selected_volume == "All Volumes":
                fig = create_visual(results)
            else:
                fig = create_visual(results, volume=selected_volume)
            st.plotly_chart(fig)
            # Group verses by volume and show each in an expander
            from collections import defaultdict
            volume_dict = defaultdict(list)
            for volume, book, chapter, verse, text in results:
                volume_dict[volume].append((book, chapter, verse, text))
            for volume, v_verses in volume_dict.items():
                with st.expander(f"{volume} ({len(v_verses)})"):
                    for book, chapter, verse, text in v_verses:
                        st.markdown(f"**{book} {chapter}:{verse}** — {text}")
        else:
            st.info("No results found for your search.")
    
else:
    st.info("Type a word above to search the scriptures.")
