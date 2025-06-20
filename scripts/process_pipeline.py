import pandas as pd
import os

# ----------------------
#  process_pipeline.py
# ----------------------
# Combines match metadata, team performance, player performance (future),
# and weather data into a unified match-level feature set for ML modeling.

# 1. Define file paths
RAW_DIR = os.path.join('data', 'raw')
MATCH_PATH = os.path.join(RAW_DIR, 'matches', 'match_metadata.csv')
TEAMS_PATH = os.path.join(RAW_DIR, 'teams', 'team_performance.csv')
# Placeholder for player data integration
# PLAYERS_PATH = os.path.join(RAW_DIR, 'players', 'players_performance.csv')
WEATHER_PATH = os.path.join(RAW_DIR, 'weather', 'weather_by_match.csv')
OUTPUT_DIR = os.path.join('data', 'processed')
OUTPUT_PATH = os.path.join(OUTPUT_DIR, 'match_feature_set.csv')

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 2. Load source data
matches_df = pd.read_csv(MATCH_PATH)
teams_df = pd.read_csv(TEAMS_PATH)
weather_df = pd.read_csv(WEATHER_PATH)

# 3. Standardize team names to codes for merging with teams_df
team_codes = {
    'Mumbai Indians': 'MI', 'Chennai Super Kings': 'CSK',
    'Royal Challengers Bangalore': 'RCB', 'Royal Challengers Bengaluru': 'RCB',
    'Kolkata Knight Riders': 'KKR', 'Delhi Capitals': 'DC',
    'Delhi Daredevils': 'DC', 'Punjab Kings': 'PBKS',
    'Kings XI Punjab': 'PBKS', 'Rajasthan Royals': 'RR',
    'Sunrisers Hyderabad': 'SRH', 'Lucknow Super Giants': 'LSG',
    'Gujarat Titans': 'GT'
}

def to_code(name):
    return team_codes.get(name, name)

# Apply mapping
matches_df['team1_code'] = matches_df['team1'].map(to_code)
matches_df['team2_code'] = matches_df['team2'].map(to_code)

# 4. Merge team performance for team1 and team2
# Prefix team1 features
team1_feats = teams_df.add_prefix('team1_').rename(columns={'team1_team_name': 'team1_code'})
# Prefix team2 features
team2_feats = teams_df.add_prefix('team2_').rename(columns={'team2_team_name': 'team2_code'})

# Merge into matches
df = matches_df.merge(team1_feats, on='team1_code', how='left')
df = df.merge(team2_feats, on='team2_code', how='left')

# 5. Merge weather data (hourly) - keeps long format for time-aware models
# Ensure consistent types
df['match_id'] = df['match_id'].astype(str)
weather_df['match_id'] = weather_df['match_id'].astype(str)

# Merge
df = df.merge(weather_df, on='match_id', how='left', suffixes=('', '_w'))

# 6. Cleanup duplicate metadata columns from weather merge
for suffix in ['_w']:
    for col in ['date', 'venue', 'city', 'day_night']:
        dup_col = col + suffix
        if dup_col in df.columns:
            df.drop(columns=dup_col, inplace=True)

# Rename original metadata columns for clarity (if desired)
df.rename(columns={
    'date': 'match_date',
    'venue': 'match_venue',
    'city': 'match_city',
    'day_night': 'is_night_match'
}, inplace=True)

# 7. (Optional) Player-level integration placeholder
# players_df = pd.read_csv(PLAYERS_PATH)
# ... compute lineup-based aggregates, e.g. team1_avg_consistency, team2_avg_consistency

# 8. Save the final feature set
print(f"Final dataset shape: {df.shape}")
print("Columns in final dataset:")
print(df.columns.tolist())

df.to_csv(OUTPUT_PATH, index=False)
print(f"Saved match feature set to {OUTPUT_PATH}")
