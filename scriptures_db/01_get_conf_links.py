# General Conference Scraper

# 1. Loop through all years and get the links to the talks
# 2. For each link, get the content, title of content, author, title of autor and date
# 3. Store into database

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Testing: Lets get 2018-2019 and build link dataframe

def get_conference_links(url):
    """
    Scrapes conference talks from a given conference URL and returns a DataFrame
    containing href, author, and title information.
    """
    # Initialize lists to store our data
    hrefs = []
    authors = []
    titles = []
    
    # Get the page content
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all talk links (they have specific class and structure)
    talk_links = soup.find_all('a', class_='sc-omeqik-0')
    
    for link in talk_links:
        href = link.get('href')
        
        # Only process links that are actual talks (not session headers)
        author_elem = link.find('p', class_='primaryMeta')
        title_elem = link.find('p', class_='title')
        
        # If we have both author and title, it's a talk (not a session header)
        if author_elem and title_elem:
            # Add the base URL if href is relative
            full_href = f"https://www.churchofjesuschrist.org{href}" if href.startswith('/') else href
            author = author_elem.text.strip()
            title = title_elem.text.strip()
            
            hrefs.append(full_href)
            authors.append(author)
            titles.append(title)
    
    # Create DataFrame
    df = pd.DataFrame({
        'href': hrefs,
        'author': authors,
        'title': titles
    })
    
    return df



def get_all_conference_urls(start_year=1970, end_year=2024):
    """
    Generate URLs for all General Conference sessions between start_year and end_year.
    Conferences are held in April (04) and October (10).
    """
    base_url = "https://www.churchofjesuschrist.org/study/general-conference"
    urls = []
    
    for year in range(start_year, end_year + 1):
        # April Conference
        urls.append(f"{base_url}/{year}/04?lang=eng")
        # October Conference
        urls.append(f"{base_url}/{year}/10?lang=eng")
    
    return urls

def scrape_all_conferences(start_year=1970, end_year=2024):
    """
    Scrape all General Conference talks between start_year and end_year.
    Returns a DataFrame with all talks.
    """
    urls = get_all_conference_urls(start_year, end_year)
    all_links = []
    
    for url in urls:
        try:
            print(f"Scraping: {url}")
            df = get_conference_links(url)
            # Add conference date information
            year = url.split('/')[-2]
            month = url.split('/')[-1].split('?')[0]
            df['conference_date'] = f"{year}-{month}"
            all_links.append(df)
            # Add a small delay to be respectful to the server
            time.sleep(1)
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            continue
    
    # Combine all DataFrames
    if all_links:
        final_df = pd.concat(all_links, ignore_index=True)
        return final_df
    else:
        return pd.DataFrame()

# Test the scraper with a smaller range first
test_df = scrape_all_conferences(1970, 2024)
print(f"Total talks scraped: {len(test_df)}")
print("\nFirst few entries:")
print(test_df.head(100))

# Save to CSV
test_df.to_csv('conference_links.csv', index=False)



