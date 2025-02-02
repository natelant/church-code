import matplotlib
matplotlib.use('Agg')  # This must come before any other matplotlib imports

import os
# Add ffmpeg to PATH explicitly
os.environ['PATH'] += os.pathsep + r'C:\ffmpeg\bin'

import sqlite3
import pandas as pd
from collections import Counter
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import bar_chart_race as bcr

# Download required NLTK data
# nltk.download('punkt')
# nltk.download('stopwords')

# Initialize stop words
stop_words = set(stopwords.words('english'))
# Add any custom stop words you want to exclude
custom_stop_words = {
    'thy', 'thee', 'thou', 'ye', 'unto', 'hath', 'say', 'said', 'saying',
    'shall', 'may', 'must', 'would', 'could', 'should',  # Modal verbs
    'one', 'two', 'three', 'first', 'second', 'third',  # Numbers
    'like', 'also', 'well', 'even', 'much', 'many'  # Common modifiers
}
stop_words.update(custom_stop_words)

# Connect to the database
conn = sqlite3.connect('conference_talks.db')

# Read the data
query = """
SELECT body_text, date_published, author_role, listed_author
FROM talks 
ORDER BY date_published
"""
df = pd.read_sql_query(query, conn)

# Clean the data
df['date_published'] = pd.to_datetime(df['date_published'])
df['year'] = df['date_published'].dt.year

# Filters for apostles and prophets
df = df[
    df['author_role'].str.contains('Twelve') |  # Matches any role containing "Twelve"
    df['author_role'].str.contains('First Presidency') |  # Matches First Presidency roles
    df['author_role'].str.contains('President of [Tt]he Church', regex=True)  # Matches both variations 
]


# Create a dictionary to store word frequencies by year
word_freq_by_year = {}

# Group the DataFrame by year
for year in sorted(df['year'].unique()):
    year_df = df[df['year'] == year]
    year_words = []
    
    # Process texts for this year
    for text in year_df['body_text']:
        words = word_tokenize(text.lower())
        words = [word for word in words if word.isalpha() and len(word) > 2]
        year_words.extend(words)
    
    # Count words for this year, excluding stop words
    word_freq = Counter(word for word in year_words if word not in stop_words)
    word_freq_by_year[year] = word_freq

# Add minimum frequency threshold
min_freq = 10  # Adjust this value as needed
filtered_words = set()
for freq_dict in word_freq_by_year.values():
    for word, count in freq_dict.items():
        if count >= min_freq:
            filtered_words.add(word)

# Create the DataFrame with filtered words
data = []
for year in sorted(word_freq_by_year.keys()):
    row = {word: word_freq_by_year[year].get(word, 0) for word in filtered_words}
    data.append(row)

bcr_df = pd.DataFrame(data, index=sorted(word_freq_by_year.keys()))

# Create the bar chart race with additional parameters
bcr.bar_chart_race(
    df=bcr_df,
    filename='word_frequency_race.mp4',
    title='Most Common Words in General Conference from the Apostles and Prophets',
    n_bars=20,
    period_length=1000,
    steps_per_period=30,
    period_fmt='{x:.0f}',
    figsize=(8, 5),
    filter_column_colors=True,

    writer='ffmpeg'  # Explicitly specify ffmpeg
)

print("Animation has been saved as 'word_frequency_race.mp4'")

conn.close()
