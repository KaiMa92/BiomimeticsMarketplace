"""
Created on Tue Dec 17 14:17:26 2024

@author: kaiser
"""

import requests

base_url = "https://api.openalex.org/works"

query_params = {
    "search": "Scansorality",
    # Title contains 'artificial intelligence'
    "per-page": 10  # Limit results
}

response = requests.get(base_url, params=query_params)

if response.status_code == 200:
    data = response.json()
    for work in data['results']:
        print(f"Title: {work['title']}")
        print(f"DOI: {work['doi']}")
        print("-----------")
else:
    print(f"Error: {response.status_code} - {response.text}")
    
    
#These searches make use of stemming and stop-word removal    
query_params = {
    #"filter": "title_and_abstract.search:vibration",
    "filter": "title_and_abstract.search:Shape%20Memory%20Alloy|Niti,title_and_abstract.search:Composite|hybrid,is_oa:true",
    "per-page": 100  # Limit results
}

response = requests.get(base_url, params=query_params)
data = response.json()
for work in data['results']:
    print(f"Title: {work['title']}")