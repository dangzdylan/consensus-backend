try:
    import os
    import sys
    from supabase import create_client
    from dotenv import load_dotenv
    import json

    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")

    if not url or not key:
        print("Missing env vars")
        sys.axis(1)

    supabase = create_client(url, key)

    # Lobby ID from logs
    lobby_id = "82b5cf32-96ec-4a6c-9d16-6585e7a700d7"
    print(f"Checking rounds for lobby: {lobby_id}")

    response = supabase.table("rounds").select("*").eq("lobby_id", lobby_id).execute()
    rounds = response.data

    print(json.dumps(rounds, indent=2))

    if rounds:
        for r in rounds:
            print(f"Round {r.get('round_number')}: Status={r.get('status')}, SelectedOption={r.get('selected_option_id')}")
    else:
        print("No rounds found.")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
