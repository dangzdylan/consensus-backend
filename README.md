# Consensus Backend

Backend API for the Consensus application.

## Overview

This is the Flask backend server for the Consensus project.

## Setup

See `SETUP.md` for detailed setup instructions.

## Running the Server

1. **Activate your virtual environment** (if not already activated):
   ```bash
   # On Mac/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

2. **Set up environment variables**:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and add your Supabase credentials:
     ```
     SUPABASE_URL=your_supabase_url_here
     SUPABASE_ANON_KEY=your_supabase_anon_key_here
     ```

3. **Run the Flask development server**:
   ```bash
   flask run
   ```
   
   Or using Python directly:
   ```bash
   python app.py
   ```

4. The server will start on `http://127.0.0.1:5000` by default.

5. **To stop the server**, press `Ctrl+C` in your terminal.

## Project Structure

- `app.py` - Flask application entrypoint
- `routes/` - API route handlers
- `models/` - Data models
- `schemas/` - Database schema definitions
- `utils/` - Utility functions
- `tests/` - Test files


