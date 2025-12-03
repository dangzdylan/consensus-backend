"""
Supabase client initialization module.
Handles the setup and configuration of the Supabase client connection.
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Supabase credentials from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise ValueError(
        "SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables"
    )

# Create and export Supabase client instance
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

