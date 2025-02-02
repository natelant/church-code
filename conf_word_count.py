import sqlite3
import pandas as pd
from collections import Counter
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Download ALL required NLTK data (run once)
# Comment out or remove these lines after first successful run
# nltk.download('punkt')
# nltk.download('stopwords')
# nltk.download('punkt_tab')
# nltk.download('averaged_perceptron_tagger')

# Connect to the database
conn = sqlite3.connect('conference_talks.db')

# Read the talks into a pandas DataFrame, filtering for Presidents only
df = pd.read_sql_query(
    "SELECT body_text, "
    "scripture_refs, "
    "date_published, "
    "listed_author, "
    "author_role "
    "FROM talks ", 
    conn
)

# Clean the data
df['date_published'] = pd.to_datetime(df['date_published'])
df['year'] = df['date_published'].dt.year

# First, let's see what roles President Nelson has had
# print("\nPresident Nelson's roles:")
# nelson_roles = df[df['listed_author'].str.contains('Russell M. Nelson', na=False)]['author_role'].unique()
# print(nelson_roles)

# Filters for apostles and prophets
# df = df[
#     df['author_role'].str.contains('Twelve') |  # Matches any role containing "Twelve"
#     df['author_role'].str.contains('First Presidency') |  # Matches First Presidency roles
#     df['author_role'].str.contains('President of [Tt]he Church', regex=True)  # Matches both variations 
# ]

# Filter for years 2015 to present
# df = df[df['year'] >= 2024]

# Filter for name
#df = df[df['listed_author'].str.contains('Russell M. Nelson', na=False)]

# Create a list of all words
all_words = []

for text in df['body_text']:

    # Tokenize the text into words
    words = word_tokenize(text.lower())
    # Keep only words (no numbers or punctuation) longer than 3 characters
    words = [word for word in words if word.isalpha() and len(word) > 2]
    all_words.extend(words)

# Get English stop words and add custom words
stop_words = set(stopwords.words('english'))
custom_stops = {'would', 'said', 'many', 'may', 'day', 'even', 'also',}
stop_words.update(custom_stops)

# Count word frequencies, excluding stop words
word_freq = Counter(word for word in all_words if word not in stop_words)

# Get the 20 most common words
top_20 = word_freq.most_common(50)

# Print analysis information
print(f"\nAnalyzing {len(df)} talks")
print(f"Date range: {df['date_published'].min().strftime('%B %Y')} to {df['date_published'].max().strftime('%B %Y')}")
print(f"Year range: {df['year'].min()} to {df['year'].max()}")

# Print results
for word, freq in top_20:
    print(f"{word}: {freq}")

print("Stopwords being filtered:", sorted(stopwords.words('english')))



conn.close()