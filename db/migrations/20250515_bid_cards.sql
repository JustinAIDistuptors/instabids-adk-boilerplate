-- Add additional fields to bid_cards table
-- Migration: 20250515_bid_cards

-- Add additional fields to the bid_cards table for more detailed project information
ALTER TABLE instabids.bid_cards
    ADD COLUMN IF NOT EXISTS materials_preferences JSONB DEFAULT '{}'::JSONB,
    ADD COLUMN IF NOT EXISTS special_requirements TEXT,
    ADD COLUMN IF NOT EXISTS accessibility_needs JSONB DEFAULT '{}'::JSONB,
    ADD COLUMN IF NOT EXISTS scheduling_constraints JSONB DEFAULT '{}'::JSONB,
    ADD COLUMN IF NOT EXISTS ai_generated_notes TEXT,
    ADD COLUMN IF NOT EXISTS image_analysis_results JSONB DEFAULT '{}'::JSONB;

-- Create table for bid card revisions to track history
CREATE TABLE IF NOT EXISTS instabids.bid_card_revisions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    bid_card_id UUID NOT NULL REFERENCES instabids.bid_cards(id),
    revision_number INTEGER NOT NULL,
    revision_data JSONB NOT NULL,
    revised_by UUID REFERENCES instabids.profiles(id),
    revision_type VARCHAR(50) NOT NULL DEFAULT 'update',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Add index on bid_card_id and revision_number
CREATE INDEX IF NOT EXISTS bid_card_revisions_bid_card_id_idx ON instabids.bid_card_revisions(bid_card_id);
CREATE UNIQUE INDEX IF NOT EXISTS bid_card_revisions_unique_idx ON instabids.bid_card_revisions(bid_card_id, revision_number);

-- Create function to automatically create revision records
CREATE OR REPLACE FUNCTION track_bid_card_revisions()
RETURNS TRIGGER AS $$
DECLARE
    revision_count INTEGER;
    revision_data JSONB;
BEGIN
    -- Get the current revision count for this bid card
    SELECT COUNT(*) INTO revision_count
    FROM instabids.bid_card_revisions
    WHERE bid_card_id = NEW.id;
    
    -- Create JSON representation of the bid card data
    revision_data = jsonb_build_object(
        'project_name', NEW.project_name,
        'project_type', NEW.project_type,
        'project_scope', NEW.project_scope,
        'location', NEW.location,
        'timeline', NEW.timeline,
        'budget_range', NEW.budget_range,
        'status', NEW.status,
        'photo_urls', NEW.photo_urls,
        'materials_preferences', NEW.materials_preferences,
        'special_requirements', NEW.special_requirements,
        'accessibility_needs', NEW.accessibility_needs,
        'scheduling_constraints', NEW.scheduling_constraints,
        'ai_generated_notes', NEW.ai_generated_notes,
        'image_analysis_results', NEW.image_analysis_results
    );
    
    -- Insert a new revision record
    INSERT INTO instabids.bid_card_revisions
        (bid_card_id, revision_number, revision_data, revised_by, revision_type)
    VALUES
        (NEW.id, revision_count + 1, revision_data, auth.uid(), 
         CASE 
            WHEN TG_OP = 'INSERT' THEN 'create'
            WHEN TG_OP = 'UPDATE' THEN 'update'
            ELSE 'unknown'
         END);
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create or replace the trigger
DROP TRIGGER IF EXISTS track_bid_card_changes ON instabids.bid_cards;
CREATE TRIGGER track_bid_card_changes
AFTER INSERT OR UPDATE ON instabids.bid_cards
FOR EACH ROW
EXECUTE FUNCTION track_bid_card_revisions();

-- Update the search vector to include new fields
DROP TRIGGER IF EXISTS bid_cards_search_vector_update ON instabids.bid_cards;

CREATE OR REPLACE FUNCTION update_bid_cards_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector = to_tsvector('english', 
        coalesce(NEW.project_name, '') || ' ' || 
        coalesce(NEW.project_type, '') || ' ' || 
        coalesce(NEW.project_scope, '') || ' ' ||
        coalesce(NEW.special_requirements, '')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER bid_cards_search_vector_update
BEFORE INSERT OR UPDATE ON instabids.bid_cards
FOR EACH ROW
EXECUTE FUNCTION update_bid_cards_search_vector();

-- Add security policies for the new table
ALTER TABLE instabids.bid_card_revisions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Homeowners can view revisions for their own bid cards"
    ON instabids.bid_card_revisions FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM instabids.bid_cards
        WHERE bid_cards.id = bid_card_revisions.bid_card_id
        AND bid_cards.homeowner_id = auth.uid()
    ));

CREATE POLICY "System can insert revisions"
    ON instabids.bid_card_revisions FOR INSERT
    WITH CHECK (revised_by = auth.uid());
