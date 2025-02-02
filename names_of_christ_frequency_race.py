import matplotlib
matplotlib.use('Agg')

import os
os.environ['PATH'] += os.pathsep + r'C:\ffmpeg\bin'

import sqlite3
import pandas as pd
from collections import Counter
import nltk
from nltk.tokenize import word_tokenize
import bar_chart_race as bcr

# Get words from names_of_christ.csv
names_of_christ = pd.read_csv('scriptures_db/data/names_of_christ.csv')
christ_names = set(names_of_christ['name'].str.lower())  # Convert to lowercase for matching

# Connect to the database
conn = sqlite3.connect('conference_talks.db')

# Read the data with president names and dates
query = """
SELECT body_text, date_published, author_role, listed_author as president
FROM talks 
WHERE author_role LIKE '%President of%Church%'
ORDER BY date_published
"""
df = pd.read_sql_query(query, conn)

# Clean the data
df['date_published'] = pd.to_datetime(df['date_published'])
df['year'] = df['date_published'].dt.year

# Create a dictionary to store word frequencies by president and year
president_word_freq = {}
current_president = None
running_totals = Counter()

# Process texts president by president, year by year
for _, row in df.iterrows():
    year = row['year']
    president = row['president']
    text = row['body_text'].lower()
    
    # If president changes, reset the counter
    if president != current_president:
        current_president = president
        running_totals = Counter()
    
    # Tokenize and count only names of Christ
    words = word_tokenize(text)
    christ_mentions = [word for word in words if word.lower() in christ_names]
    
    # Update running totals for this president
    running_totals.update(christ_mentions)
    
    # Store the cumulative counts for this year/president
    president_word_freq[(year, president)] = Counter(running_totals)

# Create the DataFrame for the bar chart race
data = []
years = []
presidents = []

for (year, president), freq_dict in sorted(president_word_freq.items()):
    row = {name: freq_dict.get(name.lower(), 0) for name in christ_names}
    data.append(row)
    years.append(year)
    presidents.append(president)

bcr_df = pd.DataFrame(data, index=[f"{year} - {president}" for year, president in zip(years, presidents)])

# Create the bar chart race
bcr.bar_chart_race(
    df=bcr_df,
    filename='christ_names_by_president.mp4',
    title='Usage of Names of Christ by Church Presidents',
    n_bars=15,
    period_length=1000,
    steps_per_period=30,
    period_fmt='{x}',
    figsize=(10, 6),
    filter_column_colors=True,
    writer='ffmpeg'
)

print("Animation has been saved as 'christ_names_by_president.mp4'")

conn.close()