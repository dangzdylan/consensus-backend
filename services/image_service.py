"""
Image service module.
Handles fetching images for places and generating placeholder images.
Completely free implementation - uses DuckDuckGo image search (no API key required).
"""

import requests
from typing import Optional, Dict
from urllib.parse import quote
import re
import json
import time

# Simple in-memory cache to avoid repeated searches for the same place
_image_cache: Dict[str, str] = {}


def generate_placeholder_image_url(name: str) -> Optional[str]:
    """
    Generate a placeholder image URL.
    Returns None to let the frontend handle placeholder display with local assets.
    This avoids network issues with external placeholder services.
    
    Args:
        name: Place name (not used, but kept for API consistency)
        
    Returns:
        None (null in JSON) - frontend should handle placeholder display
    """
    # Return None - the frontend Card component should handle null/undefined
    # image URLs by displaying a local placeholder asset or default image
    # This is more reliable than external services that may be blocked
    return None


def fetch_place_image(place_name: str, category: str = "Food", timeout: float = 2.0) -> Optional[str]:
    """
    Search the web for real images of a specific place using DuckDuckGo.
    Completely free - no API key required.
    Uses caching to avoid repeated searches for the same place.
    Has a short timeout to avoid blocking game start.
    
    Args:
        place_name: Name of the place (e.g., "Pork Store Cafe")
        category: Category of the place (for better search results)
        timeout: Maximum time to wait for image fetch (default 2 seconds)
        
    Returns:
        Image URL string of a real image of the place, or None if not found
    """
    # Check cache first
    cache_key = f"{place_name}_{category}"
    if cache_key in _image_cache:
        return _image_cache[cache_key]
    
    try:
        # Build search query - include location context for better results
        # Add city/area context if available in the place name
        query = place_name
        if category == "Food":
            query = f"{place_name} restaurant"
        elif category in ["Recreation & Entertainment", "Arts", "Social"]:
            query = f"{place_name} {category.lower()}"
        
        # Use DuckDuckGo image search (free, no API key)
        # Step 1: Get the vqd token required for image search
        search_url = "https://duckduckgo.com/"
        params = {
            "q": query
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        
        # Get initial page to extract vqd token
        # Use session to maintain cookies
        # Use short timeout to avoid blocking game start
        session = requests.Session()
        response = session.get(search_url, params=params, headers=headers, timeout=timeout)
        
        if response.status_code != 200:
            return None
        
        # Extract vqd token from the page - try multiple patterns
        vqd = None
        vqd_patterns = [
            r'vqd=([\d-]+)',
            r'vqd["\']?\s*[:=]\s*["\']?([\d-]+)',
            r'"vqd":"([\d-]+)"',
            r"vqd='([\d-]+)'",
            r'vqd:\s*"([\d-]+)"',
        ]
        
        for pattern in vqd_patterns:
            vqd_match = re.search(pattern, response.text)
            if vqd_match:
                vqd = vqd_match.group(1)
                break
        
        if not vqd:
            # Try to extract from script tags
            script_matches = re.findall(r'<script[^>]*>.*?vqd.*?</script>', response.text, re.DOTALL)
            for script in script_matches:
                for pattern in vqd_patterns:
                    vqd_match = re.search(pattern, script)
                    if vqd_match:
                        vqd = vqd_match.group(1)
                        break
                if vqd:
                    break
        
        if not vqd:
            return None
        
        # Step 2: Search for images using the vqd token
        image_search_url = "https://duckduckgo.com/i.js"
        image_params = {
            "q": query,
            "o": "json",
            "p": "1",
            "s": "0",
            "vqd": vqd,
            "f": ",,,",
            "u": "bing"
        }
        
        # Skip delay during game start to avoid blocking
        # Only add delay if we have time
        if timeout > 3:
            time.sleep(0.3)
        
        image_response = session.get(
            image_search_url,
            params=image_params,
            headers=headers,
            timeout=timeout
        )
        
        if image_response.status_code == 200:
            try:
                # DuckDuckGo returns JSON with image results
                data = image_response.json()
                results = data.get("results", [])
                
                if results and len(results) > 0:
                    # Try to get image URL from various possible fields
                    first_result = results[0]
                    
                    # DuckDuckGo image results can have URLs in different fields
                    image_url = (
                        first_result.get("image") or 
                        first_result.get("url") or 
                        first_result.get("thumbnail") or
                        first_result.get("image_url")
                    )
                    
                    if image_url and image_url.startswith("http"):
                        # Cache the result for future use
                        _image_cache[cache_key] = image_url
                        return image_url
            except (json.JSONDecodeError, KeyError, AttributeError) as e:
                print(f"Error parsing image search results for {place_name}: {str(e)}")
                return None
        
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"Network error fetching image for {place_name}: {str(e)}")
        return None
    except Exception as e:
        print(f"Error fetching image for {place_name}: {str(e)}")
        return None


def get_place_image_url(place_name: str, category: str = "Food", fast_mode: bool = True) -> Optional[str]:
    """
    Get image URL for a place. Uses free image services.
    In fast_mode (default), uses short timeout to avoid blocking.
    
    Args:
        place_name: Name of the place
        category: Category of the place
        fast_mode: If True, uses short timeout (2s) to avoid blocking game start
        
    Returns:
        Image URL (either real image or placeholder)
    """
    try:
        # In fast mode, use short timeout to avoid blocking
        timeout = 2.0 if fast_mode else 10.0
        
        # Get unique image for this place
        image_url = fetch_place_image(place_name, category, timeout=timeout)
        
        # If no image found, use placeholder
        if not image_url:
            return generate_placeholder_image_url(place_name)
        
        return image_url
    except Exception as e:
        # If anything fails, return placeholder immediately
        # Don't log errors in fast mode to avoid spam
        if not fast_mode:
            print(f"Error getting image for {place_name}: {str(e)}")
        return generate_placeholder_image_url(place_name)

