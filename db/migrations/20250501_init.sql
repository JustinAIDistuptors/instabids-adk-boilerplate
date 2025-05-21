-- Initialize database schema for InstaBids
-- Migration: 20250501_init

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create custom types
CREATE TYPE project_status AS ENUM ('draft', 'published', 'in_progress', 'completed', 'cancelled');
CREATE TYPE contractor_response AS ENUM ('interested', 'not_interested', 'needs_more_info');

-- Create schema
CREATE SCHEMA IF NOT EXISTS instabids;

-- Users table (extends Supabase auth.users)
CREATE TABLE instabids.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id),
    user_type VARCHAR(20) NOT NULL CHECK (user_type IN ('homeowner', 'contractor', 'admin')),
    display_name VARCHAR(100),
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Homeowners table
CREATE TABLE instabids.homeowners (
    id UUID PRIMARY KEY REFERENCES instabids.profiles(id),
    address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    zip VARCHAR(20),
    preferences JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Contractors table
CREATE TABLE instabids.contractors (
    id UUID PRIMARY KEY REFERENCES instabids.profiles(id),
    business_name VARCHAR(255),
    business_address VARCHAR(255),
    business_city VARCHAR(100),
    business_state VARCHAR(50),
    business_zip VARCHAR(20),
    services JSONB NOT NULL DEFAULT '{}'::JSONB,
    service_areas JSONB NOT NULL DEFAULT '{}'::JSONB,
    rating DECIMAL(3,2),
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Bid Cards table
CREATE TABLE instabids.bid_cards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    homeowner_id UUID NOT NULL REFERENCES instabids.homeowners(id),
    project_name VARCHAR(255) NOT NULL,
    project_type VARCHAR(100) NOT NULL,
    project_scope TEXT NOT NULL,
    location JSONB NOT NULL,
    timeline JSONB,
    budget_range JSONB,
    status project_status DEFAULT 'draft',
    photo_urls TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Add generated column for full-text search
ALTER TABLE instabids.bid_cards ADD COLUMN search_vector tsvector 
GENERATED ALWAYS AS (
    to_tsvector('english', 
        coalesce(project_name, '') || ' ' || 
        coalesce(project_type, '') || ' ' || 
        coalesce(project_scope, '')
    )
) STORED;

-- Create index for search
CREATE INDEX bid_cards_search_idx ON instabids.bid_cards USING GIN (search_vector);

-- Invitations table
CREATE TABLE instabids.invitations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    bid_card_id UUID NOT NULL REFERENCES instabids.bid_cards(id),
    contractor_id UUID NOT NULL REFERENCES instabids.contractors(id),
    invitation_method VARCHAR(20) NOT NULL,
    invitation_sent_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    response contractor_response,
    response_received_at TIMESTAMP WITH TIME ZONE,
    response_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    UNIQUE(bid_card_id, contractor_id)
);

-- Matches table
CREATE TABLE instabids.matches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    bid_card_id UUID NOT NULL REFERENCES instabids.bid_cards(id),
    homeowner_id UUID NOT NULL REFERENCES instabids.homeowners(id),
    contractor_id UUID NOT NULL REFERENCES instabids.contractors(id),
    match_timestamp TIMESTAMP WITH TIME ZONE DEFAULT now(),
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    UNIQUE(bid_card_id, contractor_id)
);

-- Conversations table
CREATE TABLE instabids.conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    match_id UUID NOT NULL REFERENCES instabids.matches(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Messages table
CREATE TABLE instabids.messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES instabids.conversations(id),
    sender_id UUID NOT NULL REFERENCES instabids.profiles(id),
    sender_type VARCHAR(20) NOT NULL CHECK (sender_type IN ('homeowner', 'contractor', 'system')),
    content TEXT NOT NULL,
    attachments JSONB,
    read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Trigger for updating timestamps
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add update triggers for all tables
CREATE TRIGGER update_profiles_modtime
BEFORE UPDATE ON instabids.profiles
FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_homeowners_modtime
BEFORE UPDATE ON instabids.homeowners
FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_contractors_modtime
BEFORE UPDATE ON instabids.contractors
FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_bid_cards_modtime
BEFORE UPDATE ON instabids.bid_cards
FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_invitations_modtime
BEFORE UPDATE ON instabids.invitations
FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_matches_modtime
BEFORE UPDATE ON instabids.matches
FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_conversations_modtime
BEFORE UPDATE ON instabids.conversations
FOR EACH ROW EXECUTE FUNCTION update_modified_column();

-- Security Policies (RLS)
ALTER TABLE instabids.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE instabids.homeowners ENABLE ROW LEVEL SECURITY;
ALTER TABLE instabids.contractors ENABLE ROW LEVEL SECURITY;
ALTER TABLE instabids.bid_cards ENABLE ROW LEVEL SECURITY;
ALTER TABLE instabids.invitations ENABLE ROW LEVEL SECURITY;
ALTER TABLE instabids.matches ENABLE ROW LEVEL SECURITY;
ALTER TABLE instabids.conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE instabids.messages ENABLE ROW LEVEL SECURITY;

-- Profile policies
CREATE POLICY "Users can view their own profile"
    ON instabids.profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile"
    ON instabids.profiles FOR UPDATE
    USING (auth.uid() = id);

-- Homeowner policies
CREATE POLICY "Homeowners can view their own data"
    ON instabids.homeowners FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Homeowners can update their own data"
    ON instabids.homeowners FOR UPDATE
    USING (auth.uid() = id);

-- Contractor policies
CREATE POLICY "Contractors can view their own data"
    ON instabids.contractors FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Contractors can update their own data"
    ON instabids.contractors FOR UPDATE
    USING (auth.uid() = id);

-- Bid cards policies
CREATE POLICY "Homeowners can view their own bid cards"
    ON instabids.bid_cards FOR SELECT
    USING (auth.uid() = homeowner_id);

CREATE POLICY "Homeowners can insert their own bid cards"
    ON instabids.bid_cards FOR INSERT
    WITH CHECK (auth.uid() = homeowner_id);

CREATE POLICY "Homeowners can update their own bid cards"
    ON instabids.bid_cards FOR UPDATE
    USING (auth.uid() = homeowner_id);

-- Add more policies as needed for other tables
