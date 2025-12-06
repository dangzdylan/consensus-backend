# Supabase Schema Requirements

## Required Tables and Fields

Based on the codebase analysis, here are the exact table structures needed:

### 1. `users` Table

**Required Fields:**
- `user_id` (UUID, PRIMARY KEY)
- `username` (TEXT, UNIQUE, NOT NULL)
- `location` (JSONB, default: `{}`)
- `current_lobby_id` (UUID, nullable, foreign key to `lobbies.lobby_id`)
- `is_ready` (BOOLEAN, default: `false`)
- `created_at` (TIMESTAMP, default: `now()`)
- `updated_at` (TIMESTAMP, default: `now()`)

**Optional Fields (for backward compatibility):**
- `email` (TEXT, nullable)

**Indexes:**
- Primary key on `user_id`
- Unique index on `username`
- Index on `current_lobby_id` (for faster lookups)

### 2. `lobbies` Table

**Required Fields:**
- `lobby_id` (UUID, PRIMARY KEY)
- `code` (TEXT, UNIQUE, NOT NULL) - 4-6 character join code
- `host_id` (UUID, NOT NULL, foreign key to `users.user_id`)
- `user_ids` (TEXT[] or JSONB, NOT NULL) - Array of user IDs
- `location` (JSONB, NOT NULL) - `{"latitude": float, "longitude": float}`
- `radius` (FLOAT, NOT NULL)
- `date` (TEXT, NOT NULL) - Format: "MM/DD/YYYY"
- `start_hour` (INTEGER, NOT NULL) - 0-23
- `end_hour` (INTEGER, NOT NULL) - 0-23
- `activity_counts` (JSONB, NOT NULL) - `{"Food": int, "Activity": int, ...}`
- `max_members` (INTEGER, default: 25)
- `status` (TEXT, NOT NULL, default: 'waiting') - Values: 'waiting', 'in_progress', 'completed', 'cancelled'
- `current_round` (INTEGER, default: 0)
- `created_at` (TIMESTAMP, default: `now()`)
- `updated_at` (TIMESTAMP, default: `now()`)

**Indexes:**
- Primary key on `lobby_id`
- Unique index on `code`
- Index on `host_id`
- Index on `status`

### 3. `rounds` Table

**Required Fields:**
- `round_id` (UUID, PRIMARY KEY)
- `lobby_id` (UUID, NOT NULL, foreign key to `lobbies.lobby_id`)
- `round_number` (INTEGER, NOT NULL) - 1-indexed
- `category` (TEXT, NOT NULL) - e.g., "Food", "Recreation & Entertainment", etc.
- `status` (TEXT, NOT NULL, default: 'pending') - Values: 'pending', 'active', 'completed'
- `selected_option_id` (UUID, nullable, foreign key to `options.option_id`)
- `created_at` (TIMESTAMP, default: `now()`)

**Optional Fields (for future tiebreaker support):**
- `is_tiebreaker` (BOOLEAN, default: false)
- `parent_round_id` (UUID, nullable, foreign key to `rounds.round_id`)
- `completed_at` (TIMESTAMP, nullable)

**Constraints:**
- Unique constraint on `(lobby_id, round_number)` - prevents duplicate rounds

**Indexes:**
- Primary key on `round_id`
- Unique index on `(lobby_id, round_number)`
- Index on `lobby_id`
- Index on `status`

### 4. `options` Table

**Required Fields:**
- `option_id` (UUID, PRIMARY KEY)
- `lobby_id` (UUID, NOT NULL, foreign key to `lobbies.lobby_id`)
- `round_number` (INTEGER, NOT NULL)
- `category` (TEXT, NOT NULL)
- `name` (TEXT, NOT NULL)
- `location` (JSONB, NOT NULL) - `{"latitude": float, "longitude": float}`
- `distance` (FLOAT, nullable)
- `image_url` (TEXT, nullable)
- `hours` (JSONB, nullable) - `{"open": int, "close": int, "days": [0-6]}`
- `address` (TEXT, nullable)
- `created_at` (TIMESTAMP, default: `now()`)

**Indexes:**
- Primary key on `option_id`
- Index on `(lobby_id, round_number)` - for faster round option queries
- Index on `lobby_id`

