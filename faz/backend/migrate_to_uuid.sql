-- =====================================================
-- COMPLETE DATABASE MIGRATION TO UUID
-- Converts all integer IDs to UUID while preserving data
-- Populates all empty tables with sample data
-- =====================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- STEP 1: Backup existing integer IDs in temp tables
-- =====================================================

-- Create mapping tables for old integer IDs to new UUIDs
CREATE TEMP TABLE temp_team_id_map AS
SELECT id AS old_id, uuid_generate_v4() AS new_id 
FROM teams WHERE id IS NOT NULL;

CREATE TEMP TABLE temp_user_id_map AS
SELECT id AS old_id, uuid_generate_v4() AS new_id 
FROM users WHERE id IS NOT NULL;

CREATE TEMP TABLE temp_league_id_map AS
SELECT id AS old_id, uuid_generate_v4() AS new_id 
FROM leagues WHERE id IS NOT NULL;

CREATE TEMP TABLE temp_league_standing_id_map AS
SELECT id AS old_id, uuid_generate_v4() AS new_id 
FROM league_standings WHERE id IS NOT NULL;

CREATE TEMP TABLE temp_news_id_map AS
SELECT id AS old_id, uuid_generate_v4() AS new_id 
FROM news WHERE id IS NOT NULL;

CREATE TEMP TABLE temp_match_id_map AS
SELECT id AS old_id, uuid_generate_v4() AS new_id 
FROM matches WHERE id IS NOT NULL;

CREATE TEMP TABLE temp_player_id_map AS
SELECT id AS old_id, uuid_generate_v4() AS new_id 
FROM players WHERE id IS NOT NULL;

CREATE TEMP TABLE temp_cup_competition_id_map AS
SELECT id AS old_id, uuid_generate_v4() AS new_id 
FROM cup_competitions WHERE id IS NOT NULL;

CREATE TEMP TABLE temp_cup_season_id_map AS
SELECT id AS old_id, uuid_generate_v4() AS new_id 
FROM cup_seasons WHERE id IS NOT NULL;

CREATE TEMP TABLE temp_cup_match_id_map AS
SELECT id AS old_id, uuid_generate_v4() AS new_id 
FROM cup_matches WHERE id IS NOT NULL;

CREATE TEMP TABLE temp_national_team_id_map AS
SELECT id AS old_id, uuid_generate_v4() AS new_id 
FROM national_teams WHERE id IS NOT NULL;

CREATE TEMP TABLE temp_tournament_id_map AS
SELECT id AS old_id, uuid_generate_v4() AS new_id 
FROM tournaments WHERE id IS NOT NULL;

CREATE TEMP TABLE temp_tournament_participation_id_map AS
SELECT id AS old_id, uuid_generate_v4() AS new_id 
FROM tournament_participations WHERE id IS NOT NULL;

CREATE TEMP TABLE temp_promotion_relegation_rule_id_map AS
SELECT id AS old_id, uuid_generate_v4() AS new_id 
FROM promotion_relegation_rules WHERE id IS NOT NULL;

CREATE TEMP TABLE temp_tag_id_map AS
SELECT id AS old_id, uuid_generate_v4() AS new_id 
FROM tags WHERE id IS NOT NULL;

CREATE TEMP TABLE temp_bulk_import_log_id_map AS
SELECT id AS old_id, uuid_generate_v4() AS new_id 
FROM bulk_import_logs WHERE id IS NOT NULL;

CREATE TEMP TABLE temp_continental_qualification_id_map AS
SELECT id AS old_id, uuid_generate_v4() AS new_id 
FROM continental_qualifications WHERE id IS NOT NULL;

CREATE TEMP TABLE temp_match_event_id_map AS
SELECT id AS old_id, uuid_generate_v4() AS new_id 
FROM match_events WHERE id IS NOT NULL;

CREATE TEMP TABLE temp_match_report_id_map AS
SELECT id AS old_id, uuid_generate_v4() AS new_id 
FROM match_reports WHERE id IS NOT NULL;

CREATE TEMP TABLE temp_national_team_fixture_id_map AS
SELECT id AS old_id, uuid_generate_v4() AS new_id 
FROM national_team_fixtures WHERE id IS NOT NULL;

CREATE TEMP TABLE temp_season_id_map AS
SELECT id AS old_id, uuid_generate_v4() AS new_id 
FROM seasons WHERE id IS NOT NULL;

CREATE TEMP TABLE temp_promotion_relegation_id_map AS
SELECT id AS old_id, uuid_generate_v4() AS new_id 
FROM promotion_relegations WHERE id IS NOT NULL;

-- =====================================================
-- STEP 2: Create new UUID-based tables
-- =====================================================

-- Drop existing foreign key constraints (to be recreated later)
-- Teams table has no outgoing FKs to worry about first

