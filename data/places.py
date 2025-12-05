"""
Hardcoded places data for restaurants and activities.
This includes restaurants, recreation, nature, arts, and social activities.
"""

from typing import List, Dict, Any

# Helper function to parse hours string into hours dict
def parse_hours(hours_str: str) -> Dict[str, Any]:
    """
    Parse hours string into structured format.
    Format: {open: int (0-23), close: int (0-23), days: [0-6]}
    """
    # Default hours if parsing fails
    default = {"open": 11, "close": 22, "days": [0, 1, 2, 3, 4, 5, 6]}
    
    if not hours_str:
        return default
    
    hours_str = hours_str.lower().strip()
    
    # Simple parsing - "Daily" means all days
    if "daily" in hours_str:
        # Try to extract times
        if "11am" in hours_str or "11:30am" in hours_str:
            open_time = 11
        elif "10am" in hours_str:
            open_time = 10
        elif "9am" in hours_str:
            open_time = 9
        elif "8am" in hours_str:
            open_time = 8
        elif "7am" in hours_str:
            open_time = 7
        elif "5pm" in hours_str or "5:30pm" in hours_str:
            open_time = 17
        else:
            open_time = 11
        
        if "10pm" in hours_str or "10:30pm" in hours_str:
            close_time = 22
        elif "9pm" in hours_str or "9:30pm" in hours_str:
            close_time = 21
        elif "11pm" in hours_str:
            close_time = 23
        elif "12am" in hours_str or "midnight" in hours_str:
            close_time = 24
        else:
            close_time = 22
        
        return {"open": open_time, "close": close_time, "days": [0, 1, 2, 3, 4, 5, 6]}
    
    return default


# San Francisco and Berkeley approximate coordinates
# We'll use approximate coordinates - can be refined later with geocoding
SF_CENTER = {"latitude": 37.7749, "longitude": -122.4194}
BERKELEY_CENTER = {"latitude": 37.8715, "longitude": -122.2730}

