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

# ------------------------------------------------------------------------------------------------
# Filters for apostles and prophets
df = df[
    df['author_role'].str.contains('Twelve') |  # Matches any role containing "Twelve"
    df['author_role'].str.contains('First Presidency') |  # Matches First Presidency roles
    df['author_role'].str.contains('President of the Church')  # Exact match for President of the Church
]


# Create a list of all words
all_words = []

for text in df['body_text']:
    # Tokenize the text into words
    words = word_tokenize(text.lower())
    # Keep only words (no numbers or punctuation) longer than 3 characters
    words = [word for word in words if word.isalpha() and len(word) > 3]
    all_words.extend(words)

# Get English stop words and add custom words
stop_words = set(stopwords.words('english'))
custom_stops = {'would', 'said', 'many'}
stop_words.update(custom_stops)

# Count word frequencies, excluding stop words
word_freq = Counter(word for word in all_words if word not in stop_words)

# Get the 20 most common words
top_20 = word_freq.most_common(20)

# Print results
for word, freq in top_20:
    print(f"{word}: {freq}")

print("Stopwords being filtered:", sorted(stopwords.words('english')))

# Configure pandas to show all rows
pd.set_option('display.max_rows', None)  # Show all rows
pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.width', None)  # Don't wrap wide columns
pd.set_option('display.max_colwidth', None)  # Show full content of each column

# Print all unique author roles with counts
roles_df = pd.read_sql_query(
    "SELECT author_role, COUNT(*) as talk_count "
    "FROM talks "
    "GROUP BY author_role "
    "ORDER BY talk_count DESC", 
    conn
)
print("\nUnique author roles and number of talks:")
print(roles_df)

conn.close()