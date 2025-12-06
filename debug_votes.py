import os
import sys
from supabase import create_client
from dotenv import load_dotenv
import json

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")
supabase = create_client(url, key)

lobby_id = "5ddad9b2-70b7-4d4c-bf2c-4f500880e16a"
print(f"Checking votes for lobby: {lobby_id}")

response = supabase.table("votes").select("*").eq("lobby_id", lobby_id).execute()
votes = response.data

print(f"Found {len(votes)} votes")
print(json.dumps(votes, indent=2))

for v in votes:
    val = v.get("vote")
    print(f"Vote ID: {v.get('vote_id')}, Value: {val}, Type: {type(val)}")

