-- Migration script to create modular team tables with Row-Level Security
-- Run this script to upgrade existing database to support separate offense, defense, and special teams

-- Create NFL Teams table for bulk team selection
CREATE TABLE IF NOT EXISTS nfl_teams (
    id SERIAL PRIMARY KEY,
    team_code VARCHAR(10) UNIQUE NOT NULL,
    team_name VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    nickname VARCHAR(50) NOT NULL
);

-- Create Offense Lineups table
CREATE TABLE IF NOT EXISTS offense_lineups (
    id SERIAL PRIMARY KEY,
    team_id INTEGER REFERENCES fantasy_teams(id) ON DELETE CASCADE,
    week INTEGER NOT NULL,
    season INTEGER NOT NULL,
    
    -- Offensive positions
    qb_id INTEGER REFERENCES nfl_players(id),
    rb1_id INTEGER REFERENCES nfl_players(id),
    rb2_id INTEGER REFERENCES nfl_players(id),
    wr1_id INTEGER REFERENCES nfl_players(id),
    wr2_id INTEGER REFERENCES nfl_players(id),
    te_id INTEGER REFERENCES nfl_players(id),
    
    -- Points tracking
    offense_points FLOAT DEFAULT 0.0,
    is_finalized BOOLEAN DEFAULT FALSE,
    
    UNIQUE(team_id, week, season)
);

-- Create Defense Lineups table
CREATE TABLE IF NOT EXISTS defense_lineups (
    id SERIAL PRIMARY KEY,
    team_id INTEGER REFERENCES fantasy_teams(id) ON DELETE CASCADE,
    week INTEGER NOT NULL,
    season INTEGER NOT NULL,
    
    -- Defense can be either individual players or entire team
    selection_type VARCHAR(20) NOT NULL, -- 'individual' or 'team'
    
    -- For individual player selection
    dl1_id INTEGER REFERENCES nfl_players(id), -- Defensive Line
    dl2_id INTEGER REFERENCES nfl_players(id),
    lb1_id INTEGER REFERENCES nfl_players(id), -- Linebacker
    lb2_id INTEGER REFERENCES nfl_players(id),
    cb1_id INTEGER REFERENCES nfl_players(id), -- Cornerback
    cb2_id INTEGER REFERENCES nfl_players(id),
    s1_id INTEGER REFERENCES nfl_players(id),  -- Safety
    s2_id INTEGER REFERENCES nfl_players(id),
    
    -- For team selection
    nfl_team_id INTEGER REFERENCES nfl_teams(id),
    
    -- Points tracking
    defense_points FLOAT DEFAULT 0.0,
    is_finalized BOOLEAN DEFAULT FALSE,
    
    UNIQUE(team_id, week, season)
);

