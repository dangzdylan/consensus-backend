"""
Script to fetch and hardcode images for top SF places.
Run this once to populate image URLs.
"""
import requests
import re
import json
import time
from typing import Optional

def fetch_place_image(place_name: str, category: str = "Food") -> Optional[str]:
    """Fetch image URL for a place using DuckDuckGo."""
    try:
        query = f"{place_name} San Francisco {category}"
        search_url = "https://duckduckgo.com/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(search_url, params={"q": query}, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
        
        vqd_match = re.search(r'vqd=([\d-]+)', response.text)
        if not vqd_match:
            return None
        
        vqd = vqd_match.group(1)
        time.sleep(1)  # Rate limiting
        
        image_url = "https://duckduckgo.com/i.js"
        params = {"q": query, "o": "json", "p": "1", "s": "0", "vqd": vqd, "f": ",,,", "u": "bing"}
        img_response = requests.get(image_url, params=params, headers=headers, timeout=10)
        
        if img_response.status_code == 200:
            data = img_response.json()
            results = data.get("results", [])
            if results:
                return results[0].get("image") or results[0].get("url")
    except:
        pass
    return None

# Top 15 SF places per category
PLACES = {
    "Food": [
        "Gary Danko", "Benu", "State Bird Provisions", "Zuni Café", "Tartine Bakery",
        "Hog Island Oyster Co", "House of Prime Rib", "Delfina", "Flour + Water",
        "Foreign Cinema", "Nopa", "Rich Table", "The Progress", "Lazy Bear", "Quince"
    ],
    "Recreation & Entertainment": [
        "Alcatraz Island", "Golden Gate Bridge", "Fisherman's Wharf", "Pier 39",
        "Lombard Street", "Cable Car Museum", "Exploratorium", "California Academy of Sciences",
        "SFMOMA", "de Young Museum", "Asian Art Museum", "Palace of Fine Arts",
        "Coit Tower", "Twin Peaks", "Golden Gate Park"
    ],
    "Nature": [
        "Golden Gate Park", "Presidio", "Lands End", "Crissy Field", "Baker Beach",
        "Ocean Beach", "Twin Peaks", "Mount Davidson", "Glen Canyon Park",
        "Buena Vista Park", "Dolores Park", "Mission Dolores Park", "Alamo Square",
        "Washington Square Park", "Yerba Buena Gardens"
    ],
    "Arts": [
        "SFMOMA", "de Young Museum", "Asian Art Museum", "Legion of Honor",
        "Contemporary Jewish Museum", "Walt Disney Family Museum", "Cartoon Art Museum",
        "Museum of Craft and Design", "Yerba Buena Center for the Arts",
        "American Conservatory Theater", "SF Ballet", "SF Opera", "SF Symphony",
        "Fillmore", "Great American Music Hall"
    ],
    "Social": [
        "Trick Dog", "True Laurel", "Pacific Cocktail Haven", "Smuggler's Cove",
        "The View Lounge", "Top of the Mark", "Tonga Room", "Bourbon & Branch",
        "Comstock Saloon", "Local Edition", "Rickhouse", "Novela", "Blackbird",
        "The Alembic", "Zeitgeist"
    ]
}

if __name__ == "__main__":
    results = {}
    for category, places in PLACES.items():
        print(f"\nFetching images for {category}...")
        results[category] = {}
        for place in places:
            print(f"  {place}...", end=" ", flush=True)
            img = fetch_place_image(place, category)
            results[category][place] = img
            print("✓" if img else "✗")
            time.sleep(1.5)  # Rate limiting
    
    with open("place_images.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nDone! Results saved to place_images.json")

