"""
Hardcoded places data for demo - Top 15 SF places per category.
All images are hardcoded for reliable demo experience.
"""

from typing import List, Dict, Any

# San Francisco center coordinates
SF_CENTER = {"latitude": 37.7749, "longitude": -122.4194}

def parse_hours(hours_str: str) -> Dict[str, Any]:
    """Parse hours string into structured format."""
    default = {"open": 11, "close": 22, "days": [0, 1, 2, 3, 4, 5, 6]}
    if not hours_str:
        return default
    hours_str = hours_str.lower().strip()
    if "daily" in hours_str:
        open_time = 11
        close_time = 22
        if "5pm" in hours_str:
            open_time = 17
        if "10pm" in hours_str:
            close_time = 22
        elif "11pm" in hours_str:
            close_time = 23
        return {"open": open_time, "close": close_time, "days": [0, 1, 2, 3, 4, 5, 6]}
    return default

def get_coords(address: str, city: str) -> Dict[str, float]:
    """Get approximate coordinates - all SF places use SF center with variations."""
    base = SF_CENTER.copy()
    addr_hash = abs(hash(address)) % 1000
    base["latitude"] += (addr_hash % 100 - 50) / 10000
    base["longitude"] += ((addr_hash // 100) % 100 - 50) / 10000
    return base

# Top 15 Food Restaurants in SF
FOOD_PLACES: List[Dict[str, Any]] = [
    {"name": "Gary Danko", "address": "800 North Point St", "city": "San Francisco", "cuisine": "French", "hours": "Daily 5pm-10pm", "category": "Food", "image_url": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=500"},
    {"name": "Benu", "address": "22 Hawthorne St", "city": "San Francisco", "cuisine": "Asian Fusion", "hours": "Daily 5pm-9pm", "category": "Food", "image_url": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=500"},
    {"name": "State Bird Provisions", "address": "1529 Fillmore St", "city": "San Francisco", "cuisine": "American", "hours": "Daily 5:30pm-10pm", "category": "Food", "image_url": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=500"},
    {"name": "Zuni Café", "address": "1658 Market St", "city": "San Francisco", "cuisine": "Mediterranean", "hours": "Tue-Sun 11am-1am", "category": "Food", "image_url": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=500"},
    {"name": "Tartine Bakery", "address": "600 Guerrero St", "city": "San Francisco", "cuisine": "Bakery", "hours": "Daily 8am-4pm", "category": "Food", "image_url": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=500"},
    {"name": "Hog Island Oyster Co", "address": "1 Ferry Building", "city": "San Francisco", "cuisine": "Seafood", "hours": "Daily 11am-9pm", "category": "Food", "image_url": "https://images.unsplash.com/photo-1559339352-11d035aa65de?w=500"},
    {"name": "House of Prime Rib", "address": "1906 Van Ness Ave", "city": "San Francisco", "cuisine": "Steakhouse", "hours": "Daily 5pm-10pm", "category": "Food", "image_url": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=500"},
    {"name": "Delfina", "address": "3621 18th St", "city": "San Francisco", "cuisine": "Italian", "hours": "Daily 5:30pm-10pm", "category": "Food", "image_url": "https://images.unsplash.com/photo-1551218808-94e220e084d2?w=500"},
    {"name": "Flour + Water", "address": "2401 Harrison St", "city": "San Francisco", "cuisine": "Italian", "hours": "Daily 5pm-10pm", "category": "Food", "image_url": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=500"},
    {"name": "Foreign Cinema", "address": "2534 Mission St", "city": "San Francisco", "cuisine": "Mediterranean", "hours": "Daily 5:30pm-10pm", "category": "Food", "image_url": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=500"},
    {"name": "Nopa", "address": "560 Divisadero St", "city": "San Francisco", "cuisine": "American", "hours": "Daily 5pm-1am", "category": "Food", "image_url": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=500"},
    {"name": "Rich Table", "address": "199 Gough St", "city": "San Francisco", "cuisine": "American", "hours": "Daily 5:30pm-10pm", "category": "Food", "image_url": "https://images.unsplash.com/photo-1559339352-11d035aa65de?w=500"},
    {"name": "The Progress", "address": "1525 Fillmore St", "city": "San Francisco", "cuisine": "American", "hours": "Daily 5:30pm-10pm", "category": "Food", "image_url": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=500"},
    {"name": "Lazy Bear", "address": "3416 19th St", "city": "San Francisco", "cuisine": "American", "hours": "Daily 5pm-10pm", "category": "Food", "image_url": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=500"},
    {"name": "Quince", "address": "470 Pacific Ave", "city": "San Francisco", "cuisine": "Italian", "hours": "Daily 5:30pm-9:30pm", "category": "Food", "image_url": "https://images.unsplash.com/photo-1551218808-94e220e084d2?w=500"},
]

# Top 15 Recreation & Entertainment in SF
RECREATION_PLACES: List[Dict[str, Any]] = [
    {"name": "Alcatraz Island", "address": "Alcatraz Island", "city": "San Francisco", "cuisine": "Historic Site", "hours": "Daily 9am-6pm", "category": "Recreation & Entertainment", "image_url": "https://images.unsplash.com/photo-1547036967-23d11aacaee0?w=500"},
    {"name": "Golden Gate Bridge", "address": "Golden Gate Bridge", "city": "San Francisco", "cuisine": "Landmark", "hours": "Daily 24 Hours", "category": "Recreation & Entertainment", "image_url": "https://images.unsplash.com/photo-1501594907352-04cda38ebc29?w=500"},
    {"name": "Fisherman's Wharf", "address": "Fisherman's Wharf", "city": "San Francisco", "cuisine": "Waterfront", "hours": "Daily 9am-9pm", "category": "Recreation & Entertainment", "image_url": "https://images.unsplash.com/photo-1547036967-23d11aacaee0?w=500"},
    {"name": "Pier 39", "address": "Pier 39", "city": "San Francisco", "cuisine": "Entertainment", "hours": "Daily 10am-9pm", "category": "Recreation & Entertainment", "image_url": "https://images.unsplash.com/photo-1501594907352-04cda38ebc29?w=500"},
    {"name": "Lombard Street", "address": "Lombard St", "city": "San Francisco", "cuisine": "Landmark", "hours": "Daily 24 Hours", "category": "Recreation & Entertainment", "image_url": "https://images.unsplash.com/photo-1547036967-23d11aacaee0?w=500"},
    {"name": "Cable Car Museum", "address": "1201 Mason St", "city": "San Francisco", "cuisine": "Museum", "hours": "Daily 10am-6pm", "category": "Recreation & Entertainment", "image_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=500"},
    {"name": "Exploratorium", "address": "Pier 15", "city": "San Francisco", "cuisine": "Science Museum", "hours": "Daily 10am-5pm", "category": "Recreation & Entertainment", "image_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=500"},
    {"name": "California Academy of Sciences", "address": "55 Music Concourse Dr", "city": "San Francisco", "cuisine": "Science Museum", "hours": "Daily 9:30am-5pm", "category": "Recreation & Entertainment", "image_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=500"},
    {"name": "SFMOMA", "address": "151 3rd St", "city": "San Francisco", "cuisine": "Art Museum", "hours": "Daily 10am-5pm", "category": "Recreation & Entertainment", "image_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=500"},
    {"name": "de Young Museum", "address": "50 Hagiwara Tea Garden Dr", "city": "San Francisco", "cuisine": "Art Museum", "hours": "Daily 9:30am-5:15pm", "category": "Recreation & Entertainment", "image_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=500"},
    {"name": "Asian Art Museum", "address": "200 Larkin St", "city": "San Francisco", "cuisine": "Art Museum", "hours": "Daily 10am-5pm", "category": "Recreation & Entertainment", "image_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=500"},
    {"name": "Palace of Fine Arts", "address": "3301 Lyon St", "city": "San Francisco", "cuisine": "Landmark", "hours": "Daily 24 Hours", "category": "Recreation & Entertainment", "image_url": "https://images.unsplash.com/photo-1547036967-23d11aacaee0?w=500"},
    {"name": "Coit Tower", "address": "1 Telegraph Hill Blvd", "city": "San Francisco", "cuisine": "Landmark", "hours": "Daily 10am-6pm", "category": "Recreation & Entertainment", "image_url": "https://images.unsplash.com/photo-1501594907352-04cda38ebc29?w=500"},
    {"name": "Twin Peaks", "address": "Twin Peaks Blvd", "city": "San Francisco", "cuisine": "Viewpoint", "hours": "Daily 24 Hours", "category": "Recreation & Entertainment", "image_url": "https://images.unsplash.com/photo-1501594907352-04cda38ebc29?w=500"},
    {"name": "Golden Gate Park", "address": "Golden Gate Park", "city": "San Francisco", "cuisine": "Park", "hours": "Daily 24 Hours", "category": "Recreation & Entertainment", "image_url": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=500"},
]

# Top 15 Nature spots in SF
NATURE_PLACES: List[Dict[str, Any]] = [
    {"name": "Golden Gate Park", "address": "Golden Gate Park", "city": "San Francisco", "cuisine": "Park", "hours": "Daily 24 Hours", "category": "Nature", "image_url": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=500"},
    {"name": "Presidio", "address": "Presidio", "city": "San Francisco", "cuisine": "Park", "hours": "Daily 24 Hours", "category": "Nature", "image_url": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=500"},
    {"name": "Lands End", "address": "Lands End Trail", "city": "San Francisco", "cuisine": "Trail", "hours": "Daily 24 Hours", "category": "Nature", "image_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=500"},
    {"name": "Crissy Field", "address": "Crissy Field", "city": "San Francisco", "cuisine": "Beach", "hours": "Daily 24 Hours", "category": "Nature", "image_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=500"},
    {"name": "Baker Beach", "address": "Baker Beach", "city": "San Francisco", "cuisine": "Beach", "hours": "Daily 24 Hours", "category": "Nature", "image_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=500"},
    {"name": "Ocean Beach", "address": "Ocean Beach", "city": "San Francisco", "cuisine": "Beach", "hours": "Daily 24 Hours", "category": "Nature", "image_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=500"},
    {"name": "Twin Peaks", "address": "Twin Peaks Blvd", "city": "San Francisco", "cuisine": "Viewpoint", "hours": "Daily 24 Hours", "category": "Nature", "image_url": "https://images.unsplash.com/photo-1501594907352-04cda38ebc29?w=500"},
    {"name": "Mount Davidson", "address": "Mount Davidson", "city": "San Francisco", "cuisine": "Park", "hours": "Daily 24 Hours", "category": "Nature", "image_url": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=500"},
    {"name": "Glen Canyon Park", "address": "Glen Canyon Park", "city": "San Francisco", "cuisine": "Park", "hours": "Daily 24 Hours", "category": "Nature", "image_url": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=500"},
    {"name": "Buena Vista Park", "address": "Buena Vista Park", "city": "San Francisco", "cuisine": "Park", "hours": "Daily 24 Hours", "category": "Nature", "image_url": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=500"},
    {"name": "Dolores Park", "address": "Dolores St", "city": "San Francisco", "cuisine": "Park", "hours": "Daily 24 Hours", "category": "Nature", "image_url": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=500"},
    {"name": "Mission Dolores Park", "address": "Mission Dolores Park", "city": "San Francisco", "cuisine": "Park", "hours": "Daily 24 Hours", "category": "Nature", "image_url": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=500"},
    {"name": "Alamo Square", "address": "Alamo Square", "city": "San Francisco", "cuisine": "Park", "hours": "Daily 24 Hours", "category": "Nature", "image_url": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=500"},
    {"name": "Washington Square Park", "address": "Washington Square", "city": "San Francisco", "cuisine": "Park", "hours": "Daily 24 Hours", "category": "Nature", "image_url": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=500"},
    {"name": "Yerba Buena Gardens", "address": "Yerba Buena Gardens", "city": "San Francisco", "cuisine": "Park", "hours": "Daily 24 Hours", "category": "Nature", "image_url": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=500"},
]

# Top 15 Arts venues in SF
ARTS_PLACES: List[Dict[str, Any]] = [
    {"name": "SFMOMA", "address": "151 3rd St", "city": "San Francisco", "cuisine": "Art Museum", "hours": "Daily 10am-5pm", "category": "Arts", "image_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=500"},
    {"name": "de Young Museum", "address": "50 Hagiwara Tea Garden Dr", "city": "San Francisco", "cuisine": "Art Museum", "hours": "Daily 9:30am-5:15pm", "category": "Arts", "image_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=500"},
    {"name": "Asian Art Museum", "address": "200 Larkin St", "city": "San Francisco", "cuisine": "Art Museum", "hours": "Daily 10am-5pm", "category": "Arts", "image_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=500"},
    {"name": "Legion of Honor", "address": "100 34th Ave", "city": "San Francisco", "cuisine": "Art Museum", "hours": "Daily 9:30am-5:15pm", "category": "Arts", "image_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=500"},
    {"name": "Contemporary Jewish Museum", "address": "736 Mission St", "city": "San Francisco", "cuisine": "Museum", "hours": "Daily 11am-5pm", "category": "Arts", "image_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=500"},
    {"name": "Walt Disney Family Museum", "address": "104 Montgomery St", "city": "San Francisco", "cuisine": "Museum", "hours": "Daily 10am-6pm", "category": "Arts", "image_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=500"},
    {"name": "Cartoon Art Museum", "address": "781 Beach St", "city": "San Francisco", "cuisine": "Museum", "hours": "Daily 11am-5pm", "category": "Arts", "image_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=500"},
    {"name": "Museum of Craft and Design", "address": "2569 3rd St", "city": "San Francisco", "cuisine": "Museum", "hours": "Daily 11am-6pm", "category": "Arts", "image_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=500"},
    {"name": "Yerba Buena Center for the Arts", "address": "701 Mission St", "city": "San Francisco", "cuisine": "Arts Center", "hours": "Daily 11am-6pm", "category": "Arts", "image_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=500"},
    {"name": "American Conservatory Theater", "address": "415 Geary St", "city": "San Francisco", "cuisine": "Theater", "hours": "Varies", "category": "Arts", "image_url": "https://images.unsplash.com/photo-1503095396549-807759245b35?w=500"},
    {"name": "SF Ballet", "address": "455 Franklin St", "city": "San Francisco", "cuisine": "Ballet", "hours": "Varies", "category": "Arts", "image_url": "https://images.unsplash.com/photo-1503095396549-807759245b35?w=500"},
    {"name": "SF Opera", "address": "301 Van Ness Ave", "city": "San Francisco", "cuisine": "Opera", "hours": "Varies", "category": "Arts", "image_url": "https://images.unsplash.com/photo-1503095396549-807759245b35?w=500"},
    {"name": "SF Symphony", "address": "201 Van Ness Ave", "city": "San Francisco", "cuisine": "Symphony", "hours": "Varies", "category": "Arts", "image_url": "https://images.unsplash.com/photo-1503095396549-807759245b35?w=500"},
    {"name": "Fillmore", "address": "1805 Geary Blvd", "city": "San Francisco", "cuisine": "Music Venue", "hours": "Varies", "category": "Arts", "image_url": "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=500"},
    {"name": "Great American Music Hall", "address": "859 O'Farrell St", "city": "San Francisco", "cuisine": "Music Venue", "hours": "Varies", "category": "Arts", "image_url": "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=500"},
]

# Top 15 Social venues in SF
SOCIAL_PLACES: List[Dict[str, Any]] = [
    {"name": "Trick Dog", "address": "3010 20th St", "city": "San Francisco", "cuisine": "Cocktail Bar", "hours": "Daily 4pm-12am", "category": "Social", "image_url": "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=500"},
    {"name": "True Laurel", "address": "753 Alabama St", "city": "San Francisco", "cuisine": "Cocktail Bar", "hours": "Daily 5pm-10pm", "category": "Social", "image_url": "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=500"},
    {"name": "Pacific Cocktail Haven", "address": "550 Sutter St", "city": "San Francisco", "cuisine": "Cocktail Bar", "hours": "Daily 5pm-2am", "category": "Social", "image_url": "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=500"},
    {"name": "Smuggler's Cove", "address": "650 Gough St", "city": "San Francisco", "cuisine": "Tiki Bar", "hours": "Daily 5pm-1:30am", "category": "Social", "image_url": "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=500"},
    {"name": "The View Lounge", "address": "780 Mission St", "city": "San Francisco", "cuisine": "Rooftop Bar", "hours": "Daily 5pm-11pm", "category": "Social", "image_url": "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=500"},
    {"name": "Top of the Mark", "address": "999 California St", "city": "San Francisco", "cuisine": "Rooftop Bar", "hours": "Daily 5pm-11pm", "category": "Social", "image_url": "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=500"},
    {"name": "Tonga Room", "address": "950 Mason St", "city": "San Francisco", "cuisine": "Tiki Bar", "hours": "Daily 5pm-12am", "category": "Social", "image_url": "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=500"},
    {"name": "Bourbon & Branch", "address": "501 Jones St", "city": "San Francisco", "cuisine": "Speakeasy", "hours": "Daily 6pm-2am", "category": "Social", "image_url": "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=500"},
    {"name": "Comstock Saloon", "address": "155 Columbus Ave", "city": "San Francisco", "cuisine": "Cocktail Bar", "hours": "Daily 4pm-2am", "category": "Social", "image_url": "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=500"},
    {"name": "Local Edition", "address": "691 Market St", "city": "San Francisco", "cuisine": "Cocktail Bar", "hours": "Daily 5pm-2am", "category": "Social", "image_url": "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=500"},
    {"name": "Rickhouse", "address": "246 Kearny St", "city": "San Francisco", "cuisine": "Cocktail Bar", "hours": "Daily 5pm-2am", "category": "Social", "image_url": "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=500"},
    {"name": "Novela", "address": "662 Mission St", "city": "San Francisco", "cuisine": "Cocktail Bar", "hours": "Daily 5pm-2am", "category": "Social", "image_url": "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=500"},
    {"name": "Blackbird", "address": "2124 Market St", "city": "San Francisco", "cuisine": "Cocktail Bar", "hours": "Daily 5pm-2am", "category": "Social", "image_url": "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=500"},
    {"name": "The Alembic", "address": "1725 Haight St", "city": "San Francisco", "cuisine": "Cocktail Bar", "hours": "Daily 5pm-2am", "category": "Social", "image_url": "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=500"},
    {"name": "Zeitgeist", "address": "199 Valencia St", "city": "San Francisco", "cuisine": "Beer Garden", "hours": "Daily 11am-2am", "category": "Social", "image_url": "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=500"},
]

# Combine all places
ALL_PLACES: List[Dict[str, Any]] = FOOD_PLACES + RECREATION_PLACES + NATURE_PLACES + ARTS_PLACES + SOCIAL_PLACES
