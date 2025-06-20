import pandas as pd
import os
import json
import glob
from datetime import datetime
from collections import defaultdict

def extract_match_features():
    """
    Extract match-level features from JSON files and save to CSV.
    """
    # List of teams to exclude - only historical/defunct teams
    EXCLUDED_TEAMS = {
        'Rising Pune Supergiant',
        'Gujarat Lions',
        'Rising Pune Supergiants',
        'Pune Warriors',
        'Kochi Tuskers Kerala',
        'Deccan Chargers'  # Historical team
    }
    
    # Team name mapping for teams that have changed names or have variations
    TEAM_NAME_MAPPING = {
        'Kings XI Punjab': 'Punjab Kings',
        'Royal Challengers Bangalore': 'Royal Challengers Bengaluru',
        'Delhi Daredevils': 'Delhi Capitals',
        'Gujarat Titans': 'Gujarat Titans', 
        'Lucknow Super Giants': 'Lucknow Super Giants'
    }
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join('data', 'raw', 'matches')
    os.makedirs(output_dir, exist_ok=True)
    
    # Get list of match JSON files
    match_files = glob.glob(os.path.join('ipl_data', '*.json'))
    
    if not match_files:
        print("No match JSON files found. Please ensure data is in ipl_data directory.")
        return
    
    # First pass - collect matches by date to determine day/night
    matches_by_date = defaultdict(list)
    date_match_mapping = {}
    
    # First scan to group matches by date
    for file_path in match_files:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            match_id = os.path.basename(file_path).split('.')[0]
            info = data.get('info', {})
            date = info.get('dates', [''])[0] if 'dates' in info else ''
            teams = info.get('teams', [])
            
            # Skip matches involving excluded teams
            if any(team in EXCLUDED_TEAMS for team in teams):
                continue
                
            if date:
                matches_by_date[date].append(match_id)
                date_match_mapping[match_id] = date
        except Exception as e:
            print(f"Error pre-processing {file_path}: {e}")
    
    # Sort match IDs within each date to determine day/night
    for date, match_ids in matches_by_date.items():
        match_ids.sort()  # Sort by match ID (ascending)
    
    # Second pass - extract all match data
    match_data = []
    
    for file_path in match_files:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Extract match ID from filename
            match_id = os.path.basename(file_path).split('.')[0]
            
            # Extract basic match info
            info = data.get('info', {})
            
            date = info.get('dates', [''])[0] if 'dates' in info else ''
            teams = info.get('teams', [])
            
            # Skip matches involving excluded teams
            if any(team in EXCLUDED_TEAMS for team in teams):
                continue
                
            # Map team names for consistency
            team1 = TEAM_NAME_MAPPING.get(teams[0], teams[0]) if len(teams) > 0 else ''
            team2 = TEAM_NAME_MAPPING.get(teams[1], teams[1]) if len(teams) > 1 else ''
            
            toss = info.get('toss', {})
            toss_winner = toss.get('winner', '')
            # Map toss winner name for consistency
            toss_winner = TEAM_NAME_MAPPING.get(toss_winner, toss_winner)
            toss_decision = toss.get('decision', '')
            
            venue = info.get('venue', '')
            city = info.get('city', '')
            
            match_type = info.get('match_type', '')
            
            # Extract event/stage information
            event = info.get('event', {})
            stage = event.get('stage', 'Group') if event else 'Group'
            
            outcome = info.get('outcome', {})
            winner = outcome.get('winner', '')
            # Map winner name for consistency
            winner = TEAM_NAME_MAPPING.get(winner, winner)
            
            # Extract win type and margin
            win_by = ''
            win_margin = 0
            if 'by' in outcome:
                for win_type, margin in outcome['by'].items():
                    win_by = win_type
                    win_margin = margin
            
            # Extract innings data if available
            innings = data.get('innings', [])
            
            innings1_runs = 0
            innings2_runs = 0
            innings1_wickets = 0
            innings2_wickets = 0
            
            if len(innings) > 0:
                # Count deliveries to calculate wickets
                deliveries1 = [d for over in innings[0].get('overs', []) for d in over.get('deliveries', [])]
                innings1_wickets = sum(1 for d in deliveries1 if 'wickets' in d)
                
                # Calculate total runs
                innings1_runs = sum(d.get('runs', {}).get('total', 0) for d in deliveries1)
            
            if len(innings) > 1:
                # Count deliveries to calculate wickets
                deliveries2 = [d for over in innings[1].get('overs', []) for d in over.get('deliveries', [])]
                innings2_wickets = sum(1 for d in deliveries2 if 'wickets' in d)
                
                # Calculate total runs
                innings2_runs = sum(d.get('runs', {}).get('total', 0) for d in deliveries2)
            
            # Determine day/night based on the rule:
            # If multiple matches on same date, first match (by ID) is day match, rest are night
            day_night_value = "Night"  # Default assumption
            if date in matches_by_date and len(matches_by_date[date]) > 1:
                # If this is the lowest match ID for this date, it's a day match
                if match_id == matches_by_date[date][0]:
                    day_night_value = "Day"
            
            dl_applied = 'method' in outcome
            
            match_data.append({
                'match_id': match_id,
                'date': date,
                'team1': team1,
                'team2': team2,
                'toss_winner': toss_winner,
                'toss_decision': toss_decision,
                'venue': venue,
                'city': city,
                'match_type': stage,  # Using stage field for match_type
                'winner': winner,
                'win_by': win_by,
                'win_margin': win_margin,
                'innings1_runs': innings1_runs,
                'innings2_runs': innings2_runs,
                'innings1_wickets': innings1_wickets,
                'innings2_wickets': innings2_wickets,
                'day_night': day_night_value,  # Using new day/night value
                'dl_applied': dl_applied
            })
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    # Create DataFrame and save to CSV
    if match_data:
        df = pd.DataFrame(match_data)
        output_path = os.path.join(output_dir, 'match_metadata.csv')
        df.to_csv(output_path, index=False)
        print(f"Match features saved to {output_path}")
    else:
        print("No match data was extracted.")

if __name__ == "__main__":
    extract_match_features()