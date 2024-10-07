import json
import pandas as pd
from collections import Counter
import plotly.graph_objects as go
import plotly.offline as pyo

def analyze_word(input_word, keep_case):
    # Load the JSON data
    with open('scriptures_db/data/json/scriptures.json', 'r') as file:
        scriptures_data = json.load(file)

    # Create a list to store the data
    data = []
    key_word = input_word # keep the original case

    key_word = input_word if keep_case else input_word.lower()  # Set key_word based on checkbox

    # Process each verse
    for verse in scriptures_data:
        scripture_text = verse['scripture_text']
        volume_title = verse['volume_title']  
        book_title = verse['book_title']      
        chapter_number = verse['chapter_number'] 
        verse_number = verse['verse_number']
        verse_short_title = verse['verse_short_title']
        scripture_text_lower = scripture_text.lower() if not keep_case else scripture_text  # Adjust case


        # Count occurrences of the key_word in the scripture text
        count = scripture_text_lower.count(key_word)

        # Append the data with volume, book, chapter, and count
        if count > 0:  # Only include if the count is greater than 0
            data.append({
                'volume_title': volume_title,
                'book_title': book_title,
                'chapter_number': chapter_number,
                'verse_number': verse_number,
                'verse_short_title': verse_short_title,
                'scripture_text': scripture_text,
                'count': count
            })

    # Create a DataFrame
    df = pd.DataFrame(data)
    

    return df

def create_pie_chart(df):
    # group by volume_title
    df_grouped = df.groupby('volume_title').sum('count')

    # Create a pie chart
    fig = go.Figure(data=[go.Pie(labels=df_grouped.index, values=df_grouped['count'])])
    fig.update_layout(title='Frequency of Words')

    # Convert the figure to HTML
    fig_html = pyo.plot(fig, include_plotlyjs=False, output_type='div')

    return fig_html  # Return the grouped data and HTML figure
