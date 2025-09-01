-- NFL Fantasy League Database Schema
-- PostgreSQL setup script based on SQLAlchemy models

-- Create database (run this separately if needed)
-- CREATE DATABASE nfl_fantasy;

-- Connect to the database and create tables

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- NFL Players table
CREATE TABLE IF NOT EXISTS nfl_players (
    id SERIAL PRIMARY KEY,
    nfl_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    position VARCHAR(10) NOT NULL,
    team VARCHAR(10) NOT NULL,
    price FLOAT NOT NULL DEFAULT 5000000,
    total_points FLOAT DEFAULT 0.0,
    is_injured BOOLEAN DEFAULT FALSE,
    injury_status VARCHAR(50)
);

-- Fantasy Teams table
CREATE TABLE IF NOT EXISTS fantasy_teams (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    budget_remaining FLOAT DEFAULT 100000000,
    total_points FLOAT DEFAULT 0.0,
    free_transfers INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Team Players junction table
CREATE TABLE IF NOT EXISTS team_players (
    id SERIAL PRIMARY KEY,
    team_id INTEGER REFERENCES fantasy_teams(id) ON DELETE CASCADE,
    player_id INTEGER REFERENCES nfl_players(id) ON DELETE CASCADE,
    acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    purchase_price FLOAT NOT NULL,
    UNIQUE(team_id, player_id)
);

-- Weekly Lineups table
CREATE TABLE IF NOT EXISTS weekly_lineups (
    id SERIAL PRIMARY KEY,
    team_id INTEGER REFERENCES fantasy_teams(id) ON DELETE CASCADE,
    week INTEGER NOT NULL,
    season INTEGER NOT NULL,
    qb_id INTEGER REFERENCES nfl_players(id),
    rb1_id INTEGER REFERENCES nfl_players(id),
    rb2_id INTEGER REFERENCES nfl_players(id),
    wr1_id INTEGER REFERENCES nfl_players(id),
    wr2_id INTEGER REFERENCES nfl_players(id),
    te_id INTEGER REFERENCES nfl_players(id),
    k_id INTEGER REFERENCES nfl_players(id),
    def_id INTEGER REFERENCES nfl_players(id),
    total_points FLOAT DEFAULT 0.0,
    is_finalized BOOLEAN DEFAULT FALSE,
    UNIQUE(team_id, week, season)
);

-- Weekly Scores table (player performance data)
CREATE TABLE IF NOT EXISTS weekly_scores (
    id SERIAL PRIMARY KEY,
    player_id INTEGER REFERENCES nfl_players(id) ON DELETE CASCADE,
    week INTEGER NOT NULL,
    season INTEGER NOT NULL,
    -- NFL Statistics
    passing_yards FLOAT DEFAULT 0.0,
    passing_tds INTEGER DEFAULT 0,
    passing_interceptions INTEGER DEFAULT 0,
    rushing_yards FLOAT DEFAULT 0.0,
    rushing_tds INTEGER DEFAULT 0,
    receiving_yards FLOAT DEFAULT 0.0,
    receiving_tds INTEGER DEFAULT 0,
    receptions INTEGER DEFAULT 0,
    fumbles INTEGER DEFAULT 0,
    -- Kicker stats
    field_goals_made INTEGER DEFAULT 0,
    field_goals_attempted INTEGER DEFAULT 0,
    extra_points_made INTEGER DEFAULT 0,
    -- Defense stats
    def_touchdowns INTEGER DEFAULT 0,
    def_interceptions INTEGER DEFAULT 0,
    def_fumble_recoveries INTEGER DEFAULT 0,
    def_safeties INTEGER DEFAULT 0,
    def_points_allowed INTEGER DEFAULT 0,
    -- Fantasy points
    fantasy_points FLOAT DEFAULT 0.0,
    UNIQUE(player_id, week, season)
);

-- Transfers table
CREATE TABLE IF NOT EXISTS transfers (
    id SERIAL PRIMARY KEY,
    team_id INTEGER REFERENCES fantasy_teams(id) ON DELETE CASCADE,
    week INTEGER NOT NULL,
    season INTEGER NOT NULL,
    player_in_id INTEGER REFERENCES nfl_players(id) ON DELETE CASCADE,
    player_out_id INTEGER REFERENCES nfl_players(id) ON DELETE CASCADE,
    cost FLOAT DEFAULT 0.0,
    point_hit INTEGER DEFAULT 0,
    transfer_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_nfl_players_position ON nfl_players(position);
CREATE INDEX IF NOT EXISTS idx_nfl_players_team ON nfl_players(team);
CREATE INDEX IF NOT EXISTS idx_nfl_players_price ON nfl_players(price);
CREATE INDEX IF NOT EXISTS idx_weekly_scores_week_season ON weekly_scores(week, season);
CREATE INDEX IF NOT EXISTS idx_weekly_lineups_week_season ON weekly_lineups(week, season);
CREATE INDEX IF NOT EXISTS idx_team_players_team_id ON team_players(team_id);
CREATE INDEX IF NOT EXISTS idx_transfers_week_season ON transfers(week, season);

-- Insert some sample data for testing
INSERT INTO users (username, email) VALUES 
    ('admin', 'admin@nflfantasy.com'),
    ('test_user', 'test@example.com')
ON CONFLICT (username) DO NOTHING;

-- Sample NFL players (you'll replace this with real API data)
INSERT INTO nfl_players (nfl_id, name, position, team, price, total_points) VALUES 
    ('mahomes15', 'Patrick Mahomes', 'QB', 'KC', 12000000, 285.5),
    ('allen17', 'Josh Allen', 'QB', 'BUF', 11500000, 278.2),
    ('henry22', 'Derrick Henry', 'RB', 'BAL', 9000000, 198.7),
    ('mccaffrey22', 'Christian McCaffrey', 'RB', 'SF', 11000000, 245.1),
    ('jefferson18', 'Justin Jefferson', 'WR', 'MIN', 10500000, 225.8),
    ('kupp10', 'Cooper Kupp', 'WR', 'LAR', 9500000, 201.3),
    ('kelce87', 'Travis Kelce', 'TE', 'KC', 8000000, 189.4),
    ('tucker9', 'Justin Tucker', 'K', 'BAL', 5000000, 145.2),
    ('steelers_def', 'Pittsburgh Steelers', 'DEF', 'PIT', 5500000, 167.9),
    ('bills_def', 'Buffalo Bills', 'DEF', 'BUF', 6000000, 178.3)
ON CONFLICT (nfl_id) DO NOTHING;

-- Create a view for team summaries
CREATE OR REPLACE VIEW team_summary AS
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

-- Create a view for weekly leaderboards
CREATE OR REPLACE VIEW weekly_leaderboard AS
SELECT 
    wl.week,
    wl.season,
    ft.name as team_name,
    u.username as owner,
    wl.total_points,
    RANK() OVER (PARTITION BY wl.week, wl.season ORDER BY wl.total_points DESC) as rank
FROM weekly_lineups wl
JOIN fantasy_teams ft ON wl.team_id = ft.id
JOIN users u ON ft.user_id = u.id
WHERE wl.is_finalized = TRUE;

COMMENT ON TABLE users IS 'User accounts for fantasy league participants';
COMMENT ON TABLE nfl_players IS 'NFL player data with fantasy pricing and stats';
COMMENT ON TABLE fantasy_teams IS 'User-owned fantasy teams with budget management';
COMMENT ON TABLE team_players IS 'Junction table for team rosters';
COMMENT ON TABLE weekly_lineups IS 'Starting lineups for each gameweek';
COMMENT ON TABLE weekly_scores IS 'Individual player performance and fantasy points';
COMMENT ON TABLE transfers IS 'Player transfer history with costs and penalties';

-- Display setup completion message
DO $$
BEGIN
    RAISE NOTICE '✅ NFL Fantasy League database schema created successfully!';
    RAISE NOTICE '📊 Sample data inserted for testing';
    RAISE NOTICE '🔍 Views created for team summaries and leaderboards';
    RAISE NOTICE '⚡ Indexes created for optimal performance';
END $$;