# Helper to get approximate coordinates based on address
def get_coords(address: str, city: str) -> Dict[str, float]:
    """Get approximate coordinates based on address and city."""
    # For MVP, use city center with slight variations
    if "berkeley" in city.lower():
        base = BERKELEY_CENTER.copy()
    else:
        base = SF_CENTER.copy()
    
    # Add slight variation based on address hash
    addr_hash = abs(hash(address)) % 1000
    base["latitude"] += (addr_hash % 100 - 50) / 10000
    base["longitude"] += ((addr_hash // 100) % 100 - 50) / 10000
    
    return base


# FOOD CATEGORY - Restaurants
FOOD_PLACES: List[Dict[str, Any]] = [
    # San Francisco Restaurants
    {"name": "Pork Store Cafe", "address": "1451 Haight St", "city": "San Francisco", "cuisine": "American", "hours": "7am-3pm", "category": "Food"},
    {"name": "Squat & Gobble", "address": "237 Fillmore St", "city": "San Francisco", "cuisine": "American", "hours": "8am-9pm", "category": "Food"},
    {"name": "Original Joe's", "address": "601 Union St", "city": "San Francisco", "cuisine": "Italian", "hours": "10:30am-1pm", "category": "Food"},
    {"name": "Mamacita", "address": "2317 Chestnut St", "city": "San Francisco", "cuisine": "Mexican", "hours": "5pm-10pm", "category": "Food"},
    {"name": "Tacobar", "address": "2401 Chestnut St", "city": "San Francisco", "cuisine": "Mexican", "hours": "11am-9pm", "category": "Food"},
    {"name": "Delarosa", "address": "2175 Chestnut St", "city": "San Francisco", "cuisine": "Italian", "hours": "11:30am-1pm", "category": "Food"},
    {"name": "Super Duper", "address": "2201 Chestnut St", "city": "San Francisco", "cuisine": "American", "hours": "11am-10pm", "category": "Food"},
    {"name": "Roam Artisan Burgers", "address": "1785 Union St", "city": "San Francisco", "cuisine": "American", "hours": "11:30am-9pm", "category": "Food"},
    {"name": "Causwells", "address": "2346 Chestnut St", "city": "San Francisco", "cuisine": "American", "hours": "11am-9pm", "category": "Food"},
    {"name": "A16", "address": "2355 Chestnut St", "city": "San Francisco", "cuisine": "Italian", "hours": "5pm-10pm", "category": "Food"},
    {"name": "Hog Island Oyster", "address": "1 Ferry Building", "city": "San Francisco", "cuisine": "Seafood", "hours": "Daily 11am-9pm", "category": "Food"},
    {"name": "Tadich Grill", "address": "240 California St", "city": "San Francisco", "cuisine": "Seafood", "hours": "Mon-Sat 11am-9pm", "category": "Food"},
    {"name": "Sam's Grill", "address": "374 Bush St", "city": "San Francisco", "cuisine": "American", "hours": "Mon-Fri 11am-9pm", "category": "Food"},
    {"name": "John's Grill", "address": "63 Ellis St", "city": "San Francisco", "cuisine": "American", "hours": "Daily 11am-10pm", "category": "Food"},
    {"name": "Boulevard", "address": "1 Mission St", "city": "San Francisco", "cuisine": "American", "hours": "Daily 5pm-9:30pm", "category": "Food"},
    {"name": "Waterbar", "address": "399 The Embarcadero", "city": "San Francisco", "cuisine": "Seafood", "hours": "Daily 11:30am-1am", "category": "Food"},
    {"name": "Epic Steak", "address": "369 The Embarcadero", "city": "San Francisco", "cuisine": "Steakhouse", "hours": "Daily 11:30am-9pm", "category": "Food"},
    {"name": "La Mar Cebicheria", "address": "Pier 1.5", "city": "San Francisco", "cuisine": "Peruvian", "hours": "Daily 11am-3pm", "category": "Food"},
    {"name": "Coqueta", "address": "Pier 5", "city": "San Francisco", "cuisine": "Spanish", "hours": "Daily 11:30am-2:30pm", "category": "Food"},
    {"name": "Fog City", "address": "1300 Battery St", "city": "San Francisco", "cuisine": "American", "hours": "Thu-Tue 11am-3pm", "category": "Food"},
    {"name": "Hillstone", "address": "1800 Montgomery St", "city": "San Francisco", "cuisine": "American", "hours": "Daily 5pm-9:30pm", "category": "Food"},
    {"name": "R&G Lounge", "address": "631 Kearny St", "city": "San Francisco", "cuisine": "Chinese", "hours": "Daily 4pm-11pm", "category": "Food"},
    {"name": "Yank Sing", "address": "101 Spear St", "city": "San Francisco", "cuisine": "Chinese", "hours": "Wed-Sun 12pm-9pm", "category": "Food"},
    {"name": "Harborview", "address": "4 Embarcadero Center", "city": "San Francisco", "cuisine": "Chinese", "hours": "Daily 5pm-10pm", "category": "Food"},
    {"name": "Palette Tea House", "address": "900 North Point St", "city": "San Francisco", "cuisine": "Chinese", "hours": "Daily 9am-2pm", "category": "Food"},
    {"name": "Dumpling Time", "address": "11 Division St", "city": "San Francisco", "cuisine": "Chinese", "hours": "Daily 11:30am-8pm", "category": "Food"},
    {"name": "San Tung", "address": "1031 Irving St", "city": "San Francisco", "cuisine": "Chinese", "hours": "Daily 11am-9pm", "category": "Food"},
    {"name": "Burma Superstar", "address": "309 Clement St", "city": "San Francisco", "cuisine": "Burmese", "hours": "Daily 11am-3pm", "category": "Food"},
    {"name": "Mandalay", "address": "4348 California St", "city": "San Francisco", "cuisine": "Burmese", "hours": "Daily 11:30am-9pm", "category": "Food"},
    {"name": "B Star", "address": "127 Clement St", "city": "San Francisco", "cuisine": "Burmese", "hours": "Daily 11am-10pm", "category": "Food"},
    {"name": "Violet's", "address": "2301 Clement St", "city": "San Francisco", "cuisine": "American", "hours": "Daily 5pm-10pm", "category": "Food"},
    {"name": "Fiorella", "address": "2339 Clement St", "city": "San Francisco", "cuisine": "Italian", "hours": "Daily 7am-4pm", "category": "Food"},
    {"name": "Pizzetta 211", "address": "211 23rd Ave", "city": "San Francisco", "cuisine": "Italian", "hours": "Daily 8am-3pm", "category": "Food"},
    {"name": "Pearl 6101", "address": "6101 California St", "city": "San Francisco", "cuisine": "American", "hours": "Daily 8am-9pm", "category": "Food"},
    {"name": "Outerlands", "address": "4001 Judah St", "city": "San Francisco", "cuisine": "American", "hours": "Daily 7am-7pm", "category": "Food"},
    {"name": "Hook Fish Co", "address": "4542 Irving St", "city": "San Francisco", "cuisine": "Seafood", "hours": "Daily 11am-10pm", "category": "Food"},
    {"name": "Palm City Wines", "address": "4055 Irving St", "city": "San Francisco", "cuisine": "Wine Bar", "hours": "Daily 11:30am-8pm", "category": "Food"},
    {"name": "Devil's Teeth Bakery", "address": "3876 Noriega St", "city": "San Francisco", "cuisine": "Bakery", "hours": "Daily 7am-4pm", "category": "Food"},
    {"name": "Brenda's French Soul Food", "address": "652 Polk St", "city": "San Francisco", "cuisine": "French", "hours": "Daily 8am-3pm", "category": "Food"},
    {"name": "Brenda's Meat & Three", "address": "919 Divisadero St", "city": "San Francisco", "cuisine": "American", "hours": "Daily 8am-9pm", "category": "Food"},
    {"name": "The Mill", "address": "736 Divisadero St", "city": "San Francisco", "cuisine": "Cafe", "hours": "Daily 7am-7pm", "category": "Food"},
    {"name": "4505 Burgers & BBQ", "address": "705 Divisadero St", "city": "San Francisco", "cuisine": "American", "hours": "Daily 10:30am-1am", "category": "Food"},
    {"name": "Souvla", "address": "517 Hayes St", "city": "San Francisco", "cuisine": "Greek", "hours": "Daily 11am-10pm", "category": "Food"},
    {"name": "A Mano", "address": "450 Hayes St", "city": "San Francisco", "cuisine": "Italian", "hours": "Daily 11:30am-1am", "category": "Food"},
    {"name": "Monsieur Benjamin", "address": "451 Gough St", "city": "San Francisco", "cuisine": "French", "hours": "Daily 5pm-10pm", "category": "Food"},
    {"name": "Absinthe Brasserie", "address": "398 Hayes St", "city": "San Francisco", "cuisine": "French", "hours": "Wed-Sun 11:30am-1am", "category": "Food"},
    {"name": "Suppenküche", "address": "525 Laguna St", "city": "San Francisco", "cuisine": "German", "hours": "Daily 4pm-12am", "category": "Food"},
    {"name": "Espetus", "address": "1686 Market St", "city": "San Francisco", "cuisine": "Brazilian", "hours": "Tue-Sat 5:30pm-10pm", "category": "Food"},
    {"name": "Zaytoon", "address": "1136 Valencia St", "city": "San Francisco", "cuisine": "Mediterranean", "hours": "Daily 12pm-10pm", "category": "Food"},
    {"name": "Limon", "address": "524 Valencia St", "city": "San Francisco", "cuisine": "Peruvian", "hours": "Daily 5pm-10pm", "category": "Food"},
    {"name": "Tacolicious", "address": "741 Valencia St", "city": "San Francisco", "cuisine": "Mexican", "hours": "Daily 11am-10pm", "category": "Food"},
    {"name": "Beretta", "address": "1199 Valencia St", "city": "San Francisco", "cuisine": "Italian", "hours": "Daily 5pm-10pm", "category": "Food"},
    {"name": "Flour + Water", "address": "2401 Harrison St", "city": "San Francisco", "cuisine": "Italian", "hours": "Daily 5pm-10pm", "category": "Food"},
    {"name": "Farmhouse Kitchen", "address": "710 Florida St", "city": "San Francisco", "cuisine": "Thai", "hours": "Daily 5pm-10pm", "category": "Food"},
    {"name": "Dumpling Home", "address": "298 Gough St", "city": "San Francisco", "cuisine": "Chinese", "hours": "Daily 11am-9pm", "category": "Food"},
    {"name": "Marufuku Ramen", "address": "1581 Webster St", "city": "San Francisco", "cuisine": "Japanese", "hours": "Daily 11:30am-9pm", "category": "Food"},
    {"name": "Hinodeya Ramen", "address": "1737 Buchanan St", "city": "San Francisco", "cuisine": "Japanese", "hours": "Daily 11am-10pm", "category": "Food"},
    {"name": "Nari", "address": "1625 Post St", "city": "San Francisco", "cuisine": "Thai", "hours": "Daily 5pm-9pm", "category": "Food"},
    {"name": "Kin Khao", "address": "55 Cyril Magnin St", "city": "San Francisco", "cuisine": "Thai", "hours": "Daily 5pm-9:30pm", "category": "Food"},
    {"name": "Lolo", "address": "974 Valencia St", "city": "San Francisco", "cuisine": "Mexican", "hours": "Daily 11:30am-2pm", "category": "Food"},
    {"name": "El Techo", "address": "2518 Mission St", "city": "San Francisco", "cuisine": "Latin", "hours": "Tue-Sun 5pm-9:30pm", "category": "Food"},
    {"name": "Rintaro", "address": "82 14th St", "city": "San Francisco", "cuisine": "Japanese", "hours": "Daily 5pm-9pm", "category": "Food"},
    {"name": "True Laurel", "address": "753 Alabama St", "city": "San Francisco", "cuisine": "Cocktail Bar", "hours": "Daily 5pm-10pm", "category": "Food"},
    {"name": "Trick Dog", "address": "3010 20th St", "city": "San Francisco", "cuisine": "Cocktail Bar", "hours": "Daily 4pm-12am", "category": "Food"},
    {"name": "Zeitgeist", "address": "199 Valencia St", "city": "San Francisco", "cuisine": "Bar", "hours": "Daily 11am-2am", "category": "Food"},
    {"name": "Rosamunde", "address": "2832 Mission St", "city": "San Francisco", "cuisine": "German", "hours": "Daily 11am-10pm", "category": "Food"},
    {"name": "Mission Chinese", "address": "2234 Mission St", "city": "San Francisco", "cuisine": "Chinese", "hours": "Daily 5pm-10pm", "category": "Food"},
    {"name": "Lazy Bear", "address": "3416 19th St", "city": "San Francisco", "cuisine": "American", "hours": "Daily 5pm-10pm", "category": "Food"},
    {"name": "Shizen", "address": "370 14th St", "city": "San Francisco", "cuisine": "Japanese", "hours": "Daily 5pm-9:30pm", "category": "Food"},
    {"name": "Cha Cha Cha", "address": "1801 Haight St", "city": "San Francisco", "cuisine": "Caribbean", "hours": "Daily 11am-10pm", "category": "Food"},
    {"name": "Parada 22", "address": "1805 Haight St", "city": "San Francisco", "cuisine": "Puerto Rican", "hours": "Daily 11am-10pm", "category": "Food"},
    {"name": "Magnolia Brewing", "address": "1398 Haight St", "city": "San Francisco", "cuisine": "American", "hours": "Daily 11am-12am", "category": "Food"},
    {"name": "Khana Peena", "address": "5316 College Ave", "city": "Berkeley", "cuisine": "Indian", "hours": "Daily 11am-10pm", "category": "Food"},
    {"name": "Barney's Gourmet Burgers", "address": "1600 Shattuck Ave", "city": "Berkeley", "cuisine": "American", "hours": "Daily 11am-9pm", "category": "Food"},
    {"name": "Super Duper Burgers", "address": "2355 Telegraph Ave", "city": "Berkeley", "cuisine": "American", "hours": "Daily 24 Hours", "category": "Food"},
    {"name": "Zuni Café", "address": "1658 Market St", "city": "San Francisco", "cuisine": "American", "hours": "Tue-Sun 11am-1am", "category": "Food"},
    {"name": "Gary Danko", "address": "800 North Point St", "city": "San Francisco", "cuisine": "French", "hours": "Daily 5pm-10pm", "category": "Food"},
    {"name": "Delfina", "address": "3621 18th St", "city": "San Francisco", "cuisine": "Italian", "hours": "Mon-Fri 11:30am-2pm", "category": "Food"},
    {"name": "Tartine Bakery", "address": "600 Guerrero St", "city": "San Francisco", "cuisine": "Bakery", "hours": "Daily 8am-4pm", "category": "Food"},
    {"name": "Mister Jiu's", "address": "28 Waverly Pl", "city": "San Francisco", "cuisine": "Chinese", "hours": "Tue-Sat 5pm-10pm", "category": "Food"},
    {"name": "Saison", "address": "178 Townsend St", "city": "San Francisco", "cuisine": "American", "hours": "Daily 5pm-10pm", "category": "Food"},
    {"name": "La Taqueria", "address": "2889 Mission St", "city": "San Francisco", "cuisine": "Mexican", "hours": "Daily 11am-9pm", "category": "Food"},
    {"name": "Sotto Mare", "address": "552 Green St", "city": "San Francisco", "cuisine": "Italian", "hours": "Daily 11am-10pm", "category": "Food"},
    {"name": "Swan Oyster Depot", "address": "1517 Polk St", "city": "San Francisco", "cuisine": "Seafood", "hours": "Daily 8am-5:30pm", "category": "Food"},
    
    # Berkeley Restaurants
    {"name": "La Marcha", "address": "2026 San Pablo Ave", "city": "Berkeley", "cuisine": "Spanish", "hours": "Tue-Sun 4pm-10pm", "category": "Food"},
    {"name": "Highwire Coffee", "address": "2300 College Ave", "city": "Berkeley", "cuisine": "Cafe", "hours": "Daily 7am-4pm", "category": "Food"},
    {"name": "Caffe Strada", "address": "2300 Bancroft Way", "city": "Berkeley", "cuisine": "Cafe", "hours": "Daily 6am-12am", "category": "Food"},
    {"name": "Kermit Lynch", "address": "1605 San Pablo Ave", "city": "Berkeley", "cuisine": "French", "hours": "Mon-Fri 8am-5pm", "category": "Food"},
    {"name": "Ramen Shop", "address": "5812 College Ave", "city": "Berkeley", "cuisine": "Japanese", "hours": "Wed-Sun 9am-2pm", "category": "Food"},
    {"name": "Kitchen Story", "address": "3499 16th St", "city": "San Francisco", "cuisine": "American", "hours": "Daily 5pm-12am", "category": "Food"},
    {"name": "Fieldwork Brewing", "address": "1160 Sixth St", "city": "Berkeley", "cuisine": "American", "hours": "Daily 11:30am-9pm", "category": "Food"},
    {"name": "East Bay Spice", "address": "2124 Vine St", "city": "Berkeley", "cuisine": "Indian", "hours": "Daily 11am-9pm", "category": "Food"},
    {"name": "Shen Hua", "address": "5422 College Ave", "city": "Berkeley", "cuisine": "Chinese", "hours": "Daily 5pm-9pm", "category": "Food"},
    {"name": "Manpuku", "address": "2977 College Ave", "city": "Berkeley", "cuisine": "Japanese", "hours": "Daily 11am-9pm", "category": "Food"},
    {"name": "Wood Tavern", "address": "6317 College Ave", "city": "Berkeley", "cuisine": "American", "hours": "Daily 11:30am-9pm", "category": "Food"},
    {"name": "A Côté", "address": "5478 College Ave", "city": "Berkeley", "cuisine": "French", "hours": "Daily 5pm-10pm", "category": "Food"},
    {"name": "Millennium", "address": "5912 College Ave", "city": "Berkeley", "cuisine": "American", "hours": "Daily 5pm-9pm", "category": "Food"},
    {"name": "Yasai", "address": "1820 Euclid Ave", "city": "Berkeley", "cuisine": "Japanese", "hours": "Daily 11am-9pm", "category": "Food"},
    {"name": "Chez Panisse", "address": "1517 Shattuck Ave", "city": "Berkeley", "cuisine": "French", "hours": "Mon-Sat 5:30pm-10pm", "category": "Food"},
    {"name": "Viks Chaat", "address": "2390 Fourth St", "city": "Berkeley", "cuisine": "Indian", "hours": "Daily 11am-6pm", "category": "Food"},
    {"name": "Great China", "address": "2190 Bancroft Way", "city": "Berkeley", "cuisine": "Chinese", "hours": "Wed-Mon 11:30am-9pm", "category": "Food"},
    {"name": "Comal", "address": "2020 Shattuck Ave", "city": "Berkeley", "cuisine": "Mexican", "hours": "Daily 5:30pm-10pm", "category": "Food"},
    {"name": "Cheese Board Pizza", "address": "1512 Shattuck Ave", "city": "Berkeley", "cuisine": "Pizza", "hours": "Tue-Sat 11:30am-2pm", "category": "Food"},
    {"name": "Ippuku", "address": "2130 Center St", "city": "Berkeley", "cuisine": "Japanese", "hours": "Sun-Thu 5pm-10pm", "category": "Food"},
    {"name": "Angeline's Louisiana Kitchen", "address": "2261 Shattuck Ave", "city": "Berkeley", "cuisine": "Cajun", "hours": "Wed-Sun 12pm-9pm", "category": "Food"},
    {"name": "La Note", "address": "2377 Shattuck Ave", "city": "Berkeley", "cuisine": "French", "hours": "Thu-Sun 8am-2pm", "category": "Food"},
    {"name": "Top Dog", "address": "2534 Durant Ave", "city": "Berkeley", "cuisine": "American", "hours": "Daily 10am-12am", "category": "Food"},
    {"name": "Sliver Pizzeria", "address": "2468 Telegraph Ave", "city": "Berkeley", "cuisine": "Pizza", "hours": "Daily 11am-10pm", "category": "Food"},
    {"name": "Kiraku", "address": "2566B Telegraph Ave", "city": "Berkeley", "cuisine": "Japanese", "hours": "Daily 5pm-10:30pm", "category": "Food"},
    {"name": "Revival Bar + Kitchen", "address": "2102 Shattuck Ave", "city": "Berkeley", "cuisine": "American", "hours": "Tue-Sat 4pm-10pm", "category": "Food"},
    {"name": "Jupiter", "address": "2181 Shattuck Ave", "city": "Berkeley", "cuisine": "American", "hours": "Daily 11:30am-10pm", "category": "Food"},
    {"name": "Gather", "address": "2200 Oxford St", "city": "Berkeley", "cuisine": "American", "hours": "Tue-Sat 5pm-9pm", "category": "Food"},
    {"name": "Imm Thai Street Food", "address": "2068 University Ave", "city": "Berkeley", "cuisine": "Thai", "hours": "Daily 11am-10pm", "category": "Food"},
    {"name": "Funky Elephant", "address": "1313 Ninth St", "city": "Berkeley", "cuisine": "Thai", "hours": "Wed-Sun 5pm-9pm", "category": "Food"},
    {"name": "Fish & Bird", "address": "2451 Shattuck Ave", "city": "Berkeley", "cuisine": "Japanese", "hours": "Daily 11:30am-9pm", "category": "Food"},
    {"name": "Agrodolce Osteria", "address": "1730 Shattuck Ave", "city": "Berkeley", "cuisine": "Italian", "hours": "Daily 4:30pm-9:30pm", "category": "Food"},
    {"name": "Trattoria La Siciliana", "address": "2993 College Ave", "city": "Berkeley", "cuisine": "Italian", "hours": "Tue-Sun 5pm-9pm", "category": "Food"},
    {"name": "AKEMI", "address": "1695 Solano Ave", "city": "Berkeley", "cuisine": "Japanese", "hours": "Daily 11:30am-2pm", "category": "Food"},
    {"name": "Ajanta", "address": "1888 Solano Ave", "city": "Berkeley", "cuisine": "Indian", "hours": "Tue-Sun 5pm-9:30pm", "category": "Food"},
    {"name": "Vanessa's Bistro", "address": "1715 Solano Ave", "city": "Berkeley", "cuisine": "French", "hours": "Daily 5pm-9pm", "category": "Food"},
    {"name": "Rivoli", "address": "1539 Solano Ave", "city": "Berkeley", "cuisine": "Italian", "hours": "Daily 5pm-9:30pm", "category": "Food"},
    {"name": "Corso", "address": "1788 Shattuck Ave", "city": "Berkeley", "cuisine": "Italian", "hours": "Daily 11am-9pm", "category": "Food"},
    {"name": "Grégoire", "address": "2109 Cedar St", "city": "Berkeley", "cuisine": "French", "hours": "Daily 10:30am-9pm", "category": "Food"},
    {"name": "Saul's Restaurant", "address": "1475 Shattuck Ave", "city": "Berkeley", "cuisine": "Jewish", "hours": "Daily 8am-9pm", "category": "Food"},
    {"name": "Ferdinand's", "address": "2598 Telegraph Ave", "city": "Berkeley", "cuisine": "Filipino", "hours": "Daily 11am-10pm", "category": "Food"},
    {"name": "Mezzo", "address": "2442 Telegraph Ave", "city": "Berkeley", "cuisine": "Italian", "hours": "Daily 1pm-12am", "category": "Food"},
    {"name": "Raleigh's Pub", "address": "2438 Telegraph Ave", "city": "Berkeley", "cuisine": "American", "hours": "Daily 11am-12am", "category": "Food"},
    {"name": "Cream", "address": "2399 Telegraph Ave", "city": "Berkeley", "cuisine": "Dessert", "hours": "Daily 11am-12am", "category": "Food"},
    {"name": "Artichoke Basille's Pizza", "address": "2590 Durant Ave", "city": "Berkeley", "cuisine": "Pizza", "hours": "Daily 11am-12am", "category": "Food"},
    {"name": "Gypsy's Trattoria", "address": "2514 Durant Ave", "city": "Berkeley", "cuisine": "Italian", "hours": "Daily 10am-11pm", "category": "Food"},
    {"name": "KoJa Kitchen", "address": "2395 Telegraph Ave", "city": "Berkeley", "cuisine": "Korean", "hours": "Daily 11am-9pm", "category": "Food"},
    {"name": "Marugame Udon", "address": "1919 Shattuck Ave", "city": "Berkeley", "cuisine": "Japanese", "hours": "Daily 11am-9pm", "category": "Food"},
    {"name": "Eureka!", "address": "2068 Center St", "city": "Berkeley", "cuisine": "American", "hours": "Daily 11am-11pm", "category": "Food"},
    {"name": "Tacos Sinaloa", "address": "2384 Telegraph Ave", "city": "Berkeley", "cuisine": "Mexican", "hours": "Daily 10am-10pm", "category": "Food"},
    {"name": "Cancun", "address": "2134 Allston Way", "city": "Berkeley", "cuisine": "Mexican", "hours": "Daily 10am-9pm", "category": "Food"},
    {"name": "La Mission", "address": "1255 University Ave", "city": "Berkeley", "cuisine": "Mexican", "hours": "Daily 9am-9pm", "category": "Food"},
    {"name": "Picante", "address": "1328 Sixth St", "city": "Berkeley", "cuisine": "Mexican", "hours": "Daily 11am-9pm", "category": "Food"},
    {"name": "Standard Fare", "address": "2701 Eighth St", "city": "Berkeley", "cuisine": "American", "hours": "Mon-Fri 8:30am-5pm", "category": "Food"},
    {"name": "900 Grayson", "address": "900 Grayson St", "city": "Berkeley", "cuisine": "American", "hours": "Mon-Fri 8am-2pm", "category": "Food"},
    {"name": "Bette's Oceanview Diner", "address": "1807 Fourth St", "city": "Berkeley", "cuisine": "American", "hours": "Daily 9am-2pm", "category": "Food"},
    {"name": "Tacubaya", "address": "1788 Fourth St", "city": "Berkeley", "cuisine": "Mexican", "hours": "Daily 11am-8pm", "category": "Food"},
    {"name": "Zut!", "address": "1820 Fourth St", "city": "Berkeley", "cuisine": "Mediterranean", "hours": "Daily 11:30am-9pm", "category": "Food"},
    {"name": "Iyasare", "address": "1830 Fourth St", "city": "Berkeley", "cuisine": "Japanese", "hours": "Daily 11:30am-2pm", "category": "Food"},
    {"name": "Oaktown Spice Shop", "address": "1224 Solano Ave", "city": "Berkeley", "cuisine": "American", "hours": "Daily 10am-6pm", "category": "Food"},
    {"name": "La Val's Pizza", "address": "1834 Euclid Ave", "city": "Berkeley", "cuisine": "American", "hours": "Daily 11am-10pm", "category": "Food"},
    {"name": "Triple Rock Brewing", "address": "1920 Shattuck Ave", "city": "Berkeley", "cuisine": "American", "hours": "Daily 11:30am-11pm", "category": "Food"},
    {"name": "Alborz", "address": "2142 Center St", "city": "Berkeley", "cuisine": "Persian", "hours": "Daily 11am-9:30pm", "category": "Food"},
    {"name": "Chengdu Style", "address": "2600 Bancroft Way", "city": "Berkeley", "cuisine": "Chinese", "hours": "Daily 11am-9pm", "category": "Food"},
    {"name": "Noodle Theory", "address": "6099 Claremont Ave", "city": "Berkeley", "cuisine": "Asian", "hours": "Daily 5pm-9pm", "category": "Food"},
    {"name": "Rick & Ann's", "address": "2922 Domingo Ave", "city": "Berkeley", "cuisine": "American", "hours": "Daily 7:30am-2:30pm", "category": "Food"},
    {"name": "Fournée Bakery", "address": "2903 College Ave", "city": "Berkeley", "cuisine": "Cafe", "hours": "Tue-Sat 8am-2pm", "category": "Food"},
    {"name": "Acacia", "address": "2000 Kala Bagai Way", "city": "Berkeley", "cuisine": "American", "hours": "Daily 11am-9pm", "category": "Food"},
    {"name": "Cholita Linda", "address": "2000 Kala Bagai Way", "city": "Berkeley", "cuisine": "Latin", "hours": "Daily 11am-9pm", "category": "Food"},
    {"name": "Platano", "address": "2042 University Ave", "city": "Berkeley", "cuisine": "Salvadoran", "hours": "Daily 10am-9pm", "category": "Food"},
    {"name": "Brazil Cafe", "address": "1983 Shattuck Ave", "city": "Berkeley", "cuisine": "Brazilian", "hours": "Mon-Sat 11am-8pm", "category": "Food"},
    {"name": "Cafe M", "address": "1799 Fourth St", "city": "Berkeley", "cuisine": "American", "hours": "Daily 8am-2:30pm", "category": "Food"},
    {"name": "Oceanview Diner", "address": "1807 Fourth St", "city": "Berkeley", "cuisine": "American", "hours": "Daily 9am-2pm", "category": "Food"},
    {"name": "Paisan", "address": "2514 San Pablo Ave", "city": "Berkeley", "cuisine": "Italian", "hours": "Daily 4pm-9pm", "category": "Food"},
    {"name": "Longbranch", "address": "2512 San Pablo Ave", "city": "Berkeley", "cuisine": "American", "hours": "Daily 4pm-9pm", "category": "Food"},
    {"name": "Gaumenkitzel", "address": "2121 San Pablo Ave", "city": "Berkeley", "cuisine": "German", "hours": "Wed-Sun 12pm-9pm", "category": "Food"},
]

# RECREATION & ENTERTAINMENT CATEGORY
RECREATION_PLACES: List[Dict[str, Any]] = [
    # San Francisco
    {"name": "AMC Metreon 16", "address": "135 4th St", "city": "San Francisco", "cuisine": "Movie Theater", "hours": "Daily 10am-12am", "category": "Recreation & Entertainment"},
    {"name": "Alamo Drafthouse", "address": "2550 Mission St", "city": "San Francisco", "cuisine": "Movie Theater", "hours": "Daily 11am-12am", "category": "Recreation & Entertainment"},
    {"name": "Lucky Strike", "address": "200 Bush St", "city": "San Francisco", "cuisine": "Bowling", "hours": "Daily 11am-12am", "category": "Recreation & Entertainment"},
    {"name": "Mission Bowling Club", "address": "3176 17th St", "city": "San Francisco", "cuisine": "Bowling", "hours": "Daily 5pm-12am", "category": "Recreation & Entertainment"},
    {"name": "Urban Putt", "address": "1096 S Van Ness Ave", "city": "San Francisco", "cuisine": "Mini Golf", "hours": "Daily 5pm-12am", "category": "Recreation & Entertainment"},
    {"name": "Stagecoach Greens", "address": "1370 46th Ave", "city": "San Francisco", "cuisine": "Mini Golf", "hours": "Daily 10am-10pm", "category": "Recreation & Entertainment"},
    {"name": "Dave & Buster's", "address": "855 Great Mall Dr", "city": "San Francisco", "cuisine": "Arcade", "hours": "Daily 11am-12am", "category": "Recreation & Entertainment"},
    {"name": "Musée Mécanique", "address": "Pier 45", "city": "San Francisco", "cuisine": "Arcade", "hours": "Daily 10am-8pm", "category": "Recreation & Entertainment"},
    {"name": "Escape Room SF", "address": "55 Taylor St", "city": "San Francisco", "cuisine": "Escape Room", "hours": "Daily 12pm-10pm", "category": "Recreation & Entertainment"},
    {"name": "Palace of Fine Arts", "address": "3601 Lyon St", "city": "San Francisco", "cuisine": "Landmark", "hours": "Daily 6am-9pm", "category": "Recreation & Entertainment"},
    {"name": "Pier 39", "address": "Pier 39", "city": "San Francisco", "cuisine": "Entertainment", "hours": "Daily 10am-9pm", "category": "Recreation & Entertainment"},
    {"name": "Fisherman's Wharf", "address": "Fisherman's Wharf", "city": "San Francisco", "cuisine": "Entertainment", "hours": "Daily 24 Hours", "category": "Recreation & Entertainment"},
    {"name": "Golden Gate Park", "address": "Golden Gate Park", "city": "San Francisco", "cuisine": "Park", "hours": "Daily 5am-12am", "category": "Recreation & Entertainment"},
    {"name": "Dolores Park", "address": "Dolores St & 19th St", "city": "San Francisco", "cuisine": "Park", "hours": "Daily 6am-10pm", "category": "Recreation & Entertainment"},
    {"name": "Alcatraz Island", "address": "Alcatraz Island", "city": "San Francisco", "cuisine": "Tour", "hours": "Daily 9am-6pm", "category": "Recreation & Entertainment"},
    {"name": "Cable Car Museum", "address": "1201 Mason St", "city": "San Francisco", "cuisine": "Museum", "hours": "Daily 10am-5pm", "category": "Recreation & Entertainment"},
    {"name": "Exploratorium", "address": "Pier 15", "city": "San Francisco", "cuisine": "Museum", "hours": "Tue-Sun 10am-5pm", "category": "Recreation & Entertainment"},
    {"name": "California Academy of Sciences", "address": "55 Music Concourse Dr", "city": "San Francisco", "cuisine": "Museum", "hours": "Mon-Sat 9:30am-5pm", "category": "Recreation & Entertainment"},
    {"name": "de Young Museum", "address": "50 Hagiwara Tea Garden Dr", "city": "San Francisco", "cuisine": "Museum", "hours": "Tue-Sun 9:30am-5:15pm", "category": "Recreation & Entertainment"},
    {"name": "SFMOMA", "address": "151 3rd St", "city": "San Francisco", "cuisine": "Museum", "hours": "Fri-Tue 10am-5pm", "category": "Recreation & Entertainment"},
    {"name": "Legion of Honor", "address": "100 34th Ave", "city": "San Francisco", "cuisine": "Museum", "hours": "Tue-Sun 9:30am-5:15pm", "category": "Recreation & Entertainment"},
    {"name": "Asian Art Museum", "address": "200 Larkin St", "city": "San Francisco", "cuisine": "Museum", "hours": "Tue-Sun 10am-5pm", "category": "Recreation & Entertainment"},
    {"name": "Walt Disney Family Museum", "address": "104 Montgomery St", "city": "San Francisco", "cuisine": "Museum", "hours": "Wed-Mon 10am-6pm", "category": "Recreation & Entertainment"},
    {"name": "San Francisco Zoo", "address": "1 Zoo Rd", "city": "San Francisco", "cuisine": "Zoo", "hours": "Daily 10am-5pm", "category": "Recreation & Entertainment"},
    {"name": "Aquarium of the Bay", "address": "Pier 39", "city": "San Francisco", "cuisine": "Aquarium", "hours": "Daily 10am-7pm", "category": "Recreation & Entertainment"},
    {"name": "AT&T Park", "address": "24 Willie Mays Plaza", "city": "San Francisco", "cuisine": "Stadium", "hours": "Varies", "category": "Recreation & Entertainment"},
    {"name": "Chase Center", "address": "1 Warriors Way", "city": "San Francisco", "cuisine": "Arena", "hours": "Varies", "category": "Recreation & Entertainment"},
    {"name": "Oracle Park", "address": "24 Willie Mays Plaza", "city": "San Francisco", "cuisine": "Stadium", "hours": "Varies", "category": "Recreation & Entertainment"},
    {"name": "Stern Grove", "address": "19th Ave & Sloat Blvd", "city": "San Francisco", "cuisine": "Park", "hours": "Daily 6am-10pm", "category": "Recreation & Entertainment"},
    {"name": "Presidio", "address": "Presidio", "city": "San Francisco", "cuisine": "Park", "hours": "Daily 6am-10pm", "category": "Recreation & Entertainment"},
    
    # Berkeley
    {"name": "Berkeley Repertory Theatre", "address": "2025 Addison St", "city": "Berkeley", "cuisine": "Theater", "hours": "Varies", "category": "Recreation & Entertainment"},
    {"name": "California Theatre", "address": "2113 Kittredge St", "city": "Berkeley", "cuisine": "Theater", "hours": "Varies", "category": "Recreation & Entertainment"},
    {"name": "Freight & Salvage", "address": "2020 Addison St", "city": "Berkeley", "cuisine": "Music Venue", "hours": "Daily 7pm-11pm", "category": "Recreation & Entertainment"},
    {"name": "Greek Theatre", "address": "2001 Gayley Rd", "city": "Berkeley", "cuisine": "Concert Venue", "hours": "Varies", "category": "Recreation & Entertainment"},
    {"name": "UC Theatre", "address": "2036 University Ave", "city": "Berkeley", "cuisine": "Concert Venue", "hours": "Varies", "category": "Recreation & Entertainment"},
    {"name": "Berkeley Art Museum", "address": "2155 Center St", "city": "Berkeley", "cuisine": "Museum", "hours": "Wed-Sun 11am-7pm", "category": "Recreation & Entertainment"},
    {"name": "Lawrence Hall of Science", "address": "1 Centennial Dr", "city": "Berkeley", "cuisine": "Museum", "hours": "Wed-Sun 10am-5pm", "category": "Recreation & Entertainment"},
    {"name": "UC Berkeley Botanical Garden", "address": "200 Centennial Dr", "city": "Berkeley", "cuisine": "Garden", "hours": "Daily 9am-5pm", "category": "Recreation & Entertainment"},
    {"name": "Tilden Regional Park", "address": "Tilden Park", "city": "Berkeley", "cuisine": "Park", "hours": "Daily 5am-10pm", "category": "Recreation & Entertainment"},
    {"name": "Cesar Chavez Park", "address": "Cesar Chavez Park", "city": "Berkeley", "cuisine": "Park", "hours": "Daily 6am-10pm", "category": "Recreation & Entertainment"},
    {"name": "Berkeley Marina", "address": "Berkeley Marina", "city": "Berkeley", "cuisine": "Marina", "hours": "Daily 6am-10pm", "category": "Recreation & Entertainment"},
    {"name": "Adventure Playground", "address": "1600 University Ave", "city": "Berkeley", "cuisine": "Playground", "hours": "Sat-Sun 11am-4pm", "category": "Recreation & Entertainment"},
    {"name": "Berkeley Bowl", "address": "2020 Oregon St", "city": "Berkeley", "cuisine": "Grocery", "hours": "Daily 9am-9pm", "category": "Recreation & Entertainment"},
    {"name": "Berkeley Rose Garden", "address": "1200 Euclid Ave", "city": "Berkeley", "cuisine": "Garden", "hours": "Daily 6am-10pm", "category": "Recreation & Entertainment"},
]

# NATURE CATEGORY
NATURE_PLACES: List[Dict[str, Any]] = [
    # San Francisco
    {"name": "Golden Gate Park", "address": "Golden Gate Park", "city": "San Francisco", "cuisine": "Park", "hours": "Daily 5am-12am", "category": "Nature"},
    {"name": "Presidio", "address": "Presidio", "city": "San Francisco", "cuisine": "Park", "hours": "Daily 6am-10pm", "category": "Nature"},
    {"name": "Dolores Park", "address": "Dolores St & 19th St", "city": "San Francisco", "cuisine": "Park", "hours": "Daily 6am-10pm", "category": "Nature"},
    {"name": "Crissy Field", "address": "1199 East Beach", "city": "San Francisco", "cuisine": "Beach", "hours": "Daily 6am-10pm", "category": "Nature"},
    {"name": "Ocean Beach", "address": "Ocean Beach", "city": "San Francisco", "cuisine": "Beach", "hours": "Daily 24 Hours", "category": "Nature"},
    {"name": "Baker Beach", "address": "Baker Beach", "city": "San Francisco", "cuisine": "Beach", "hours": "Daily 6am-10pm", "category": "Nature"},
    {"name": "Lands End", "address": "Lands End", "city": "San Francisco", "cuisine": "Trail", "hours": "Daily 6am-10pm", "category": "Nature"},
    {"name": "Twin Peaks", "address": "Twin Peaks", "city": "San Francisco", "cuisine": "Viewpoint", "hours": "Daily 5am-12am", "category": "Nature"},
    {"name": "Buena Vista Park", "address": "Buena Vista Park", "city": "San Francisco", "cuisine": "Park", "hours": "Daily 5am-12am", "category": "Nature"},
    {"name": "Glen Canyon Park", "address": "Glen Canyon Park", "city": "San Francisco", "cuisine": "Park", "hours": "Daily 5am-10pm", "category": "Nature"},
    {"name": "Stern Grove", "address": "19th Ave & Sloat Blvd", "city": "San Francisco", "cuisine": "Park", "hours": "Daily 6am-10pm", "category": "Nature"},
    {"name": "Mount Davidson", "address": "Mount Davidson", "city": "San Francisco", "cuisine": "Trail", "hours": "Daily 5am-10pm", "category": "Nature"},
    {"name": "Corona Heights Park", "address": "Corona Heights Park", "city": "San Francisco", "cuisine": "Park", "hours": "Daily 5am-10pm", "category": "Nature"},
    {"name": "Bernal Heights Park", "address": "Bernal Heights Blvd", "city": "San Francisco", "cuisine": "Park", "hours": "Daily 5am-10pm", "category": "Nature"},
    {"name": "McLaren Park", "address": "McLaren Park", "city": "San Francisco", "cuisine": "Park", "hours": "Daily 5am-10pm", "category": "Nature"},
    {"name": "Fort Funston", "address": "Fort Funston", "city": "San Francisco", "cuisine": "Beach", "hours": "Daily 6am-10pm", "category": "Nature"},
    {"name": "Sutro Baths", "address": "Sutro Baths", "city": "San Francisco", "cuisine": "Ruins", "hours": "Daily 6am-10pm", "category": "Nature"},
    {"name": "Japanese Tea Garden", "address": "75 Hagiwara Tea Garden Dr", "city": "San Francisco", "cuisine": "Garden", "hours": "Daily 9am-5:45pm", "category": "Nature"},
    {"name": "San Francisco Botanical Garden", "address": "1199 9th Ave", "city": "San Francisco", "cuisine": "Garden", "hours": "Daily 7:30am-6pm", "category": "Nature"},
    {"name": "Conservatory of Flowers", "address": "100 John F Kennedy Dr", "city": "San Francisco", "cuisine": "Garden", "hours": "Tue-Sun 10am-4:30pm", "category": "Nature"},
    {"name": "Stow Lake", "address": "Stow Lake", "city": "San Francisco", "cuisine": "Lake", "hours": "Daily 6am-10pm", "category": "Nature"},
    {"name": "Strawberry Hill", "address": "Strawberry Hill", "city": "San Francisco", "cuisine": "Island", "hours": "Daily 6am-10pm", "category": "Nature"},
    {"name": "Alamo Square", "address": "Alamo Square", "city": "San Francisco", "cuisine": "Park", "hours": "Daily 5am-12am", "category": "Nature"},
    {"name": "Washington Square", "address": "Washington Square", "city": "San Francisco", "cuisine": "Park", "hours": "Daily 6am-10pm", "category": "Nature"},
    {"name": "Lafayette Park", "address": "Lafayette Park", "city": "San Francisco", "cuisine": "Park", "hours": "Daily 5am-10pm", "category": "Nature"},
    {"name": "Mission Creek Park", "address": "Mission Creek Park", "city": "San Francisco", "cuisine": "Park", "hours": "Daily 6am-10pm", "category": "Nature"},
    {"name": "Heron's Head Park", "address": "Heron's Head Park", "city": "San Francisco", "cuisine": "Park", "hours": "Daily 6am-10pm", "category": "Nature"},
    {"name": "Candlestick Point", "address": "Candlestick Point", "city": "San Francisco", "cuisine": "Park", "hours": "Daily 6am-10pm", "category": "Nature"},
    
    # Berkeley
    {"name": "Tilden Regional Park", "address": "Tilden Park", "city": "Berkeley", "cuisine": "Park", "hours": "Daily 5am-10pm", "category": "Nature"},
    {"name": "Cesar Chavez Park", "address": "Cesar Chavez Park", "city": "Berkeley", "cuisine": "Park", "hours": "Daily 6am-10pm", "category": "Nature"},
    {"name": "Berkeley Rose Garden", "address": "1200 Euclid Ave", "city": "Berkeley", "cuisine": "Garden", "hours": "Daily 6am-10pm", "category": "Nature"},
    {"name": "UC Berkeley Botanical Garden", "address": "200 Centennial Dr", "city": "Berkeley", "cuisine": "Garden", "hours": "Daily 9am-5pm", "category": "Nature"},
    {"name": "Indian Rock Park", "address": "950 Indian Rock Ave", "city": "Berkeley", "cuisine": "Park", "hours": "Daily 6am-10pm", "category": "Nature"},
    {"name": "Cragmont Park", "address": "Regal Rd", "city": "Berkeley", "cuisine": "Park", "hours": "Daily 6am-10pm", "category": "Nature"},
    {"name": "Willard Park", "address": "Hillegass Ave & Derby St", "city": "Berkeley", "cuisine": "Park", "hours": "Daily 6am-10pm", "category": "Nature"},
    {"name": "Ohlone Park", "address": "Hearst Ave & Milvia St", "city": "Berkeley", "cuisine": "Park", "hours": "Daily 6am-10pm", "category": "Nature"},
    {"name": "Live Oak Park", "address": "1301 Shattuck Ave", "city": "Berkeley", "cuisine": "Park", "hours": "Daily 6am-10pm", "category": "Nature"},
    {"name": "Codornices Park", "address": "1201 Euclid Ave", "city": "Berkeley", "cuisine": "Park", "hours": "Daily 6am-10pm", "category": "Nature"},
    {"name": "Jewel Lake", "address": "Jewel Lake", "city": "Berkeley", "cuisine": "Lake", "hours": "Daily 6am-10pm", "category": "Nature"},
    {"name": "Lake Anza", "address": "Lake Anza", "city": "Berkeley", "cuisine": "Lake", "hours": "Daily 6am-10pm", "category": "Nature"},
    {"name": "Tilden Little Farm", "address": "600 Canon Dr", "city": "Berkeley", "cuisine": "Farm", "hours": "Daily 8:30am-4pm", "category": "Nature"},
    {"name": "Berkeley Marina", "address": "Berkeley Marina", "city": "Berkeley", "cuisine": "Marina", "hours": "Daily 6am-10pm", "category": "Nature"},
    {"name": "Strawberry Creek", "address": "Strawberry Creek", "city": "Berkeley", "cuisine": "Creek", "hours": "Daily 6am-10pm", "category": "Nature"},
    {"name": "Claremont Canyon", "address": "Claremont Canyon", "city": "Berkeley", "cuisine": "Trail", "hours": "Daily 6am-10pm", "category": "Nature"},
    {"name": "Fire Trails", "address": "Fire Trails", "city": "Berkeley", "cuisine": "Trail", "hours": "Daily 6am-10pm", "category": "Nature"},
    {"name": "Grizzly Peak", "address": "Grizzly Peak Blvd", "city": "Berkeley", "cuisine": "Viewpoint", "hours": "Daily 6am-10pm", "category": "Nature"},
]

# ARTS CATEGORY
ARTS_PLACES: List[Dict[str, Any]] = [
    # San Francisco
    {"name": "SFMOMA", "address": "151 3rd St", "city": "San Francisco", "cuisine": "Art Museum", "hours": "Fri-Tue 10am-5pm", "category": "Arts"},
    {"name": "de Young Museum", "address": "50 Hagiwara Tea Garden Dr", "city": "San Francisco", "cuisine": "Art Museum", "hours": "Tue-Sun 9:30am-5:15pm", "category": "Arts"},
    {"name": "Legion of Honor", "address": "100 34th Ave", "city": "San Francisco", "cuisine": "Art Museum", "hours": "Tue-Sun 9:30am-5:15pm", "category": "Arts"},
    {"name": "Asian Art Museum", "address": "200 Larkin St", "city": "San Francisco", "cuisine": "Art Museum", "hours": "Tue-Sun 10am-5pm", "category": "Arts"},
    {"name": "Contemporary Jewish Museum", "address": "736 Mission St", "city": "San Francisco", "cuisine": "Museum", "hours": "Thu-Tue 11am-5pm", "category": "Arts"},
    {"name": "Walt Disney Family Museum", "address": "104 Montgomery St", "city": "San Francisco", "cuisine": "Museum", "hours": "Wed-Mon 10am-6pm", "category": "Arts"},
    {"name": "Cartoon Art Museum", "address": "781 Beach St", "city": "San Francisco", "cuisine": "Museum", "hours": "Tue-Sun 11am-5pm", "category": "Arts"},
    {"name": "Yerba Buena Center for the Arts", "address": "701 Mission St", "city": "San Francisco", "cuisine": "Arts Center", "hours": "Wed-Sun 12pm-6pm", "category": "Arts"},
    {"name": "SF Art Institute", "address": "800 Chestnut St", "city": "San Francisco", "cuisine": "Art School", "hours": "Mon-Fri 9am-5pm", "category": "Arts"},
    {"name": "SF Opera", "address": "301 Van Ness Ave", "city": "San Francisco", "cuisine": "Opera House", "hours": "Varies", "category": "Arts"},
    {"name": "SF Ballet", "address": "455 Franklin St", "city": "San Francisco", "cuisine": "Ballet", "hours": "Varies", "category": "Arts"},
    {"name": "SF Symphony", "address": "201 Van Ness Ave", "city": "San Francisco", "cuisine": "Concert Hall", "hours": "Varies", "category": "Arts"},
    {"name": "American Conservatory Theater", "address": "415 Geary St", "city": "San Francisco", "cuisine": "Theater", "hours": "Varies", "category": "Arts"},
    {"name": "Curran Theatre", "address": "445 Geary St", "city": "San Francisco", "cuisine": "Theater", "hours": "Varies", "category": "Arts"},
    {"name": "Orpheum Theatre", "address": "1192 Market St", "city": "San Francisco", "cuisine": "Theater", "hours": "Varies", "category": "Arts"},
    {"name": "Golden Gate Theatre", "address": "1 Taylor St", "city": "San Francisco", "cuisine": "Theater", "hours": "Varies", "category": "Arts"},
    {"name": "Fillmore", "address": "1805 Geary Blvd", "city": "San Francisco", "cuisine": "Music Venue", "hours": "Varies", "category": "Arts"},
    {"name": "Great American Music Hall", "address": "859 O'Farrell St", "city": "San Francisco", "cuisine": "Music Venue", "hours": "Varies", "category": "Arts"},
    {"name": "The Independent", "address": "628 Divisadero St", "city": "San Francisco", "cuisine": "Music Venue", "hours": "Daily 8pm-2am", "category": "Arts"},
    {"name": "Bottom of the Hill", "address": "1233 17th St", "city": "San Francisco", "cuisine": "Music Venue", "hours": "Daily 8pm-2am", "category": "Arts"},
    {"name": "Slim's", "address": "333 11th St", "city": "San Francisco", "cuisine": "Music Venue", "hours": "Daily 8pm-2am", "category": "Arts"},
    {"name": "Rickshaw Stop", "address": "155 Fell St", "city": "San Francisco", "cuisine": "Music Venue", "hours": "Daily 8pm-2am", "category": "Arts"},
    {"name": "Bimbo's 365 Club", "address": "1025 Columbus Ave", "city": "San Francisco", "cuisine": "Music Venue", "hours": "Varies", "category": "Arts"},
    {"name": "SF Jazz Center", "address": "201 Franklin St", "city": "San Francisco", "cuisine": "Jazz Venue", "hours": "Varies", "category": "Arts"},
    {"name": "Blue Note", "address": "1330 Fillmore St", "city": "San Francisco", "cuisine": "Jazz Venue", "hours": "Daily 6pm-12am", "category": "Arts"},
    {"name": "SF Playhouse", "address": "450 Post St", "city": "San Francisco", "cuisine": "Theater", "hours": "Varies", "category": "Arts"},
    {"name": "Magic Theatre", "address": "Fort Mason", "city": "San Francisco", "cuisine": "Theater", "hours": "Varies", "category": "Arts"},
    {"name": "Marsh", "address": "1062 Valencia St", "city": "San Francisco", "cuisine": "Theater", "hours": "Varies", "category": "Arts"},
    {"name": "Exit Theatre", "address": "156 Eddy St", "city": "San Francisco", "cuisine": "Theater", "hours": "Varies", "category": "Arts"},
    {"name": "Intersection for the Arts", "address": "925 Mission St", "city": "San Francisco", "cuisine": "Arts Center", "hours": "Wed-Sat 12pm-5pm", "category": "Arts"},
    
    # Berkeley
    {"name": "Berkeley Art Museum", "address": "2155 Center St", "city": "Berkeley", "cuisine": "Art Museum", "hours": "Wed-Sun 11am-7pm", "category": "Arts"},
    {"name": "Berkeley Repertory Theatre", "address": "2025 Addison St", "city": "Berkeley", "cuisine": "Theater", "hours": "Varies", "category": "Arts"},
    {"name": "Freight & Salvage", "address": "2020 Addison St", "city": "Berkeley", "cuisine": "Music Venue", "hours": "Daily 7pm-11pm", "category": "Arts"},
    {"name": "Greek Theatre", "address": "2001 Gayley Rd", "city": "Berkeley", "cuisine": "Concert Venue", "hours": "Varies", "category": "Arts"},
    {"name": "UC Theatre", "address": "2036 University Ave", "city": "Berkeley", "cuisine": "Concert Venue", "hours": "Varies", "category": "Arts"},
    {"name": "Ashby Stage", "address": "1901 Ashby Ave", "city": "Berkeley", "cuisine": "Theater", "hours": "Varies", "category": "Arts"},
    {"name": "Aurora Theatre", "address": "2081 Addison St", "city": "Berkeley", "cuisine": "Theater", "hours": "Varies", "category": "Arts"},
    {"name": "Shotgun Players", "address": "1901 Ashby Ave", "city": "Berkeley", "cuisine": "Theater", "hours": "Varies", "category": "Arts"},
    {"name": "Jazzschool", "address": "2087 Addison St", "city": "Berkeley", "cuisine": "Music School", "hours": "Mon-Fri 10am-6pm", "category": "Arts"},
    {"name": "Berkeley Art Center", "address": "1275 Walnut St", "city": "Berkeley", "cuisine": "Arts Center", "hours": "Wed-Sun 12pm-5pm", "category": "Arts"},
    {"name": "Kala Art Institute", "address": "2990 San Pablo Ave", "city": "Berkeley", "cuisine": "Arts Center", "hours": "Tue-Fri 12pm-5pm", "category": "Arts"},
    {"name": "Berkeley Symphony", "address": "2155 Center St", "city": "Berkeley", "cuisine": "Orchestra", "hours": "Varies", "category": "Arts"},
]

# SOCIAL CATEGORY
SOCIAL_PLACES: List[Dict[str, Any]] = [
    # San Francisco
    {"name": "Zeitgeist", "address": "199 Valencia St", "city": "San Francisco", "cuisine": "Bar", "hours": "Daily 11am-2am", "category": "Social"},
    {"name": "Toronado", "address": "547 Haight St", "city": "San Francisco", "cuisine": "Bar", "hours": "Daily 11:30am-2am", "category": "Social"},
    {"name": "The Page", "address": "298 Divisadero St", "city": "San Francisco", "cuisine": "Bar", "hours": "Daily 5pm-2am", "category": "Social"},
    {"name": "The Alembic", "address": "1725 Haight St", "city": "San Francisco", "cuisine": "Bar", "hours": "Daily 5pm-2am", "category": "Social"},
    {"name": "The Willows", "address": "1582 Folsom St", "city": "San Francisco", "cuisine": "Bar", "hours": "Daily 5pm-2am", "category": "Social"},
    {"name": "Smuggler's Cove", "address": "650 Gough St", "city": "San Francisco", "cuisine": "Bar", "hours": "Daily 5pm-1:30am", "category": "Social"},
    {"name": "Trick Dog", "address": "3010 20th St", "city": "San Francisco", "cuisine": "Cocktail Bar", "hours": "Daily 4pm-12am", "category": "Social"},
    {"name": "True Laurel", "address": "753 Alabama St", "city": "San Francisco", "cuisine": "Cocktail Bar", "hours": "Daily 5pm-10pm", "category": "Social"},
    {"name": "The Interval", "address": "Fort Mason", "city": "San Francisco", "cuisine": "Bar", "hours": "Daily 12pm-12am", "category": "Social"},
    {"name": "Comstock Saloon", "address": "155 Columbus Ave", "city": "San Francisco", "cuisine": "Bar", "hours": "Daily 4pm-2am", "category": "Social"},
    {"name": "Vesuvio", "address": "255 Columbus Ave", "city": "San Francisco", "cuisine": "Bar", "hours": "Daily 6am-2am", "category": "Social"},
    {"name": "Specs", "address": "12 William Saroyan Pl", "city": "San Francisco", "cuisine": "Bar", "hours": "Daily 5pm-2am", "category": "Social"},
    {"name": "Li Po", "address": "916 Grant Ave", "city": "San Francisco", "cuisine": "Bar", "hours": "Daily 2pm-2am", "category": "Social"},
    {"name": "The Saloon", "address": "1232 Grant Ave", "city": "San Francisco", "cuisine": "Bar", "hours": "Daily 12pm-2am", "category": "Social"},
    {"name": "Elixir", "address": "3200 16th St", "city": "San Francisco", "cuisine": "Bar", "hours": "Daily 3pm-2am", "category": "Social"},
    {"name": "The Phoenix", "address": "811 Valencia St", "city": "San Francisco", "cuisine": "Bar", "hours": "Daily 12pm-2am", "category": "Social"},
    {"name": "The Homestead", "address": "2301 Folsom St", "city": "San Francisco", "cuisine": "Bar", "hours": "Daily 5pm-2am", "category": "Social"},
    {"name": "The Sycamore", "address": "2140 Mission St", "city": "San Francisco", "cuisine": "Bar", "hours": "Daily 4pm-2am", "category": "Social"},
    {"name": "The Knockout", "address": "3223 Mission St", "city": "San Francisco", "cuisine": "Bar", "hours": "Daily 4pm-2am", "category": "Social"},
    {"name": "The Make-Out Room", "address": "3225 22nd St", "city": "San Francisco", "cuisine": "Bar", "hours": "Daily 5pm-2am", "category": "Social"},
    {"name": "Thee Parkside", "address": "1600 17th St", "city": "San Francisco", "cuisine": "Bar", "hours": "Daily 12pm-2am", "category": "Social"},
    {"name": "Thee Stork Club", "address": "2330 Telegraph Ave", "city": "Oakland", "cuisine": "Bar", "hours": "Daily 4pm-2am", "category": "Social"},
    {"name": "Cafe du Nord", "address": "2174 Market St", "city": "San Francisco", "cuisine": "Bar", "hours": "Daily 7pm-2am", "category": "Social"},
    {"name": "The Stud", "address": "399 9th St", "city": "San Francisco", "cuisine": "Bar", "hours": "Daily 5pm-2am", "category": "Social"},
    {"name": "The Lookout", "address": "3600 16th St", "city": "San Francisco", "cuisine": "Bar", "hours": "Daily 4pm-2am", "category": "Social"},
    {"name": "The Mix", "address": "4086 18th St", "city": "San Francisco", "cuisine": "Bar", "hours": "Daily 2pm-2am", "category": "Social"},
    {"name": "The Eagle", "address": "398 12th St", "city": "San Francisco", "cuisine": "Bar", "hours": "Daily 2pm-2am", "category": "Social"},
    {"name": "The Cinch", "address": "1723 Polk St", "city": "San Francisco", "cuisine": "Bar", "hours": "Daily 12pm-2am", "category": "Social"},
    {"name": "The Pilsner Inn", "address": "225 Church St", "city": "San Francisco", "cuisine": "Bar", "hours": "Daily 12pm-2am", "category": "Social"},
    {"name": "The Mint", "address": "1942 Market St", "city": "San Francisco", "cuisine": "Karaoke", "hours": "Daily 4pm-2am", "category": "Social"},
    {"name": "The Detour", "address": "2200 Market St", "city": "San Francisco", "cuisine": "Bar", "hours": "Daily 4pm-2am", "category": "Social"},
    
    # Berkeley
    {"name": "Jupiter", "address": "2181 Shattuck Ave", "city": "Berkeley", "cuisine": "Bar", "hours": "Daily 11:30am-10pm", "category": "Social"},
    {"name": "Triple Rock Brewing", "address": "1920 Shattuck Ave", "city": "Berkeley", "cuisine": "Brewery", "hours": "Daily 11:30am-11pm", "category": "Social"},
    {"name": "Fieldwork Brewing", "address": "1160 Sixth St", "city": "Berkeley", "cuisine": "Brewery", "hours": "Daily 11:30am-9pm", "category": "Social"},
    {"name": "The Albatross", "address": "1822 San Pablo Ave", "city": "Berkeley", "cuisine": "Bar", "hours": "Daily 4pm-2am", "category": "Social"},
    {"name": "The Pub", "address": "1492 Solano Ave", "city": "Berkeley", "cuisine": "Bar", "hours": "Daily 11am-2am", "category": "Social"},
    {"name": "Raleigh's Pub", "address": "2438 Telegraph Ave", "city": "Berkeley", "cuisine": "Bar", "hours": "Daily 11am-12am", "category": "Social"},
    {"name": "Bobby G's", "address": "2072 University Ave", "city": "Berkeley", "cuisine": "Bar", "hours": "Daily 11am-2am", "category": "Social"},
    {"name": "Kip's Bar & Grill", "address": "2439 Durant Ave", "city": "Berkeley", "cuisine": "Bar", "hours": "Daily 11am-2am", "category": "Social"},
    {"name": "Pappy's", "address": "2367 Telegraph Ave", "city": "Berkeley", "cuisine": "Bar", "hours": "Daily 11am-2am", "category": "Social"},
    {"name": "Henry's", "address": "2600 Durant Ave", "city": "Berkeley", "cuisine": "Bar", "hours": "Daily 11am-2am", "category": "Social"},
    {"name": "Blakes on Telegraph", "address": "2367 Telegraph Ave", "city": "Berkeley", "cuisine": "Bar", "hours": "Daily 11am-2am", "category": "Social"},
    {"name": "The Bear's Lair", "address": "2475 Bancroft Way", "city": "Berkeley", "cuisine": "Bar", "hours": "Daily 11am-2am", "category": "Social"},
    {"name": "Cafe Strada", "address": "2300 Bancroft Way", "city": "Berkeley", "cuisine": "Cafe", "hours": "Daily 6am-12am", "category": "Social"},
    {"name": "Caffe Mediterraneum", "address": "2475 Telegraph Ave", "city": "Berkeley", "cuisine": "Cafe", "hours": "Daily 6am-12am", "category": "Social"},
    {"name": "Au Coquelet", "address": "2000 University Ave", "city": "Berkeley", "cuisine": "Cafe", "hours": "Daily 6am-12am", "category": "Social"},
    {"name": "Cafe Milano", "address": "2522 Bancroft Way", "city": "Berkeley", "cuisine": "Cafe", "hours": "Daily 7am-10pm", "category": "Social"},
    {"name": "Blue Bottle Coffee", "address": "2118 University Ave", "city": "Berkeley", "cuisine": "Cafe", "hours": "Daily 7am-6pm", "category": "Social"},
    {"name": "Philz Coffee", "address": "1600 Shattuck Ave", "city": "Berkeley", "cuisine": "Cafe", "hours": "Daily 6am-8pm", "category": "Social"},
    {"name": "Peet's Coffee", "address": "2124 Vine St", "city": "Berkeley", "cuisine": "Cafe", "hours": "Daily 5:30am-9pm", "category": "Social"},
    {"name": "Highwire Coffee", "address": "2300 College Ave", "city": "Berkeley", "cuisine": "Cafe", "hours": "Daily 7am-4pm", "category": "Social"},
    {"name": "Caffe Strada", "address": "2300 Bancroft Way", "city": "Berkeley", "cuisine": "Cafe", "hours": "Daily 6am-12am", "category": "Social"},
    {"name": "Free Speech Movement Cafe", "address": "Moffitt Library", "city": "Berkeley", "cuisine": "Cafe", "hours": "Mon-Fri 7am-7pm", "category": "Social"},
    {"name": "Musical Offering", "address": "2430 Bancroft Way", "city": "Berkeley", "cuisine": "Cafe", "hours": "Daily 7am-9pm", "category": "Social"},
    {"name": "Babette", "address": "2000 Center St", "city": "Berkeley", "cuisine": "Cafe", "hours": "Daily 7am-6pm", "category": "Social"},
    {"name": "Bartavelle", "address": "1609 Shattuck Ave", "city": "Berkeley", "cuisine": "Cafe", "hours": "Daily 8am-3pm", "category": "Social"},
    {"name": "Elmwood Cafe", "address": "2900 College Ave", "city": "Berkeley", "cuisine": "Cafe", "hours": "Daily 7am-9pm", "category": "Social"},
    {"name": "Baker & Commons", "address": "2100 Center St", "city": "Berkeley", "cuisine": "Cafe", "hours": "Daily 7am-6pm", "category": "Social"},
    {"name": "La Mediterranee", "address": "2936 College Ave", "city": "Berkeley", "cuisine": "Cafe", "hours": "Daily 11am-9pm", "category": "Social"},
]

# Combine all places
ALL_PLACES: List[Dict[str, Any]] = FOOD_PLACES + RECREATION_PLACES + NATURE_PLACES + ARTS_PLACES + SOCIAL_PLACES

