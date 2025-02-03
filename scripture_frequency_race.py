import matplotlib
matplotlib.use('Agg')

import os
os.environ['PATH'] += os.pathsep + r'C:\ffmpeg\bin'

import sqlite3
import pandas as pd
from collections import Counter
import ast
import re
import bar_chart_race as bcr

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

# Function to clean and standardize scripture references
def clean_scripture_ref(ref):
    # Remove unicode characters and clean up common patterns
    ref = ref.encode('ascii', 'ignore').decode()
    
    # Regular expression to match book name, chapter, and verse
    # This will handle patterns like:
    # "1 Nephi 3:7", "D&C 89:1", "Genesis 1:1", "Alma 32:21-23"
    pattern = r'((?:\d\s+)?[A-Za-z&]+(?:\s+[A-Za-z]+)?)\s*(?:chapter\s+)?(\d+):(\d+(?:-\d+)?)'
    match = re.match(pattern, ref)
    
    if match:
        book = match.group(1).strip()
        chapter = match.group(2)
        verse = match.group(3)
        
        # Standardize book names
        if book.startswith(('1 ', '2 ', '3 ', '4 ')):
            number, rest = book.split(' ', 1)
            book = f"{number} {rest}"
            
        # Handle verse ranges (e.g., "3-5" becomes "3")
        verse = verse.split('-')[0]  # Take just the first verse of a range
        
        return f"{book} {chapter}:{verse}"
    
    return None

# Create a dictionary to store cumulative scripture frequencies
cumulative_scripture_freq = {}
running_totals = Counter()

# Process texts year by year, accumulating frequencies
for year in sorted(df['year'].unique()):
    year_df = df[df['year'] == year]
    year_scriptures = Counter()
    
    # Process scripture references for this year
    for refs in year_df['scripture_refs']:
        if refs:
            try:
                # Convert string representation of list to actual list
                scripture_list = ast.literal_eval(refs)
                # Clean and count each reference
                cleaned_refs = [clean_scripture_ref(ref) for ref in scripture_list]
                # Remove None values from failed matches
                cleaned_refs = [ref for ref in cleaned_refs if ref is not None]
                year_scriptures.update(cleaned_refs)
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

# Filter for references that appear at least 5 times
min_occurrences = 5
filtered_scriptures = {
    scripture for scripture in all_scriptures 
    if max(count.get(scripture, 0) for count in cumulative_scripture_freq.values()) >= min_occurrences
}

for year in sorted(cumulative_scripture_freq.keys()):
    row = {scripture: cumulative_scripture_freq[year].get(scripture, 0) 
           for scripture in filtered_scriptures}
    data.append(row)

bcr_df = pd.DataFrame(data, index=sorted(cumulative_scripture_freq.keys()))

# Create the bar chart race
bcr.bar_chart_race(
    df=bcr_df,
    filename='cumulative_scripture_verse_references.mp4',
    title='Most Cited Scripture Verses in Conference Talks (1971-Present)',
    n_bars=15,  # Reduced due to more granular data
    period_length=1000,
    steps_per_period=30,
    period_fmt='{x:.0f}',
    figsize=(14, 8),  # Increased width for longer labels
    filter_column_colors=True,
    writer='ffmpeg'
)

print("Animation has been saved as 'cumulative_scripture_verse_references.mp4'")

conn.close() 