### 5. `votes` Table

**Required Fields:**
- `vote_id` (UUID, PRIMARY KEY)
- `lobby_id` (UUID, NOT NULL, foreign key to `lobbies.lobby_id`)
- `user_id` (UUID, NOT NULL, foreign key to `users.user_id`)
- `option_id` (UUID, NOT NULL, foreign key to `options.option_id`)
- `round_number` (INTEGER, NOT NULL)
- `vote` (BOOLEAN, NOT NULL) - `true` for like/superlike, `false` for dislike
- `created_at` (TIMESTAMP, default: `now()`)

**Constraints:**
- Unique constraint on `(user_id, option_id, round_number)` - prevents duplicate votes from same user

**Indexes:**
- Primary key on `vote_id`
- Unique index on `(user_id, option_id, round_number)`
- Index on `(lobby_id, round_number)` - for faster round vote queries
- Index on `option_id`

## SQL Migration Script

**⚠️ IMPORTANT: Use the complete migration script in `supabase_migration.sql`**

This script is idempotent (safe to run multiple times) and includes:
- All required tables and fields
- Missing column detection and addition
- Proper indexes for performance
- Foreign key constraints with existence checks
- RLS disabled for demo
- Updated_at triggers

For the complete, production-ready migration script, see: **`supabase_migration.sql`**

### Quick Reference (Old Script - Use supabase_migration.sql instead):

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username TEXT UNIQUE NOT NULL,
    email TEXT,
    location JSONB DEFAULT '{}'::jsonb,
    current_lobby_id UUID,
    is_ready BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_current_lobby ON users(current_lobby_id);

-- 2. Lobbies Table
CREATE TABLE IF NOT EXISTS lobbies (
    lobby_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code TEXT UNIQUE NOT NULL,
    host_id UUID NOT NULL,
    user_ids TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
    location JSONB NOT NULL,
    radius FLOAT NOT NULL,
    date TEXT NOT NULL,
    start_hour INTEGER NOT NULL,
    end_hour INTEGER NOT NULL,
    activity_counts JSONB NOT NULL,
    max_members INTEGER DEFAULT 25,
    status TEXT NOT NULL DEFAULT 'waiting',
    current_round INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now(),
    CONSTRAINT check_status CHECK (status IN ('waiting', 'in_progress', 'completed', 'cancelled')),
    CONSTRAINT check_hours CHECK (start_hour >= 0 AND start_hour <= 23 AND end_hour >= 0 AND end_hour <= 23)
);

CREATE INDEX IF NOT EXISTS idx_lobbies_code ON lobbies(code);
CREATE INDEX IF NOT EXISTS idx_lobbies_host ON lobbies(host_id);
CREATE INDEX IF NOT EXISTS idx_lobbies_status ON lobbies(status);

-- 3. Rounds Table
CREATE TABLE IF NOT EXISTS rounds (
    round_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lobby_id UUID NOT NULL,
    round_number INTEGER NOT NULL,
    category TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    selected_option_id UUID,
    is_tiebreaker BOOLEAN DEFAULT false,
    parent_round_id UUID,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT now(),
    CONSTRAINT unique_lobby_round UNIQUE (lobby_id, round_number),
    CONSTRAINT check_round_status CHECK (status IN ('pending', 'active', 'completed'))
);

CREATE INDEX IF NOT EXISTS idx_rounds_lobby ON rounds(lobby_id);
CREATE INDEX IF NOT EXISTS idx_rounds_status ON rounds(status);

