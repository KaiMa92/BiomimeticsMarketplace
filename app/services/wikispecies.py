# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 11:36:52 2024

@author: kaiser
"""

import requests
from PIL import Image
from io import BytesIO
import wikipediaapi
import requests

def get_wikispecies_images(species_name):
    # Prepare the API request URL for the MediaWiki API
    url = "https://species.wikimedia.org/w/api.php"
    
    # Query parameters for searching the page of the given species
    params = {
        "action": "query",
        "format": "json",
        "titles": species_name,
        "prop": "images",
        "imlimit": "max"
    }
    
    # Send the request to the MediaWiki API
    response = requests.get(url, params=params)
    data = response.json()
    
    # Extract the page ID (the key to the page data)
    page_id = next(iter(data["query"]["pages"]))
    
    # Check if the page exists and contains images
    if "images" not in data["query"]["pages"][page_id]:
        print(f"No images found for species: {species_name}")
        return []
    
    # Extract image file titles
    images = data["query"]["pages"][page_id]["images"]
    image_files = [img["title"] for img in images]
    
    # Now retrieve the actual URLs for each image file
    image_urls = []
    for image_file in image_files:
        # Query for the image info, particularly the URL
        params = {
            "action": "query",
            "format": "json",
            "titles": image_file,
            "prop": "imageinfo",
            "iiprop": "url"
        }
        response = requests.get(url, params=params)
        data = response.json()
        
        # Extract the image URL from the response
        page_id = next(iter(data["query"]["pages"]))
        if "imageinfo" in data["query"]["pages"][page_id]:
            image_url = data["query"]["pages"][page_id]["imageinfo"][0]["url"]
            image_urls.append(image_url)
    
    return image_urls

# Example usage
# =============================================================================
# species_name = "Steatornis caripensis"
# image_urls = get_wikispecies_images(species_name)
# 
# if image_urls:
#     print(f"Found {len(image_urls)} images for species '{species_name}':")
#     for url in image_urls:
#         print(url)
# else:
#     print(f"No images found for species '{species_name}'.")
# =============================================================================


def get_image_from_url(url):
    try:
        # Define headers with User-Agent to comply with Wikimedia policy
        headers = {
            'User-Agent': 'BioInfomTechnology/1.0 (AppwebsiteUnderConstruction max.kaiser@ivw.uni-kl.de)'
        }
        
        # Send a GET request with the custom headers
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check if the request was successful

        # Open the image using PIL from the downloaded content
        img = Image.open(BytesIO(response.content))
        return img
    
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve the image: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

def select_url(url_lst):
    if url_lst == []:
        url = 'https://upload.wikimedia.org/wikipedia/commons/f/f3/Wollmilchsau.jpg'
        return url
    else:  
        for url in url_lst: 
            if 'logo' in url: 
                pass
            else: 
                return url
        
def get_image_url(species_name):
    url_lst = get_wikispecies_images(species_name)
    url = select_url(url_lst)
    return url

def get_image(species_name):
    url_lst = get_wikispecies_images(species_name)
    url = select_url(url_lst)
    img = get_image_from_url(url)
    return img

# Example usage
# =============================================================================
# image_url = "https://upload.wikimedia.org/wikipedia/commons/4/4b/Africat_Cheetah.jpg"
# display_image_from_url(image_url)
# =============================================================================

def fetch_first_image_url(search_term):
    # Wikimedia Commons API endpoint
    search_url = "https://commons.wikimedia.org/w/api.php"
    
    # Step 1: Search for the term in the File namespace (images)
    search_params = {
        "action": "query",
        "list": "search",
        "srsearch": search_term,
        "format": "json",
        "srlimit": 1,      # Limit to 1 result
        "srnamespace": 6   # Search only in the File namespace
    }
    response = requests.get(search_url, params=search_params)
    
    # Handle response errors
    if response.status_code != 200:
        raise Exception(f"Error: Failed to fetch search results (HTTP {response.status_code})")
    
    search_results = response.json()
    
    # Check if any results were found
    if not search_results.get('query', {}).get('search'):
        return "No results found."
    
    # Extract the title of the first search result
    first_title = search_results['query']['search'][0]['title']
    
    # Step 2: Fetch image information for the first result
    image_params = {
        "action": "query",
        "titles": first_title,
        "prop": "imageinfo",
        "iiprop": "url",
        "format": "json"
    }
    image_response = requests.get(search_url, params=image_params)
    
    # Handle response errors
    if image_response.status_code != 200:
        raise Exception(f"Error: Failed to fetch image details (HTTP {image_response.status_code})")
    
    image_details = image_response.json()
    
    # Extract the image URL
    pages = image_details.get('query', {}).get('pages', {})
    for page_id, page_data in pages.items():
        if "imageinfo" in page_data:
            return page_data['imageinfo'][0]['url']
    
    return "No image URL found."