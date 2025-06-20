# IPL Data Processing Scripts Documentation

This directory contains Python scripts for processing IPL match data and generating team and player statistics. The scripts process JSON match data files to calculate various performance metrics for both teams and individual players.


## Usage

All scripts can be run independently:

```python
python fetch_matches.py # Process match metadata
python fetch_teams.py   # Process team statistics
python fetch_players.py # Process player statistics
```

The scripts require:
- Python 3.x
- pandas
- numpy
- Cricsheet's JSON match data files in the `ipl_data/` directory

## Data Structure

Both scripts expect match data in JSON format with specific structure:
- Match information (date, teams, venue)
- Innings data (runs, wickets, overs)
- Player performances (batting, bowling statistics)

The processed data is saved in CSV format for easy analysis and model training.

-------------------------------------------------------------------

## fetch_matches.py

This script extracts match-level metadata from IPL JSON files and creates a consolidated dataset of match information.

### Key Features

1. **Team Name Standardization**
   - Handles team name variations (e.g., "Kings XI Punjab" → "Punjab Kings")
   - Excludes defunct teams (Rising Pune Supergiant, Gujarat Lions, etc.)

2. **Day/Night Match Detection**
   - Automatically determines if match was played during day or night
   - Rules: First match of the day is considered day match, rest are night matches

3. **Match Result Processing**
   - Captures win type (wickets/runs) and margin
   - Records Duckworth-Lewis-Stern (DLS) method application

### Extracted Metrics

#### Match Metadata
- Match ID
- Date
- Teams involved
- Venue and city
- Match type/stage (Group, Playoff, Final)

#### Match Conditions
- Toss winner and decision
- Day/Night classification
- DLS method application

#### Match Outcomes
- Winning team
- Win type (by runs or wickets)
- Win margin
- Innings scores and wickets

### Output
Generates `data/raw/matches/match_metadata.csv` with the above details.

---------------------------------------------------------------

## fetch_teams.py

This script processes team-level statistics from IPL matches and generates comprehensive team performance metrics.

### Key Features

1. **Team Name Standardization**
   - Handles team name variations (e.g., "Kings XI Punjab" → "Punjab Kings")
   - Maintains consistent team codes (e.g., CSK, MI, RCB)
   - Excludes defunct teams (Rising Pune Supergiant, Gujarat Lions, etc.)

2. **Home Venue Mapping**
   - Maps each team to their designated home venue(s)
   - Used for home/away performance analysis

### Calculated Metrics

#### Match Statistics
- **Overall Performance**
  - Win percentage (overall and last 7 matches)
  - Matches played
  - Recent matches count

#### Batting Performance
- **Scoring Metrics**
  - Average batting score (overall and last 7 matches)
  - Powerplay performance (avg. score in first 6 overs)
  - Death overs performance (avg. score in last 5 overs)
  - Wickets lost average (last 7 matches)

#### Bowling Performance
- **Economy Rates**
  - Powerplay economy (runs per over in first 6 overs)
  - Death overs economy (runs per over in last 5 overs)
  - Average wickets taken (last 7 matches)

#### Situational Performance
- **Batting First vs Chasing**
  - Win rate when batting first (overall and last 7)
  - Win rate when chasing (overall and last 7)
- **Home vs Away**
  - Home win rate
  - Away win rate

#### Advanced Metrics
1. **Momentum Score (0-100)**
   Calculated using:
   - Recent win percentage (40% weight)
   - Margin of victory (30% weight)
   - Performance consistency (30% weight)

2. **Venue Adaptability Score (0-100)**
   - Based on number of different venues played at
   - Normalized to max of 100 (10 venues = 100%)

### Output
Generates `data/raw/teams/team_performance.csv` with all team statistics.

----------------------------------------------------------------

## fetch_players.py

This script processes player-level statistics from IPL matches and generates detailed individual performance metrics.

### Key Features

1. **Role Determination**
   Automatically classifies players as:
   - Batsman
   - Bowler
   - All-rounder
   
   Based on:
   - Wickets per match ratio
   - Runs per match ratio

2. **Performance Tracking**
   - Maintains both career and recent (last 7 matches) statistics
   - Tracks players across different teams

### Calculated Metrics

#### Batting Metrics
- **Career Statistics**
  - Total runs
  - Career average
  - Career strike rate
  - Total boundaries (4s and 6s)

- **Recent Form (Last 7 matches)**
  - Recent average
  - Recent strike rate
  - Boundary count
  - Dot ball percentage

#### Bowling Metrics
- **Career Statistics**
  - Total wickets
  - Career economy rate
  - Overs bowled

- **Recent Form (Last 7 matches)**
  - Recent wickets
  - Recent economy rate
  - Dot ball percentage

#### Player Consistency Score (0-100)
Calculated differently based on player role:

1. **Batsman Consistency (100%)**
   - Average runs (40% weight)
   - Strike rate (30% weight)
   - Boundary rate (20% weight)
   - Score volatility (10% weight)

2. **Bowler Consistency (100%)**
   - Wickets per match (40% weight)
   - Dot ball percentage (30% weight)
   - Economy rate (20% weight)
   - Performance volatility (10% weight)

3. **All-rounder Consistency**
   - Average of batting and bowling consistency scores

### Output
Generates `data/raw/players/players_performance.csv` with comprehensive player statistics.


----------------------------------------------------------------

