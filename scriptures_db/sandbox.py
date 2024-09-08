import json
import pandas as pd
from collections import Counter
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Load the JSON data
with open('scriptures_db/data/json/lds-scriptures-json.txt', 'r') as file:
    scriptures_data = json.load(file)

# Create a list to store the data
data = []

# Process each verse
for verse in scriptures_data:
    volume_title = verse['volume_title']
    book_title = verse['book_title']
    chapter = verse['chapter_number']
    words = verse['scripture_text'].split()
    
    # Add an entry for each word
    for word in words:
        data.append({
            'volume_title': volume_title,
            'book_title': book_title,
            'chapter': chapter,
            'word': word.lower()  # Convert to lowercase for consistency
        })

# Create a DataFrame
df = pd.DataFrame(data)

# Calculate word frequencies
word_counts = Counter(df['word'])

# Add word frequency to the DataFrame
df['frequency'] = df['word'].map(word_counts)

# Filter by names from names_of_christ.csv
names_of_christ = pd.read_csv('scriptures_db/data/names_of_christ.csv')
names_of_christ_list = names_of_christ['name'].tolist()

print(names_of_christ_list)

# Filter the DataFrame and get rid of duplicates
df_filtered = df[df['word'].isin(names_of_christ_list)].drop_duplicates()

# Group by word and volume_title, then unstack
df_grouped = df_filtered.groupby(['word', 'volume_title']).size().unstack().fillna(0)

# Sort the DataFrame based on the 'Book of Mormon' column in descending order
df_grouped = df_grouped.sort_values(by='Book of Mormon', ascending=False)

# Create a grouped bar chart using Plotly
fig = go.Figure()

for volume in df_grouped.columns:
    fig.add_trace(go.Bar(
        x=df_grouped.index,
        y=df_grouped[volume],
        name=volume,
        text=df_grouped[volume],
        textposition='auto'
    ))

fig.update_layout(
    title='Frequency of Names of Christ by Volume (Sorted by Book of Mormon)',
    xaxis_title='Names of Christ',
    yaxis_title='Frequency',
    barmode='group',
    height=600,
    width=1200,
    legend_title='Volume Title',
    legend=dict(x=1.05, y=1, xanchor='left', yanchor='top')
)

fig.show()

# word clouds
# Import necessary libraries
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Define common words to be eliminated
common_words = set(['the', 'and', 'of', 'to', 'in', 'that', 'for', 'is', 'on', 'with', 'by', 'as', 'be', 'at', 'this', 'was', 'are', 'from', 'it', 'an', 'not', 'or', 'have', 'all', 'they', 'which', 'but', 'we', 'he', 'she', 'you', 'who', 'them', 'his', 'her', 'their', 'our', 'your', 'its'])

# Function to create and save word cloud
def create_word_cloud(text, title):
    # Create WordCloud object
    wordcloud = WordCloud(width=800, height=400, background_color='white', stopwords=common_words).generate(text)
    
    # Display the generated image
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(title)
    
    # Save the image
    plt.savefig(f'wordcloud_{title.lower().replace(" ", "_")}.png', bbox_inches='tight')
    plt.close()

# Create word clouds for each volume title
for volume in df['volume_title'].unique():
    # Filter data for the current volume
    volume_data = df[df['volume_title'] == volume]
    
    # Combine all words in the volume
    text = ' '.join(volume_data['word'])
    
    # Create and save word cloud
    create_word_cloud(text, volume)

print("Word clouds have been generated and saved.")
