import matplotlib
matplotlib.use('Agg')

import os
# Add the full path to ffmpeg
os.environ['PATH'] = r'C:\ffmpeg\bin' + os.pathsep + os.environ['PATH']  # Changed from += to explicit assignment

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
    # Replace special hyphens/dashes with standard hyphen before encoding
    ref = ref.replace('–', '-')  # en-dash
    ref = ref.replace('—', '-')  # em-dash
    ref = ref.replace('‐', '-')  # hyphen
    ref = ref.encode('ascii', 'ignore').decode()
    
    # Convert written numbers to digits (up to 999)
    number_words = {
        'first': '1', 'second': '2', 'third': '3', 'fourth': '4',
        'fifth': '5', 'sixth': '6', 'seventh': '7', 'eighth': '8',
        'ninth': '9', 'tenth': '10', 'twentieth': '20', 'thirtieth': '30',
        'fortieth': '40', 'fiftieth': '50', 'sixtieth': '60',
        'seventieth': '70', 'eightieth': '80', 'ninetieth': '90',
        'hundredth': '100'
    }
    
    # Convert ordinal numbers (e.g., "90th" to "90")
    ref = re.sub(r'(\d+)(?:st|nd|rd|th)', r'\1', ref)
    
    # Standardize common book names and formats
    ref = ref.replace('Doctrine and Covenants', 'D&C')
    ref = ref.replace('Matthew', 'Matt.')
    ref = ref.replace('Nephi', 'Ne.')
    ref = ref.replace('section of the', '')
    ref = ref.replace('verse', '')
    ref = ref.replace('verses', '')
    
    # Replace written numbers with digits
    for word, digit in number_words.items():
        ref = ref.replace(word, digit)
    
    # Regular expressions to match different formats
    patterns = [
        # Standard format: "D&C 90:11"
        r'((?:\d\s+)?[A-Za-z&]+(?:\s+[A-Za-z.]+)?)\s*(?:chapter\s+|section\s+)?(\d+):(\d+(?:-\d+)?)',
        # Verbose format: "90th section... verse 11"
        r'(?:section\s+)?(\d+).*?verse.*?(\d+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, ref, re.IGNORECASE)
        if match:
            if len(match.groups()) == 3:  # Standard format
                book = match.group(1).strip()
                chapter = match.group(2)
                verse_range = match.group(3)
            else:  # Verbose format for D&C
                book = 'D&C'
                chapter = match.group(1)
                verse_range = match.group(2)
            
            # Standardize book names
            if book.startswith(('1 ', '2 ', '3 ', '4 ')):
                number, rest = book.split(' ', 1)
                book = f"{number} {rest}"
            
            # Handle verse ranges
            verses = []
            if '-' in verse_range:
                try:
                    start, end = verse_range.split('-')
                    start = int(start.strip())
                    end = int(end.strip())
                    verses.extend(range(start, end + 1))
                except ValueError:
                    # If there's any issue parsing the range, just use the first number
                    verses = [int(verse_range.split('-')[0].strip())]
            else:
                verses = [int(verse_range.strip())]
            
            return [f"{book} {chapter}:{verse}" for verse in verses]
    
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
                scripture_list = ast.literal_eval(refs)
                # Clean and count each reference
                for ref in scripture_list:
                    cleaned_refs = clean_scripture_ref(ref)
                    if cleaned_refs:  # Now returns a list of references
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