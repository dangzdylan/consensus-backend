# Environment Variables

This document describes all environment variables needed for the Consensus backend.

## Required Variables

### Supabase Configuration
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_ANON_KEY` - Your Supabase anonymous/public key

### Places API Configuration

You need at least one of the following API keys to fetch restaurants and activities dynamically:

#### Option 1: Yelp Fusion API (Recommended)
- `YELP_API_KEY` - Your Yelp Fusion API key
  - Get one at: https://www.yelp.com/developers/v3/manage_app

#### Option 2: Google Places API
- `GOOGLE_PLACES_API_KEY` - Your Google Places API key
  - Get one at: https://console.cloud.google.com/apis/credentials
  - Enable "Places API" in Google Cloud Console

### API Preference
- `PREFERRED_PLACES_API` - Which API to use: `"yelp"` or `"google"` (default: `"yelp"`)

## Example .env File

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here

# Places API (choose one or both)
YELP_API_KEY=your-yelp-api-key-here
GOOGLE_PLACES_API_KEY=your-google-places-api-key-here

# API Preference
PREFERRED_PLACES_API=yelp
```

## Notes

- If both API keys are provided, the `PREFERRED_PLACES_API` setting determines which one is used
- The application will work without API keys, but places won't be fetched automatically when creating lobbies
- You can manually refresh places using the `/api/lobbies/<lobby_id>/refresh-places` endpoint after setting up API keys

