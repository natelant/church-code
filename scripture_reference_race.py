import matplotlib
matplotlib.use('Agg')

import os
os.environ['PATH'] += os.pathsep + r'C:\ffmpeg\bin'

import sqlite3
import pandas as pd
from collections import Counter
import bar_chart_race as bcr
import ast  # To safely evaluate string representations of lists

# Connect to the database
conn = sqlite3.connect('conference_talks.db')

# Read the data
query = """
SELECT scripture_refs, date_published
FROM talks 
WHERE scripture_refs IS NOT NULL
ORDER BY date_published
"""
df = pd.read_sql_query(query, conn)

# Clean the data
df['date_published'] = pd.to_datetime(df['date_published'])
df['year'] = df['date_published'].dt.year


# Create a dictionary to store cumulative scripture frequencies
cumulative_scripture_freq = {}
running_totals = Counter()

# Process texts year by year, accumulating frequencies
for year in sorted(df['year'].unique()):
    year_df = df[df['year'] == year]
    year_scriptures = Counter()
    
    # Process scripture references for this year
    for refs in year_df['scripture_refs']:
        if refs:  # Check if refs is not None
            try:
                # Safely convert string representation of list to actual list
                scripture_list = ast.literal_eval(refs)
                year_scriptures.update(scripture_list)
            except (ValueError, SyntaxError):
                continue
    
    # Add this year's scriptures to running totals
    running_totals.update(year_scriptures)
    
    # Store the cumulative counts for this year
    cumulative_scripture_freq[year] = Counter(running_totals)

# Create the DataFrame for the bar chart race
data = []
all_scriptures = set()
for counts in cumulative_scripture_freq.values():
    all_scriptures.update(counts.keys())

for year in sorted(cumulative_scripture_freq.keys()):
    row = {scripture: cumulative_scripture_freq[year].get(scripture, 0) 
           for scripture in all_scriptures}
    data.append(row)

bcr_df = pd.DataFrame(data, index=sorted(cumulative_scripture_freq.keys()))

# Create the bar chart race
bcr.bar_chart_race(
    df=bcr_df,
    filename='cumulative_scripture_references.mp4',
    title='Cumulative Scripture References in Conference Talks (1851-Present)',
    n_bars=20,
    period_length=1000,
    steps_per_period=30,
    period_fmt='{x:.0f}',
    figsize=(10, 6),
    filter_column_colors=True,
    writer='ffmpeg'
)

print("Animation has been saved as 'cumulative_scripture_references.mp4'")

conn.close()