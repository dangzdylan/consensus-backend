-- ============================================
-- Supabase Migration Script for Consensus Backend
-- Run this in Supabase SQL Editor
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- 1. USERS TABLE
-- ============================================
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

-- Add missing columns if they don't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'is_ready') THEN
        ALTER TABLE users ADD COLUMN is_ready BOOLEAN DEFAULT false;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'location') THEN
        ALTER TABLE users ADD COLUMN location JSONB DEFAULT '{}'::jsonb;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'current_lobby_id') THEN
        ALTER TABLE users ADD COLUMN current_lobby_id UUID;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_current_lobby ON users(current_lobby_id);

-- ============================================
-- 2. LOBBIES TABLE
-- ============================================
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

-- Add missing columns if they don't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'lobbies' AND column_name = 'current_round') THEN
        ALTER TABLE lobbies ADD COLUMN current_round INTEGER DEFAULT 0;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'lobbies' AND column_name = 'date') THEN
        ALTER TABLE lobbies ADD COLUMN date TEXT NOT NULL DEFAULT '';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'lobbies' AND column_name = 'start_hour') THEN
        ALTER TABLE lobbies ADD COLUMN start_hour INTEGER NOT NULL DEFAULT 12;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'lobbies' AND column_name = 'end_hour') THEN
        ALTER TABLE lobbies ADD COLUMN end_hour INTEGER NOT NULL DEFAULT 18;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'lobbies' AND column_name = 'activity_counts') THEN
        ALTER TABLE lobbies ADD COLUMN activity_counts JSONB NOT NULL DEFAULT '{}'::jsonb;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_lobbies_code ON lobbies(code);
CREATE INDEX IF NOT EXISTS idx_lobbies_host ON lobbies(host_id);
CREATE INDEX IF NOT EXISTS idx_lobbies_status ON lobbies(status);

-- ============================================
-- 3. ROUNDS TABLE
-- ============================================
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

-- Add missing columns if they don't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'rounds' AND column_name = 'selected_option_id') THEN
        ALTER TABLE rounds ADD COLUMN selected_option_id UUID;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'rounds' AND column_name = 'is_tiebreaker') THEN
        ALTER TABLE rounds ADD COLUMN is_tiebreaker BOOLEAN DEFAULT false;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'rounds' AND column_name = 'parent_round_id') THEN
        ALTER TABLE rounds ADD COLUMN parent_round_id UUID;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'rounds' AND column_name = 'completed_at') THEN
        ALTER TABLE rounds ADD COLUMN completed_at TIMESTAMP;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_rounds_lobby ON rounds(lobby_id);
CREATE INDEX IF NOT EXISTS idx_rounds_status ON rounds(status);

-- ============================================
-- 4. OPTIONS TABLE
-- ============================================
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

-- Add missing columns if they don't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'options' AND column_name = 'image_url') THEN
        ALTER TABLE options ADD COLUMN image_url TEXT;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_options_lobby_round ON options(lobby_id, round_number);
CREATE INDEX IF NOT EXISTS idx_options_lobby ON options(lobby_id);

-- ============================================
-- 5. VOTES TABLE
-- ============================================
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

-- ============================================
-- FOREIGN KEY CONSTRAINTS
-- ============================================

-- Users -> Lobbies (current_lobby_id)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_users_current_lobby') THEN
        ALTER TABLE users 
            ADD CONSTRAINT fk_users_current_lobby 
            FOREIGN KEY (current_lobby_id) REFERENCES lobbies(lobby_id) ON DELETE SET NULL;
    END IF;
END $$;

-- Lobbies -> Users (host_id)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_lobbies_host') THEN
        ALTER TABLE lobbies 
            ADD CONSTRAINT fk_lobbies_host 
            FOREIGN KEY (host_id) REFERENCES users(user_id) ON DELETE CASCADE;
    END IF;
END $$;

-- Rounds -> Lobbies
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_rounds_lobby') THEN
        ALTER TABLE rounds 
            ADD CONSTRAINT fk_rounds_lobby 
            FOREIGN KEY (lobby_id) REFERENCES lobbies(lobby_id) ON DELETE CASCADE;
    END IF;
END $$;

-- Rounds -> Options (selected_option_id)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_rounds_selected_option') THEN
        ALTER TABLE rounds 
            ADD CONSTRAINT fk_rounds_selected_option 
            FOREIGN KEY (selected_option_id) REFERENCES options(option_id) ON DELETE SET NULL;
    END IF;
END $$;

-- Rounds -> Rounds (parent_round_id for tiebreakers)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_rounds_parent_round') THEN
        ALTER TABLE rounds 
            ADD CONSTRAINT fk_rounds_parent_round 
            FOREIGN KEY (parent_round_id) REFERENCES rounds(round_id) ON DELETE SET NULL;
    END IF;
END $$;

-- Options -> Lobbies
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_options_lobby') THEN
        ALTER TABLE options 
            ADD CONSTRAINT fk_options_lobby 
            FOREIGN KEY (lobby_id) REFERENCES lobbies(lobby_id) ON DELETE CASCADE;
    END IF;
END $$;

-- Votes -> Lobbies
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_votes_lobby') THEN
        ALTER TABLE votes 
            ADD CONSTRAINT fk_votes_lobby 
            FOREIGN KEY (lobby_id) REFERENCES lobbies(lobby_id) ON DELETE CASCADE;
    END IF;
END $$;

-- Votes -> Users
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_votes_user') THEN
        ALTER TABLE votes 
            ADD CONSTRAINT fk_votes_user 
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE;
    END IF;
END $$;

-- Votes -> Options
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_votes_option') THEN
        ALTER TABLE votes 
            ADD CONSTRAINT fk_votes_option 
            FOREIGN KEY (option_id) REFERENCES options(option_id) ON DELETE CASCADE;
    END IF;
END $$;

-- ============================================
-- TRIGGERS FOR updated_at
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_lobbies_updated_at ON lobbies;
CREATE TRIGGER update_lobbies_updated_at BEFORE UPDATE ON lobbies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- DISABLE ROW LEVEL SECURITY (for MVP/demo)
-- ============================================

ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE lobbies DISABLE ROW LEVEL SECURITY;
ALTER TABLE rounds DISABLE ROW LEVEL SECURITY;
ALTER TABLE options DISABLE ROW LEVEL SECURITY;
ALTER TABLE votes DISABLE ROW LEVEL SECURITY;

-- ============================================
-- VERIFICATION QUERIES (optional - run to check)
-- ============================================

-- Check all tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('users', 'lobbies', 'rounds', 'options', 'votes')
ORDER BY table_name;

-- Check critical fields exist
SELECT table_name, column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name IN ('users', 'lobbies', 'rounds', 'options', 'votes')
AND column_name IN ('is_ready', 'current_round', 'selected_option_id', 'image_url')
ORDER BY table_name, column_name;

