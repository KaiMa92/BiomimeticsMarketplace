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


def resolve_abstract(abstract_inverted_index):
    if not abstract_inverted_index:
        return ""

    # Create a dictionary mapping positions to words
    position_word_map = {}
    for word, positions in abstract_inverted_index.items():
        for position in positions:
            position_word_map[position] = word

    # Reconstruct the abstract by iterating over sorted positions
    sorted_positions = sorted(position_word_map.keys())
    abstract = " ".join(position_word_map[pos] for pos in sorted_positions)

    return abstract

def add_abstract(data): 
    for result in data['results']: 
        abstract = resolve_abstract(result['abstract_inverted_index'])
        result['abstract'] = abstract
    return data



base_url = "https://api.openalex.org/works"

# =============================================================================
# query_params = {
#     "search": "Scansorality",
#     # Title contains 'artificial intelligence'
#     "per-page": 10  # Limit results
# }
# 
# response = requests.get(base_url, params=query_params)
# 
# if response.status_code == 200:
#     data = response.json()
#     for work in data['results']:
#         print(f"Title: {work['title']}")
#         print(f"DOI: {work['doi']}")
#         print("-----------")
# else:
#     print(f"Error: {response.status_code} - {response.text}")
# =============================================================================
    
    
#These searches make use of stemming and stop-word removal    
query_params = {
    #"filter": "title_and_abstract.search:vibration",
    "filter": "title_and_abstract.search:Shape%20Memory%20Alloy|Niti,title_and_abstract.search:Composite|hybrid,is_oa:true",
    "per-page": 5  # Limit results
}

response = requests.get(base_url, params=query_params)
data = response.json()
data = add_abstract(data)
#for work in data['results']:
#    print(f"Title: {work['title']}")