-- Create new teams table
CREATE TABLE teams_new (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR UNIQUE NOT NULL,
    short_name VARCHAR,
    logo VARCHAR,
    founded INTEGER,
    stadium VARCHAR,
    coach VARCHAR,
    description TEXT,
    gender VARCHAR,
    team_type VARCHAR,
    current_league_level VARCHAR,
    league_tier INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create new users table
CREATE TABLE users_new (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR UNIQUE,
    username VARCHAR UNIQUE,
    hashed_password VARCHAR,
    full_name VARCHAR,
    role USERROLE,
    club_id UUID,
    is_active BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create new leagues table
CREATE TABLE leagues_new (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR UNIQUE,
    gender GENDER,
    level LEAGUELEVEL,
    tier INTEGER,
    season VARCHAR,
    current_champion_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create new league_standings table
CREATE TABLE league_standings_new (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    league_id UUID,
    team_id UUID,
    season VARCHAR,
    played INTEGER,
    won INTEGER,
    drawn INTEGER,
    lost INTEGER,
    goals_for INTEGER,
    goals_against INTEGER,
    points INTEGER
);

-- Create new news table
CREATE TABLE news_new (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR,
    slug VARCHAR UNIQUE,
    content TEXT,
    excerpt VARCHAR(300),
    featured_image VARCHAR,
    author_id UUID,
    views INTEGER,
    is_published BOOLEAN,
    published_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create new matches table
CREATE TABLE matches_new (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    home_team VARCHAR,
    away_team VARCHAR,
    home_score INTEGER,
    away_score INTEGER,
    match_date TIMESTAMP WITH TIME ZONE,
    venue VARCHAR,
    competition VARCHAR,
    status VARCHAR,
    is_home_match BOOLEAN,
    referee_id UUID
);

-- Create new players table
CREATE TABLE players_new (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR,
    position VARCHAR,
    jersey_number INTEGER,
    date_of_birth DATE,
    nationality VARCHAR,
    photo VARCHAR,
    team_id UUID,
    goals INTEGER,
    assists INTEGER,
    appearances INTEGER
);

-- Create new cup_competitions table
CREATE TABLE cup_competitions_new (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR,
    gender GENDER,
    competition_type VARCHAR,
    season VARCHAR,
    current_champion_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create new cup_seasons table
CREATE TABLE cup_seasons_new (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cup_competition_id UUID,
    season VARCHAR,
    winner_id UUID,
    runner_up_id UUID,
    started_at DATE,
    ended_at DATE
);

-- Create new cup_matches table
CREATE TABLE cup_matches_new (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cup_season_id UUID,
    round_name VARCHAR,
    home_team_id UUID,
    away_team_id UUID,
    home_score INTEGER,
    away_score INTEGER,
    match_date TIMESTAMP WITH TIME ZONE,
    venue VARCHAR,
    is_played BOOLEAN,
    winner_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create new national_teams table
CREATE TABLE national_teams_new (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    gender GENDER,
    age_group VARCHAR,
    name VARCHAR,
    coach VARCHAR,
    captain_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create new tournaments table
CREATE TABLE tournaments_new (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR UNIQUE,
    category TOURNAMENTCATEGORY,
    gender GENDER,
    age_group VARCHAR,
    has_qualifiers BOOLEAN,
    is_major_tournament BOOLEAN,
    continent VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create new tournament_participations table
CREATE TABLE tournament_participations_new (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    national_team_id UUID,
    tournament_name VARCHAR,
    year VARCHAR,
    round_reached VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create new promotion_relegation_rules table
CREATE TABLE promotion_relegation_rules_new (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    from_league_id UUID,
    to_league_id UUID,
    positions_promoted INTEGER,
    positions_relegated INTEGER,
    season VARCHAR
);

-- Create new promotion_relegations table
CREATE TABLE promotion_relegations_new (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    team_id UUID,
    from_league_id UUID,
    to_league_id UUID,
    season VARCHAR,
    action VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create new tags table
CREATE TABLE tags_new (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR UNIQUE,
    slug VARCHAR UNIQUE
);

-- Create new news_tags table (junction)
CREATE TABLE news_tags_new (
    news_id UUID,
    tag_id UUID
);

-- Create new bulk_import_logs table
CREATE TABLE bulk_import_logs_new (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name VARCHAR,
    file_name VARCHAR,
    rows_imported INTEGER,
    errors TEXT,
    imported_by UUID,
    imported_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create new continental_qualifications table
CREATE TABLE continental_qualifications_new (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    season VARCHAR,
    competition_name VARCHAR,
    gender GENDER,
    qualifying_team_id UUID,
    qualification_reason VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create new match_events table
CREATE TABLE match_events_new (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    match_id UUID,
    event_type MATCHEVENTTYPE,
    player_id UUID,
    related_player_id UUID,
    minute INTEGER,
    minute_added INTEGER,
    description VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create new match_reports table
CREATE TABLE match_reports_new (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    match_id UUID UNIQUE,
    referee_id UUID,
    content TEXT,
    yellow_cards JSON,
    red_cards JSON,
    incidents JSON,
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create new national_team_fixtures table
CREATE TABLE national_team_fixtures_new (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    national_team_id UUID,
    opponent VARCHAR,
    match_date TIMESTAMP WITH TIME ZONE,
    venue VARCHAR,
    competition VARCHAR,
    match_type MATCHTYPE,
    home_away VARCHAR,
    goals_for INTEGER,
    goals_against INTEGER,
    result VARCHAR,
    is_played BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create new seasons table
CREATE TABLE seasons_new (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR UNIQUE,
    start_date DATE,
    end_date DATE,
    is_current BOOLEAN
);

-- Create new league_tables (legacy) table
CREATE TABLE league_tables_new (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    team_id UUID,
    played INTEGER,
    won INTEGER,
    drawn INTEGER,
    lost INTEGER,
    goals_for INTEGER,
    goals_against INTEGER,
    points INTEGER,
    season VARCHAR
);

-- =====================================================
-- STEP 3: Migrate data to new tables (convert IDs to UUID)
-- =====================================================

-- Migrate teams
INSERT INTO teams_new (id, name, short_name, logo, founded, stadium, coach, description, gender, team_type, current_league_level, league_tier, created_at)
SELECT tm.new_id, t.name, t.short_name, t.logo, t.founded, t.stadium, t.coach, t.description, t.gender, t.team_type, t.current_league_level, t.league_tier, t.created_at
FROM teams t
JOIN temp_team_id_map tm ON tm.old_id = t.id;

-- Migrate users (club_id will be updated after teams migration)
INSERT INTO users_new (id, email, username, hashed_password, full_name, role, club_id, is_active, created_at)
SELECT um.new_id, u.email, u.username, u.hashed_password, u.full_name, u.role, 
       (SELECT new_id FROM temp_team_id_map WHERE old_id = u.club_id),
       u.is_active, u.created_at
FROM users u
JOIN temp_user_id_map um ON um.old_id = u.id;

-- Migrate leagues
INSERT INTO leagues_new (id, name, gender, level, tier, season, current_champion_id, created_at)
SELECT lm.new_id, l.name, l.gender, l.level, l.tier, l.season,
       (SELECT new_id FROM temp_team_id_map WHERE old_id = l.current_champion_id),
       l.created_at
FROM leagues l
JOIN temp_league_id_map lm ON lm.old_id = l.id;

-- Migrate league_standings
INSERT INTO league_standings_new (id, league_id, team_id, season, played, won, drawn, lost, goals_for, goals_against, points)
SELECT lsm.new_id,
       (SELECT new_id FROM temp_league_id_map WHERE old_id = ls.league_id),
       (SELECT new_id FROM temp_team_id_map WHERE old_id = ls.team_id),
       ls.season, ls.played, ls.won, ls.drawn, ls.lost, ls.goals_for, ls.goals_against, ls.points
FROM league_standings ls
JOIN temp_league_standing_id_map lsm ON lsm.old_id = ls.id;

-- Migrate news
INSERT INTO news_new (id, title, slug, content, excerpt, featured_image, author_id, views, is_published, published_at, created_at, updated_at)
SELECT nm.new_id, n.title, n.slug, n.content, n.excerpt, n.featured_image,
       (SELECT new_id FROM temp_user_id_map WHERE old_id = n.author_id),
       n.views, n.is_published, n.published_at, n.created_at, n.updated_at
FROM news n
JOIN temp_news_id_map nm ON nm.old_id = n.id;

-- Migrate matches
INSERT INTO matches_new (id, home_team, away_team, home_score, away_score, match_date, venue, competition, status, is_home_match, referee_id)
SELECT mm.new_id, m.home_team, m.away_team, m.home_score, m.away_score, m.match_date, m.venue, m.competition, m.status, m.is_home_match,
       (SELECT new_id FROM temp_user_id_map WHERE old_id = m.referee_id)
FROM matches m
JOIN temp_match_id_map mm ON mm.old_id = m.id;

-- Migrate players
INSERT INTO players_new (id, name, position, jersey_number, date_of_birth, nationality, photo, team_id, goals, assists, appearances)
SELECT pm.new_id, p.name, p.position, p.jersey_number, p.date_of_birth, p.nationality, p.photo,
       (SELECT new_id FROM temp_team_id_map WHERE old_id = p.team_id),
       p.goals, p.assists, p.appearances
FROM players p
JOIN temp_player_id_map pm ON pm.old_id = p.id;

-- Migrate cup_competitions
INSERT INTO cup_competitions_new (id, name, gender, competition_type, season, current_champion_id, created_at)
SELECT cm.new_id, c.name, c.gender, c.competition_type, c.season,
       (SELECT new_id FROM temp_team_id_map WHERE old_id = c.current_champion_id),
       c.created_at
FROM cup_competitions c
JOIN temp_cup_competition_id_map cm ON cm.old_id = c.id;

-- Migrate cup_seasons
INSERT INTO cup_seasons_new (id, cup_competition_id, season, winner_id, runner_up_id, started_at, ended_at)
SELECT csm.new_id,
       (SELECT new_id FROM temp_cup_competition_id_map WHERE old_id = cs.cup_competition_id),
       cs.season,
       (SELECT new_id FROM temp_team_id_map WHERE old_id = cs.winner_id),
       (SELECT new_id FROM temp_team_id_map WHERE old_id = cs.runner_up_id),
       cs.started_at, cs.ended_at
FROM cup_seasons cs
JOIN temp_cup_season_id_map csm ON csm.old_id = cs.id;

-- Migrate cup_matches
INSERT INTO cup_matches_new (id, cup_season_id, round_name, home_team_id, away_team_id, home_score, away_score, match_date, venue, is_played, winner_id, created_at)
SELECT cmm.new_id,
       (SELECT new_id FROM temp_cup_season_id_map WHERE old_id = cm.cup_season_id),
       cm.round_name,
       (SELECT new_id FROM temp_team_id_map WHERE old_id = cm.home_team_id),
       (SELECT new_id FROM temp_team_id_map WHERE old_id = cm.away_team_id),
       cm.home_score, cm.away_score, cm.match_date, cm.venue, cm.is_played,
       (SELECT new_id FROM temp_team_id_map WHERE old_id = cm.winner_id),
       cm.created_at
FROM cup_matches cm
JOIN temp_cup_match_id_map cmm ON cmm.old_id = cm.id;

-- Migrate national_teams
INSERT INTO national_teams_new (id, gender, age_group, name, coach, captain_id, created_at)
SELECT nm.new_id, nt.gender, nt.age_group, nt.name, nt.coach,
       (SELECT new_id FROM temp_player_id_map WHERE old_id = nt.captain_id),
       nt.created_at
FROM national_teams nt
JOIN temp_national_team_id_map nm ON nm.old_id = nt.id;

-- Migrate tournaments
INSERT INTO tournaments_new (id, name, category, gender, age_group, has_qualifiers, is_major_tournament, continent, created_at)
SELECT tm.new_id, t.name, t.category, t.gender, t.age_group, t.has_qualifiers, t.is_major_tournament, t.continent, t.created_at
FROM tournaments t
JOIN temp_tournament_id_map tm ON tm.old_id = t.id;

-- Migrate tournament_participations
INSERT INTO tournament_participations_new (id, national_team_id, tournament_name, year, round_reached, created_at)
SELECT tpm.new_id,
       (SELECT new_id FROM temp_national_team_id_map WHERE old_id = tp.national_team_id),
       tp.tournament_name, tp.year, tp.round_reached, tp.created_at
FROM tournament_participations tp
JOIN temp_tournament_participation_id_map tpm ON tpm.old_id = tp.id;

-- Migrate promotion_relegation_rules
INSERT INTO promotion_relegation_rules_new (id, from_league_id, to_league_id, positions_promoted, positions_relegated, season)
SELECT prm.new_id,
       (SELECT new_id FROM temp_league_id_map WHERE old_id = pr.from_league_id),
       (SELECT new_id FROM temp_league_id_map WHERE old_id = pr.to_league_id),
       pr.positions_promoted, pr.positions_relegated, pr.season
FROM promotion_relegation_rules pr
JOIN temp_promotion_relegation_rule_id_map prm ON prm.old_id = pr.id;

-- =====================================================
-- STEP 4: Populate empty tables with sample data
-- =====================================================

-- Populate seasons
INSERT INTO seasons_new (name, start_date, end_date, is_current) VALUES
('2025-2026', '2025-08-01', '2026-05-31', true),
('2024-2025', '2024-08-01', '2025-05-31', false),
('2023-2024', '2023-08-01', '2024-05-31', false);

-- Populate tags
INSERT INTO tags_new (name, slug) VALUES
('National Team', 'national-team'),
('Super League', 'super-league'),
('Women Football', 'women-football'),
('Transfer News', 'transfer-news'),
('Match Report', 'match-report'),
('Injury Update', 'injury-update'),
('AFCON', 'afcon'),
('World Cup Qualifiers', 'world-cup-qualifiers'),
('COSAFA', 'cosafa'),
('Youth Football', 'youth-football');

-- Populate news_tags (link existing news with tags)
INSERT INTO news_tags_new (news_id, tag_id)
SELECT 
    (SELECT new_id FROM temp_news_id_map WHERE old_id = n.id),
    (SELECT new_id FROM temp_tag_id_map WHERE old_id = t.id)
FROM (VALUES 
    (1, 8), (2, 3), (3, 2), (4, 1), (5, 1),
    (6, 3), (7, 2), (8, 10), (9, 2), (10, 3)
) AS mappings(news_old_id, tag_old_id)
JOIN news n ON n.id = news_old_id
JOIN tags t ON t.id = tag_old_id;

-- Populate match_events (sample events for existing matches)
INSERT INTO match_events_new (match_id, event_type, player_id, minute)
SELECT 
    (SELECT new_id FROM temp_match_id_map WHERE old_id = 11),
    'GOAL'::MATCHEVENTTYPE,
    (SELECT new_id FROM temp_player_id_map WHERE old_id = 1),
    23
UNION ALL
SELECT 
    (SELECT new_id FROM temp_match_id_map WHERE old_id = 11),
    'GOAL'::MATCHEVENTTYPE,
    (SELECT new_id FROM temp_player_id_map WHERE old_id = 1),
    56
UNION ALL
SELECT 
    (SELECT new_id FROM temp_match_id_map WHERE old_id = 11),
    'YELLOW_CARD'::MATCHEVENTTYPE,
    (SELECT new_id FROM temp_player_id_map WHERE old_id = 5),
    78;

-- Populate match_reports (sample reports for finished matches)
INSERT INTO match_reports_new (match_id, referee_id, content, yellow_cards, red_cards)
SELECT 
    (SELECT new_id FROM temp_match_id_map WHERE old_id = 11),
    (SELECT new_id FROM temp_user_id_map WHERE old_id = 1),
    'ZESCO United dominated possession and created numerous chances. Patson Daka scored a brace to secure the win.',
    '[{"player": "Frankie Musonda", "minute": 78}]',
    '[]'::JSON
UNION ALL
SELECT 
    (SELECT new_id FROM temp_match_id_map WHERE old_id = 12),
    (SELECT new_id FROM temp_user_id_map WHERE old_id = 1),
    'A closely contested match with both teams sharing possession. The draw was a fair result.',
    '[]'::JSON,
    '[]'::JSON;

-- Populate national_team_fixtures (sample fixtures for national teams)
INSERT INTO national_team_fixtures_new (national_team_id, opponent, match_date, venue, competition, match_type, home_away, is_played)
SELECT 
    (SELECT new_id FROM temp_national_team_id_map WHERE old_id = 1),
    'Morocco',
    '2026-06-10 15:00:00+02',
    'National Heroes Stadium, Lusaka',
    'World Cup Qualifiers',
    'QUALIFIER'::MATCHTYPE,
    'home',
    false
UNION ALL
SELECT 
    (SELECT new_id FROM temp_national_team_id_map WHERE old_id = 1),
    'Nigeria',
    '2026-06-15 15:00:00+02',
    'Moshood Abiola Stadium, Abuja',
    'World Cup Qualifiers',
    'QUALIFIER'::MATCHTYPE,
    'away',
    false
UNION ALL
SELECT 
    (SELECT new_id FROM temp_national_team_id_map WHERE old_id = 6),
    'South Africa',
    '2026-07-20 15:00:00+02',
    'National Heroes Stadium, Lusaka',
    'COSAFA Women''s Cup',
    'TOURNAMENT'::MATCHTYPE,
    'home',
    false;

-- Populate bulk_import_logs
INSERT INTO bulk_import_logs_new (table_name, file_name, rows_imported, errors, imported_by)
SELECT 
    'teams',
    'initial_teams_import.csv',
    81,
    NULL,
    (SELECT new_id FROM temp_user_id_map WHERE old_id = 1)
UNION ALL
SELECT 
    'players',
    'initial_players_import.csv',
    41,
    NULL,
    (SELECT new_id FROM temp_user_id_map WHERE old_id = 1)
UNION ALL
SELECT 
    'news',
    'initial_news_import.csv',
    30,
    NULL,
    (SELECT new_id FROM temp_user_id_map WHERE old_id = 1);

-- Populate continental_qualifications (based on league standings)
INSERT INTO continental_qualifications_new (season, competition_name, gender, qualifying_team_id, qualification_reason)
SELECT 
    '2025-2026',
    'CAF Champions League',
    'MALE'::GENDER,
    (SELECT new_id FROM temp_team_id_map WHERE old_id = 1),
    'Super League Winner'
UNION ALL
SELECT 
    '2025-2026',
    'CAF Confederation Cup',
    'MALE'::GENDER,
    (SELECT new_id FROM temp_team_id_map WHERE old_id = 2),
    'Super League Runner-up'
UNION ALL
SELECT 
    '2025-2026',
    'COSAFA Women''s Champions League',
    'FEMALE'::GENDER,
    (SELECT new_id FROM temp_team_id_map WHERE old_id = 36),
    'Women''s Super League Winner';

-- Populate promotion_relegations (historical record)
INSERT INTO promotion_relegations_new (team_id, from_league_id, to_league_id, season, action)
SELECT 
    (SELECT new_id FROM temp_team_id_map WHERE old_id = 15),
    (SELECT new_id FROM temp_league_id_map WHERE old_id = 1),
    (SELECT new_id FROM temp_league_id_map WHERE old_id = 2),
    '2024-2025',
    'relegated'
UNION ALL
SELECT 
    (SELECT new_id FROM temp_team_id_map WHERE old_id = 20),
    (SELECT new_id FROM temp_league_id_map WHERE old_id = 2),
    (SELECT new_id FROM temp_league_id_map WHERE old_id = 1),
    '2024-2025',
    'promoted';

-- =====================================================
-- STEP 5: Drop old tables and rename new ones
-- =====================================================

-- Drop old tables
DROP TABLE IF EXISTS news_tags CASCADE;
DROP TABLE IF EXISTS tags CASCADE;
DROP TABLE IF EXISTS match_reports CASCADE;
DROP TABLE IF EXISTS match_events CASCADE;
DROP TABLE IF EXISTS continental_qualifications CASCADE;
DROP TABLE IF EXISTS bulk_import_logs CASCADE;
DROP TABLE IF EXISTS national_team_fixtures CASCADE;
DROP TABLE IF EXISTS tournament_participations CASCADE;
DROP TABLE IF EXISTS tournaments CASCADE;
DROP TABLE IF EXISTS cup_matches CASCADE;
DROP TABLE IF EXISTS cup_seasons CASCADE;
DROP TABLE IF EXISTS cup_competitions CASCADE;
DROP TABLE IF EXISTS promotion_relegations CASCADE;
DROP TABLE IF EXISTS promotion_relegation_rules CASCADE;
DROP TABLE IF EXISTS league_standings CASCADE;
DROP TABLE IF EXISTS league_tables CASCADE;
DROP TABLE IF EXISTS matches CASCADE;
DROP TABLE IF EXISTS news CASCADE;
DROP TABLE IF EXISTS players CASCADE;
DROP TABLE IF EXISTS national_teams CASCADE;
DROP TABLE IF EXISTS seasons CASCADE;
DROP TABLE IF EXISTS leagues CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS teams CASCADE;

-- Rename new tables to original names
ALTER TABLE teams_new RENAME TO teams;
ALTER TABLE users_new RENAME TO users;
ALTER TABLE leagues_new RENAME TO leagues;
ALTER TABLE league_standings_new RENAME TO league_standings;
ALTER TABLE news_new RENAME TO news;
ALTER TABLE matches_new RENAME TO matches;
ALTER TABLE players_new RENAME TO players;
ALTER TABLE cup_competitions_new RENAME TO cup_competitions;
ALTER TABLE cup_seasons_new RENAME TO cup_seasons;
ALTER TABLE cup_matches_new RENAME TO cup_matches;
ALTER TABLE national_teams_new RENAME TO national_teams;
ALTER TABLE tournaments_new RENAME TO tournaments;
ALTER TABLE tournament_participations_new RENAME TO tournament_participations;
ALTER TABLE promotion_relegation_rules_new RENAME TO promotion_relegation_rules;
ALTER TABLE promotion_relegations_new RENAME TO promotion_relegations;
ALTER TABLE tags_new RENAME TO tags;
ALTER TABLE news_tags_new RENAME TO news_tags;
ALTER TABLE bulk_import_logs_new RENAME TO bulk_import_logs;
ALTER TABLE continental_qualifications_new RENAME TO continental_qualifications;
ALTER TABLE match_events_new RENAME TO match_events;
ALTER TABLE match_reports_new RENAME TO match_reports;
ALTER TABLE national_team_fixtures_new RENAME TO national_team_fixtures;
ALTER TABLE seasons_new RENAME TO seasons;
ALTER TABLE league_tables_new RENAME TO league_tables;

-- =====================================================
-- STEP 6: Recreate indexes and constraints
-- =====================================================

-- Teams indexes
CREATE UNIQUE INDEX ix_teams_name ON teams (name);
CREATE INDEX ix_teams_id ON teams (id);
CREATE INDEX ix_teams_gender ON teams (gender);

-- Users indexes
CREATE UNIQUE INDEX ix_users_email ON users (email);
CREATE UNIQUE INDEX ix_users_username ON users (username);
CREATE INDEX ix_users_id ON users (id);

-- Leagues indexes
CREATE UNIQUE INDEX ix_leagues_name ON leagues (name);
CREATE INDEX ix_leagues_id ON leagues (id);

-- League standings indexes
CREATE INDEX ix_league_standings_id ON league_standings (id);
CREATE INDEX ix_league_standings_league_id ON league_standings (league_id);
CREATE INDEX ix_league_standings_team_id ON league_standings (team_id);

-- News indexes
CREATE UNIQUE INDEX ix_news_slug ON news (slug);
CREATE INDEX ix_news_title ON news (title);
CREATE INDEX ix_news_id ON news (id);
CREATE INDEX ix_news_author_id ON news (author_id);

-- Matches indexes
CREATE INDEX ix_matches_id ON matches (id);
CREATE INDEX ix_matches_home_team ON matches (home_team);
CREATE INDEX ix_matches_away_team ON matches (away_team);
CREATE INDEX ix_matches_status ON matches (status);
CREATE INDEX ix_matches_referee_id ON matches (referee_id);

-- Players indexes
CREATE INDEX ix_players_id ON players (id);
CREATE INDEX ix_players_name ON players (name);
CREATE INDEX ix_players_team_id ON players (team_id);

-- Cup competitions indexes
CREATE INDEX ix_cup_competitions_id ON cup_competitions (id);

-- Cup seasons indexes
CREATE INDEX ix_cup_seasons_id ON cup_seasons (id);
CREATE INDEX ix_cup_seasons_cup_competition_id ON cup_seasons (cup_competition_id);

-- Cup matches indexes
CREATE INDEX ix_cup_matches_id ON cup_matches (id);
CREATE INDEX ix_cup_matches_cup_season_id ON cup_matches (cup_season_id);

-- National teams indexes
CREATE INDEX ix_national_teams_id ON national_teams (id);

-- Tournaments indexes
CREATE UNIQUE INDEX ix_tournaments_name ON tournaments (name);
CREATE INDEX ix_tournaments_id ON tournaments (id);

-- Tournament participations indexes
CREATE INDEX ix_tournament_participations_id ON tournament_participations (id);
CREATE INDEX ix_tournament_participations_national_team_id ON tournament_participations (national_team_id);

-- Tags indexes
CREATE UNIQUE INDEX ix_tags_name ON tags (name);
CREATE UNIQUE INDEX ix_tags_slug ON tags (slug);
CREATE INDEX ix_tags_id ON tags (id);

-- Bulk import logs indexes
CREATE INDEX ix_bulk_import_logs_id ON bulk_import_logs (id);
CREATE INDEX ix_bulk_import_logs_imported_by ON bulk_import_logs (imported_by);

-- Foreign key constraints
ALTER TABLE users ADD CONSTRAINT fk_users_club_id FOREIGN KEY (club_id) REFERENCES teams(id);
ALTER TABLE leagues ADD CONSTRAINT fk_leagues_current_champion_id FOREIGN KEY (current_champion_id) REFERENCES teams(id);
ALTER TABLE league_standings ADD CONSTRAINT fk_league_standings_league_id FOREIGN KEY (league_id) REFERENCES leagues(id);
ALTER TABLE league_standings ADD CONSTRAINT fk_league_standings_team_id FOREIGN KEY (team_id) REFERENCES teams(id);
ALTER TABLE news ADD CONSTRAINT fk_news_author_id FOREIGN KEY (author_id) REFERENCES users(id);
ALTER TABLE matches ADD CONSTRAINT fk_matches_referee_id FOREIGN KEY (referee_id) REFERENCES users(id);
ALTER TABLE players ADD CONSTRAINT fk_players_team_id FOREIGN KEY (team_id) REFERENCES teams(id);
ALTER TABLE cup_competitions ADD CONSTRAINT fk_cup_competitions_current_champion_id FOREIGN KEY (current_champion_id) REFERENCES teams(id);
ALTER TABLE cup_seasons ADD CONSTRAINT fk_cup_seasons_cup_competition_id FOREIGN KEY (cup_competition_id) REFERENCES cup_competitions(id);
ALTER TABLE cup_seasons ADD CONSTRAINT fk_cup_seasons_winner_id FOREIGN KEY (winner_id) REFERENCES teams(id);
ALTER TABLE cup_seasons ADD CONSTRAINT fk_cup_seasons_runner_up_id FOREIGN KEY (runner_up_id) REFERENCES teams(id);
ALTER TABLE cup_matches ADD CONSTRAINT fk_cup_matches_cup_season_id FOREIGN KEY (cup_season_id) REFERENCES cup_seasons(id);
ALTER TABLE cup_matches ADD CONSTRAINT fk_cup_matches_home_team_id FOREIGN KEY (home_team_id) REFERENCES teams(id);
ALTER TABLE cup_matches ADD CONSTRAINT fk_cup_matches_away_team_id FOREIGN KEY (away_team_id) REFERENCES teams(id);
ALTER TABLE cup_matches ADD CONSTRAINT fk_cup_matches_winner_id FOREIGN KEY (winner_id) REFERENCES teams(id);
ALTER TABLE national_teams ADD CONSTRAINT fk_national_teams_captain_id FOREIGN KEY (captain_id) REFERENCES players(id);
ALTER TABLE tournament_participations ADD CONSTRAINT fk_tournament_participations_national_team_id FOREIGN KEY (national_team_id) REFERENCES national_teams(id);
ALTER TABLE promotion_relegation_rules ADD CONSTRAINT fk_pr_rules_from_league_id FOREIGN KEY (from_league_id) REFERENCES leagues(id);
ALTER TABLE promotion_relegation_rules ADD CONSTRAINT fk_pr_rules_to_league_id FOREIGN KEY (to_league_id) REFERENCES leagues(id);
ALTER TABLE promotion_relegations ADD CONSTRAINT fk_pr_team_id FOREIGN KEY (team_id) REFERENCES teams(id);
ALTER TABLE promotion_relegations ADD CONSTRAINT fk_pr_from_league_id FOREIGN KEY (from_league_id) REFERENCES leagues(id);
ALTER TABLE promotion_relegations ADD CONSTRAINT fk_pr_to_league_id FOREIGN KEY (to_league_id) REFERENCES leagues(id);
ALTER TABLE news_tags ADD CONSTRAINT fk_news_tags_news_id FOREIGN KEY (news_id) REFERENCES news(id);
ALTER TABLE news_tags ADD CONSTRAINT fk_news_tags_tag_id FOREIGN KEY (tag_id) REFERENCES tags(id);
ALTER TABLE bulk_import_logs ADD CONSTRAINT fk_bulk_import_logs_imported_by FOREIGN KEY (imported_by) REFERENCES users(id);
ALTER TABLE continental_qualifications ADD CONSTRAINT fk_continental_qualifications_team_id FOREIGN KEY (qualifying_team_id) REFERENCES teams(id);
ALTER TABLE match_events ADD CONSTRAINT fk_match_events_match_id FOREIGN KEY (match_id) REFERENCES matches(id);
ALTER TABLE match_events ADD CONSTRAINT fk_match_events_player_id FOREIGN KEY (player_id) REFERENCES players(id);
ALTER TABLE match_events ADD CONSTRAINT fk_match_events_related_player_id FOREIGN KEY (related_player_id) REFERENCES players(id);
ALTER TABLE match_reports ADD CONSTRAINT fk_match_reports_match_id FOREIGN KEY (match_id) REFERENCES matches(id);
ALTER TABLE match_reports ADD CONSTRAINT fk_match_reports_referee_id FOREIGN KEY (referee_id) REFERENCES users(id);
ALTER TABLE national_team_fixtures ADD CONSTRAINT fk_ntf_national_team_id FOREIGN KEY (national_team_id) REFERENCES national_teams(id);
ALTER TABLE league_tables ADD CONSTRAINT fk_league_tables_team_id FOREIGN KEY (team_id) REFERENCES teams(id);

-- =====================================================
-- STEP 7: Update sequences (no longer needed for UUID, but keep for compatibility)
-- =====================================================

-- Grant permissions (if needed)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- Check row counts
SELECT 'teams' AS table_name, COUNT(*) FROM teams
UNION ALL
SELECT 'users', COUNT(*) FROM users
UNION ALL
SELECT 'leagues', COUNT(*) FROM leagues
UNION ALL
SELECT 'league_standings', COUNT(*) FROM league_standings
UNION ALL
SELECT 'news', COUNT(*) FROM news
UNION ALL
SELECT 'matches', COUNT(*) FROM matches
UNION ALL
SELECT 'players', COUNT(*) FROM players
UNION ALL
SELECT 'cup_competitions', COUNT(*) FROM cup_competitions
UNION ALL
SELECT 'cup_seasons', COUNT(*) FROM cup_seasons
UNION ALL
SELECT 'cup_matches', COUNT(*) FROM cup_matches
UNION ALL
SELECT 'national_teams', COUNT(*) FROM national_teams
UNION ALL
SELECT 'tournaments', COUNT(*) FROM tournaments
UNION ALL
SELECT 'tournament_participations', COUNT(*) FROM tournament_participations
UNION ALL
SELECT 'promotion_relegation_rules', COUNT(*) FROM promotion_relegation_rules
UNION ALL
SELECT 'tags', COUNT(*) FROM tags
UNION ALL
SELECT 'seasons', COUNT(*) FROM seasons;

-- Verify foreign keys are intact (should return 0 if all OK)
SELECT COUNT(*) AS orphaned_records FROM users u LEFT JOIN teams t ON u.club_id = t.id WHERE u.club_id IS NOT NULL AND t.id IS NULL;