-- 4. Options Table
CREATE TABLE IF NOT EXISTS options (
    option_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lobby_id UUID NOT NULL,
    round_number INTEGER NOT NULL,
    category TEXT NOT NULL,
    name TEXT NOT NULL,
    location JSONB NOT NULL,
    distance FLOAT,
    image_url TEXT,
    hours JSONB,
    address TEXT,
    created_at TIMESTAMP DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_options_lobby_round ON options(lobby_id, round_number);
CREATE INDEX IF NOT EXISTS idx_options_lobby ON options(lobby_id);

-- 5. Votes Table
CREATE TABLE IF NOT EXISTS votes (
    vote_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lobby_id UUID NOT NULL,
    user_id UUID NOT NULL,
    option_id UUID NOT NULL,
    round_number INTEGER NOT NULL,
    vote BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT now(),
    CONSTRAINT unique_user_vote UNIQUE (user_id, option_id, round_number)
);

CREATE INDEX IF NOT EXISTS idx_votes_lobby_round ON votes(lobby_id, round_number);
CREATE INDEX IF NOT EXISTS idx_votes_option ON votes(option_id);
CREATE INDEX IF NOT EXISTS idx_votes_user ON votes(user_id);

-- Foreign Key Constraints
ALTER TABLE lobbies 
    ADD CONSTRAINT fk_lobbies_host FOREIGN KEY (host_id) REFERENCES users(user_id) ON DELETE CASCADE;

-- Note: current_lobby_id in users table references lobbies, not a self-reference
-- This foreign key is already handled by the users table constraint

-- Rounds table foreign keys
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_rounds_lobby') THEN
        ALTER TABLE rounds 
            ADD CONSTRAINT fk_rounds_lobby 
            FOREIGN KEY (lobby_id) REFERENCES lobbies(lobby_id) ON DELETE CASCADE;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_rounds_selected_option') THEN
        ALTER TABLE rounds 
            ADD CONSTRAINT fk_rounds_selected_option 
            FOREIGN KEY (selected_option_id) REFERENCES options(option_id) ON DELETE SET NULL;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_rounds_parent_round') THEN
        ALTER TABLE rounds 
            ADD CONSTRAINT fk_rounds_parent_round 
            FOREIGN KEY (parent_round_id) REFERENCES rounds(round_id) ON DELETE SET NULL;
    END IF;
END $$;

-- Options table foreign keys
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_options_lobby') THEN
        ALTER TABLE options 
            ADD CONSTRAINT fk_options_lobby 
            FOREIGN KEY (lobby_id) REFERENCES lobbies(lobby_id) ON DELETE CASCADE;
    END IF;
END $$;

-- Votes table foreign keys
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_votes_lobby') THEN
        ALTER TABLE votes 
            ADD CONSTRAINT fk_votes_lobby 
            FOREIGN KEY (lobby_id) REFERENCES lobbies(lobby_id) ON DELETE CASCADE;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_votes_user') THEN
        ALTER TABLE votes 
            ADD CONSTRAINT fk_votes_user 
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_votes_option') THEN
        ALTER TABLE votes 
            ADD CONSTRAINT fk_votes_option 
            FOREIGN KEY (option_id) REFERENCES options(option_id) ON DELETE CASCADE;
    END IF;
END $$;

-- Update updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at (drop and recreate to avoid errors)
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_lobbies_updated_at ON lobbies;
CREATE TRIGGER update_lobbies_updated_at BEFORE UPDATE ON lobbies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

## Row Level Security (RLS)

**For Demo/MVP: RLS should be DISABLED**

If you need to enable RLS later, you can use:

```sql
-- Disable RLS (for MVP/demo)
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE lobbies DISABLE ROW LEVEL SECURITY;
ALTER TABLE rounds DISABLE ROW LEVEL SECURITY;
ALTER TABLE options DISABLE ROW LEVEL SECURITY;
ALTER TABLE votes DISABLE ROW LEVEL SECURITY;
```

## Common Issues to Check

1. **Missing `is_ready` field in users table** - This was added recently
2. **Missing `current_round` field in lobbies table** - Required for game state
3. **Missing `selected_option_id` in rounds table** - Required for consensus tracking
4. **Status values mismatch** - Ensure status values match exactly: 'waiting', 'in_progress', 'completed', 'cancelled'
5. **Unique constraints** - Ensure `(lobby_id, round_number)` is unique in rounds table
6. **Array type for user_ids** - Should be `TEXT[]` or `JSONB`, not a single TEXT field

## Verification Queries

Run these to verify your schema:

```sql
-- Check users table structure
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'users'
ORDER BY ordinal_position;

-- Check lobbies table structure
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'lobbies'
ORDER BY ordinal_position;

-- Check for required indexes
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename IN ('users', 'lobbies', 'rounds', 'options', 'votes');

-- Check foreign keys
SELECT
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY';
```

