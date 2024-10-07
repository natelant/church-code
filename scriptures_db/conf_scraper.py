import requests
import json

def scrape_conference_talk(lang, uri):
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
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse JSON response
        data = response.json()
        
        # Extract relevant information
        title = data['meta']['title']
        author = data['content']['body'].split('<p class="author-name"')[1].split('>')[1].split('<')[0]
        content = data['content']['body']
        # year and month are in the uri, so we can extract them
        year = uri.split('/')[2]
        month = uri.split('/')[3]
        
        # Create a dictionary with the extracted data
        talk_data = {
            "title": title,
            "author": author,
            "year": year,
            "month": month,
            "content": content,
            "lang": lang,
            "uri": uri
        }
        
        return talk_data
    
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

# Example usage
lang = "eng"
uri = "/general-conference/2024/04/13holland"
result = scrape_conference_talk(lang, uri)

if result:
    print(f"Title: {result['title']}")
    print(f"Author: {result['author']}")
    print(f"Content length: {len(result['content'])} characters")
    # You can save the result to a file or process it further as needed
else:
    print("Failed to scrape the talk.")