-- Create Special Teams Lineups table
CREATE TABLE IF NOT EXISTS special_teams_lineups (
    id SERIAL PRIMARY KEY,
    team_id INTEGER REFERENCES fantasy_teams(id) ON DELETE CASCADE,
    week INTEGER NOT NULL,
    season INTEGER NOT NULL,
    
    -- Special teams can be either individual players or entire team
    selection_type VARCHAR(20) NOT NULL, -- 'individual' or 'team'
    
    -- For individual player selection
    kicker_id INTEGER REFERENCES nfl_players(id),
    punter_id INTEGER REFERENCES nfl_players(id),
    
    -- For team selection
    nfl_team_id INTEGER REFERENCES nfl_teams(id),
    
    -- Points tracking
    special_teams_points FLOAT DEFAULT 0.0,
    is_finalized BOOLEAN DEFAULT FALSE,
    
    UNIQUE(team_id, week, season)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_offense_lineups_team_week ON offense_lineups(team_id, week, season);
CREATE INDEX IF NOT EXISTS idx_defense_lineups_team_week ON defense_lineups(team_id, week, season);
CREATE INDEX IF NOT EXISTS idx_special_teams_lineups_team_week ON special_teams_lineups(team_id, week, season);
CREATE INDEX IF NOT EXISTS idx_nfl_teams_code ON nfl_teams(team_code);

-- Insert NFL Teams data
INSERT INTO nfl_teams (team_code, team_name, city, nickname) VALUES 
    ('ARI', 'Arizona Cardinals', 'Arizona', 'Cardinals'),
    ('ATL', 'Atlanta Falcons', 'Atlanta', 'Falcons'),
    ('BAL', 'Baltimore Ravens', 'Baltimore', 'Ravens'),
    ('BUF', 'Buffalo Bills', 'Buffalo', 'Bills'),
    ('CAR', 'Carolina Panthers', 'Carolina', 'Panthers'),
    ('CHI', 'Chicago Bears', 'Chicago', 'Bears'),
    ('CIN', 'Cincinnati Bengals', 'Cincinnati', 'Bengals'),
    ('CLE', 'Cleveland Browns', 'Cleveland', 'Browns'),
    ('DAL', 'Dallas Cowboys', 'Dallas', 'Cowboys'),
    ('DEN', 'Denver Broncos', 'Denver', 'Broncos'),
    ('DET', 'Detroit Lions', 'Detroit', 'Lions'),
    ('GB', 'Green Bay Packers', 'Green Bay', 'Packers'),
    ('HOU', 'Houston Texans', 'Houston', 'Texans'),
    ('IND', 'Indianapolis Colts', 'Indianapolis', 'Colts'),
    ('JAX', 'Jacksonville Jaguars', 'Jacksonville', 'Jaguars'),
    ('KC', 'Kansas City Chiefs', 'Kansas City', 'Chiefs'),
    ('LV', 'Las Vegas Raiders', 'Las Vegas', 'Raiders'),
    ('LAC', 'Los Angeles Chargers', 'Los Angeles', 'Chargers'),
    ('LAR', 'Los Angeles Rams', 'Los Angeles', 'Rams'),
    ('MIA', 'Miami Dolphins', 'Miami', 'Dolphins'),
    ('MIN', 'Minnesota Vikings', 'Minnesota', 'Vikings'),
    ('NE', 'New England Patriots', 'New England', 'Patriots'),
    ('NO', 'New Orleans Saints', 'New Orleans', 'Saints'),
    ('NYG', 'New York Giants', 'New York', 'Giants'),
    ('NYJ', 'New York Jets', 'New York', 'Jets'),
    ('PHI', 'Philadelphia Eagles', 'Philadelphia', 'Eagles'),
    ('PIT', 'Pittsburgh Steelers', 'Pittsburgh', 'Steelers'),
    ('SF', 'San Francisco 49ers', 'San Francisco', '49ers'),
    ('SEA', 'Seattle Seahawks', 'Seattle', 'Seahawks'),
    ('TB', 'Tampa Bay Buccaneers', 'Tampa Bay', 'Buccaneers'),
    ('TEN', 'Tennessee Titans', 'Tennessee', 'Titans'),
    ('WAS', 'Washington Commanders', 'Washington', 'Commanders')
ON CONFLICT (team_code) DO NOTHING;

-- Enable Row-Level Security on all lineup tables
ALTER TABLE offense_lineups ENABLE ROW LEVEL SECURITY;
ALTER TABLE defense_lineups ENABLE ROW LEVEL SECURITY;
ALTER TABLE special_teams_lineups ENABLE ROW LEVEL SECURITY;

-- Create function to get current user ID (placeholder - implement based on your auth system)
CREATE OR REPLACE FUNCTION current_user_id()
RETURNS INTEGER AS $$
BEGIN
    -- This is a placeholder function. In a real implementation, you would:
    -- 1. Get the current user from your authentication system
    -- 2. Return their user ID
    -- For now, we'll return 1 as a default (admin user)
    RETURN 1;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create RLS policies for offense_lineups
CREATE POLICY user_offense_policy ON offense_lineups
    FOR ALL
    USING (
        team_id IN (
            SELECT id FROM fantasy_teams WHERE user_id = current_user_id()
        )
    );

-- Create RLS policies for defense_lineups
CREATE POLICY user_defense_policy ON defense_lineups
    FOR ALL
    USING (
        team_id IN (
            SELECT id FROM fantasy_teams WHERE user_id = current_user_id()
        )
    );

-- Create RLS policies for special_teams_lineups
CREATE POLICY user_special_teams_policy ON special_teams_lineups
    FOR ALL
    USING (
        team_id IN (
            SELECT id FROM fantasy_teams WHERE user_id = current_user_id()
        )
    );

-- Create helper functions for modular team management

-- Function to calculate offense points
CREATE OR REPLACE FUNCTION calculate_offense_points(p_team_id INTEGER, p_week INTEGER, p_season INTEGER)
RETURNS FLOAT AS $$
DECLARE
    total_points FLOAT := 0.0;
    player_points FLOAT;
BEGIN
    -- Calculate points for QB
    SELECT COALESCE(ws.fantasy_points, 0) INTO player_points
    FROM offense_lineups ol
    LEFT JOIN weekly_scores ws ON ol.qb_id = ws.player_id AND ws.week = p_week AND ws.season = p_season
    WHERE ol.team_id = p_team_id AND ol.week = p_week AND ol.season = p_season;
    total_points := total_points + COALESCE(player_points, 0);
    
    -- Calculate points for RB1
    SELECT COALESCE(ws.fantasy_points, 0) INTO player_points
    FROM offense_lineups ol
    LEFT JOIN weekly_scores ws ON ol.rb1_id = ws.player_id AND ws.week = p_week AND ws.season = p_season
    WHERE ol.team_id = p_team_id AND ol.week = p_week AND ol.season = p_season;
    total_points := total_points + COALESCE(player_points, 0);
    
    -- Calculate points for RB2
    SELECT COALESCE(ws.fantasy_points, 0) INTO player_points
    FROM offense_lineups ol
    LEFT JOIN weekly_scores ws ON ol.rb2_id = ws.player_id AND ws.week = p_week AND ws.season = p_season
    WHERE ol.team_id = p_team_id AND ol.week = p_week AND ol.season = p_season;
    total_points := total_points + COALESCE(player_points, 0);
    
    -- Calculate points for WR1
    SELECT COALESCE(ws.fantasy_points, 0) INTO player_points
    FROM offense_lineups ol
    LEFT JOIN weekly_scores ws ON ol.wr1_id = ws.player_id AND ws.week = p_week AND ws.season = p_season
    WHERE ol.team_id = p_team_id AND ol.week = p_week AND ol.season = p_season;
    total_points := total_points + COALESCE(player_points, 0);
    
    -- Calculate points for WR2
    SELECT COALESCE(ws.fantasy_points, 0) INTO player_points
    FROM offense_lineups ol
    LEFT JOIN weekly_scores ws ON ol.wr2_id = ws.player_id AND ws.week = p_week AND ws.season = p_season
    WHERE ol.team_id = p_team_id AND ol.week = p_week AND ol.season = p_season;
    total_points := total_points + COALESCE(player_points, 0);
    
    -- Calculate points for TE
    SELECT COALESCE(ws.fantasy_points, 0) INTO player_points
    FROM offense_lineups ol
    LEFT JOIN weekly_scores ws ON ol.te_id = ws.player_id AND ws.week = p_week AND ws.season = p_season
    WHERE ol.team_id = p_team_id AND ol.week = p_week AND ol.season = p_season;
    total_points := total_points + COALESCE(player_points, 0);
    
    RETURN total_points;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate defense points (simplified - would need more complex logic for team defense)
CREATE OR REPLACE FUNCTION calculate_defense_points(p_team_id INTEGER, p_week INTEGER, p_season INTEGER)
RETURNS FLOAT AS $$
DECLARE
    total_points FLOAT := 0.0;
    player_points FLOAT;
BEGIN
    -- For now, we'll calculate individual defensive player points
    -- In a real implementation, you'd also handle team defense scoring
    
    -- Calculate points for all defensive positions
    SELECT COALESCE(SUM(ws.fantasy_points), 0) INTO total_points
    FROM defense_lineups dl
    LEFT JOIN weekly_scores ws ON (
        ws.player_id IN (dl.dl1_id, dl.dl2_id, dl.lb1_id, dl.lb2_id, dl.cb1_id, dl.cb2_id, dl.s1_id, dl.s2_id)
        AND ws.week = p_week 
        AND ws.season = p_season
    )
    WHERE dl.team_id = p_team_id AND dl.week = p_week AND dl.season = p_season;
    
    RETURN total_points;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate special teams points
CREATE OR REPLACE FUNCTION calculate_special_teams_points(p_team_id INTEGER, p_week INTEGER, p_season INTEGER)
RETURNS FLOAT AS $$
DECLARE
    total_points FLOAT := 0.0;
    player_points FLOAT;
BEGIN
    -- Calculate points for kicker
    SELECT COALESCE(ws.fantasy_points, 0) INTO player_points
    FROM special_teams_lineups stl
    LEFT JOIN weekly_scores ws ON stl.kicker_id = ws.player_id AND ws.week = p_week AND ws.season = p_season
    WHERE stl.team_id = p_team_id AND stl.week = p_week AND stl.season = p_season;
    total_points := total_points + COALESCE(player_points, 0);
    
    -- Calculate points for punter
    SELECT COALESCE(ws.fantasy_points, 0) INTO player_points
    FROM special_teams_lineups stl
    LEFT JOIN weekly_scores ws ON stl.punter_id = ws.player_id AND ws.week = p_week AND ws.season = p_season
    WHERE stl.team_id = p_team_id AND stl.week = p_week AND stl.season = p_season;
    total_points := total_points + COALESCE(player_points, 0);
    
    RETURN total_points;
END;
$$ LANGUAGE plpgsql;

-- Create view for modular team summaries
CREATE OR REPLACE VIEW modular_team_summary AS
SELECT 
    ft.id as team_id,
    ft.name as team_name,
    u.username as owner,
    ft.budget_remaining,
    ft.total_points,
    ft.free_transfers,
    COUNT(tp.player_id) as player_count,
    COALESCE(SUM(np.price), 0) as squad_value
FROM fantasy_teams ft
JOIN users u ON ft.user_id = u.id
LEFT JOIN team_players tp ON ft.id = tp.team_id
LEFT JOIN nfl_players np ON tp.player_id = np.id
GROUP BY ft.id, ft.name, u.username, ft.budget_remaining, ft.total_points, ft.free_transfers;

-- Create view for weekly modular leaderboards
CREATE OR REPLACE VIEW weekly_modular_leaderboard AS
SELECT 
    ol.week,
    ol.season,
    ft.name as team_name,
    u.username as owner,
    COALESCE(ol.offense_points, 0) as offense_points,
    COALESCE(dl.defense_points, 0) as defense_points,
    COALESCE(stl.special_teams_points, 0) as special_teams_points,
    COALESCE(ol.offense_points, 0) + COALESCE(dl.defense_points, 0) + COALESCE(stl.special_teams_points, 0) as total_points,
    RANK() OVER (PARTITION BY ol.week, ol.season ORDER BY 
        COALESCE(ol.offense_points, 0) + COALESCE(dl.defense_points, 0) + COALESCE(stl.special_teams_points, 0) DESC
    ) as rank
FROM offense_lineups ol
JOIN fantasy_teams ft ON ol.team_id = ft.id
JOIN users u ON ft.user_id = u.id
LEFT JOIN defense_lineups dl ON ol.team_id = dl.team_id AND ol.week = dl.week AND ol.season = dl.season
LEFT JOIN special_teams_lineups stl ON ol.team_id = stl.team_id AND ol.week = stl.week AND ol.season = stl.season
WHERE ol.is_finalized = TRUE;

-- Add comments for documentation
COMMENT ON TABLE nfl_teams IS 'NFL team information for bulk team selection';
COMMENT ON TABLE offense_lineups IS 'Offensive player lineups with individual point tracking';
COMMENT ON TABLE defense_lineups IS 'Defensive lineups supporting both individual players and team selection';
COMMENT ON TABLE special_teams_lineups IS 'Special teams lineups supporting both individual players and team selection';

COMMENT ON FUNCTION current_user_id() IS 'Returns current authenticated user ID (implement based on auth system)';
COMMENT ON FUNCTION calculate_offense_points(INTEGER, INTEGER, INTEGER) IS 'Calculates total offense points for a team in a specific week';
COMMENT ON FUNCTION calculate_defense_points(INTEGER, INTEGER, INTEGER) IS 'Calculates total defense points for a team in a specific week';
COMMENT ON FUNCTION calculate_special_teams_points(INTEGER, INTEGER, INTEGER) IS 'Calculates total special teams points for a team in a specific week';

-- Display completion message
DO $$
BEGIN
    RAISE NOTICE '✅ Modular team tables created successfully!';
    RAISE NOTICE '🔒 Row-Level Security enabled on all lineup tables';
    RAISE NOTICE '📊 NFL teams data inserted';
    RAISE NOTICE '⚡ Indexes and helper functions created';
    RAISE NOTICE '🔍 Views created for modular team summaries and leaderboards';
    RAISE NOTICE '⚠️  Remember to implement current_user_id() function based on your authentication system';
END $$;
