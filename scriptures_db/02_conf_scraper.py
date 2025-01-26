import pandas as pd
import requests
import json
import time
from bs4 import BeautifulSoup
from pathlib import Path
import sqlite3
import re

def parse_talk_body(body_html):
    """
    Parse the HTML body content and extract structured text
    """
    soup = BeautifulSoup(body_html, 'html.parser')
    
    # Extract header information
    header = soup.find('header')
    title = header.find('h1').text.strip() if header and header.find('h1') else ''
    author_name = header.find('p', class_='author-name').text.strip() if header and header.find('p', class_='author-name') else ''
    author_role = header.find('p', class_='author-role').text.strip() if header and header.find('p', class_='author-role') else ''
    
    # Extract main content paragraphs
    body_block = soup.find('div', class_='body-block')
    paragraphs = []
    
    if body_block:
        # Remove any script tags
        for script in body_block.find_all('script'):
            script.decompose()
            
        # Remove video elements
        for video in body_block.find_all('video'):
            video.decompose()
            
        # Remove page break spans
        for page_break in body_block.find_all('span', class_='page-break'):
            page_break.decompose()
            
        # Process remaining paragraphs
        for p in body_block.find_all(['p']):
            # Skip if it's a header-related paragraph
            if p.parent.name == 'header' or 'byline' in p.parent.get('class', []):
                continue
                
            # Skip empty paragraphs
            text = p.get_text(strip=True)
            if not text:
                continue
                
            # Handle scripture references
            scripture_refs = []
            for ref in p.find_all('a', class_='scripture-ref'):
                scripture_refs.append({
                    'text': ref.text.strip(),
                    'url': ref.get('href', '')
                })
                
            # Handle poetry
            if 'poetry' in p.get('class', []):
                poetry_lines = [line.text.strip() for line in p.find_all('p', class_='line')]
                if poetry_lines:
                    paragraphs.append({
                        'type': 'poetry',
                        'content': poetry_lines,
                        'scripture_refs': scripture_refs if scripture_refs else None
                    })
            else:
                # Regular paragraph
                paragraphs.append({
                    'type': 'paragraph',
                    'content': text,
                    'scripture_refs': scripture_refs if scripture_refs else None
                })
    
    return {
        'header': {
            'title': title,
            'author_name': author_name.replace('By ', ''),  # Remove 'By ' prefix
            'author_role': author_role
        },
        'paragraphs': paragraphs
    }

def scrape_conference_talk(lang, uri):
    """
    Fetch talk content using the Church's API
    """
    # API endpoint
    url = "https://www.churchofjesuschrist.org/study/api/v3/language-pages/type/content"
    
    # Parameters
    params = {
        "lang": lang,
        "uri": uri
    }
    
    # Headers
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
    }
    
    try:
        # Send GET request
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        # Parse JSON response
        data = response.json()
        
        # Parse the body HTML
        parsed_body = parse_talk_body(data['content']['body'])
        
        # Extract relevant information
        talk_data = {
            "title": data['meta']['title'],
            "description": data['content']['head']['page-meta-social']['pageMeta'].get('description', ''),
            "body_html": data['content']['body'],  # Keep original HTML
            "body_parsed": parsed_body,  # Add parsed content
            "date_published": json.loads(data['meta']['structuredData'])['datePublished'],
            "canonical_url": data['meta']['canonicalUrl'],
            "audio_url": data['meta']['audio'][0]['mediaUrl'] if data['meta'].get('audio') else None,
            "lang": lang,
            "uri": uri
        }
        
        return talk_data
    
    except Exception as e:
        print(f"Error fetching talk {uri}: {str(e)}")
        return None

def clean_text(text):
    """
    Clean text by:
    1. Converting to lowercase
    2. Removing punctuation
    3. Removing extra whitespace
    4. Removing numbers
    """
    # Convert to lowercase
    text = text.lower()
    # Remove punctuation and numbers
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\d+', ' ', text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text

def extract_talk_text(parsed_body):
    """
    Extract all paragraph text from parsed body and combine into single cleaned text
    """
    # Get all paragraph content
    paragraphs = [p['content'] for p in parsed_body['paragraphs'] 
                 if p['type'] == 'paragraph']
    
    # Join paragraphs with space and clean
    full_text = ' '.join(paragraphs)
    return clean_text(full_text)

def extract_scripture_refs(parsed_body):
    """
    Extract all scripture references from parsed body into a list of just the reference text
    """
    scripture_refs = []
    for p in parsed_body['paragraphs']:
        if p.get('scripture_refs'):
            # Only collect the text of each reference, not the URL
            scripture_refs.extend(ref['text'] for ref in p['scripture_refs'])
    return json.dumps(scripture_refs) if scripture_refs else None

def init_database():
    """
    Initialize SQLite database with proper schema
    """
    conn = sqlite3.connect('conference_talks.db')
    c = conn.cursor()
    
    # Create talks table
    c.execute('''
        CREATE TABLE IF NOT EXISTS talks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            body_html TEXT,
            body_parsed TEXT,
            body_text TEXT,
            scripture_refs TEXT,
            date_published TEXT,
            canonical_url TEXT,
            audio_url TEXT,
            lang TEXT,
            uri TEXT,
            listed_author TEXT,
            listed_title TEXT,
            author_role TEXT
        )
    ''')
    
    conn.commit()
    return conn

def process_talks_batch(df, conn):
    """
    Process talks from the DataFrame and store in SQLite
    """
    c = conn.cursor()
    total_talks = len(df)
    
    for idx in range(total_talks):
        row = df.iloc[idx]
        print(f"Processing {row['conference_date']} talk {idx + 1}/{total_talks}: {row['title']} by {row['author']}")
        
        uri = row['href'].split('?')[0].replace('https://www.churchofjesuschrist.org/study', '')
        talk_data = scrape_conference_talk('eng', uri)
        
        if talk_data:
            # Extract author_role from parsed body
            author_role = talk_data['body_parsed']['header']['author_role']
            
            # Extract cleaned text for word analysis
            body_text = extract_talk_text(talk_data['body_parsed'])
            
            # Extract scripture references
            scripture_refs = extract_scripture_refs(talk_data['body_parsed'])
            
            # Add original metadata
            talk_data.update({
                "listed_author": row['author'],
                "listed_title": row['title'],
                "author_role": author_role,
                "body_text": body_text,
                "scripture_refs": scripture_refs
            })
            
            # Insert into database
            c.execute('''
                INSERT INTO talks (
                    title, description, body_html, body_parsed, 
                    body_text, scripture_refs, date_published, canonical_url, 
                    audio_url, lang, uri, listed_author, listed_title,
                    author_role
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                talk_data['title'],
                talk_data['description'],
                talk_data['body_html'],
                json.dumps(talk_data['body_parsed']),
                talk_data['body_text'],
                talk_data['scripture_refs'],
                talk_data['date_published'],
                talk_data['canonical_url'],
                talk_data['audio_url'],
                talk_data['lang'],
                talk_data['uri'],
                talk_data['listed_author'],
                talk_data['listed_title'],
                talk_data['author_role']
            ))
            
            conn.commit()
        
        time.sleep(1)

def main():
    # Initialize database
    conn = init_database()
    
    # Read conference links
    links_df = pd.read_csv('scriptures_db/data/conference_links.csv')
    
    # Process all talks
    process_talks_batch(links_df, conn)
    
    print("\nProcessing complete!")
    conn.close()

if __name__ == "__main__":
    main()

