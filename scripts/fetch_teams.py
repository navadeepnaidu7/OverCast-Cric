import json
import os
import pandas as pd
from collections import defaultdict
from datetime import datetime
import numpy as np
from pathlib import Path

def get_team_code(team_name):
    """Return the standardized team code"""
    team_codes = {
        'Mumbai Indians': 'MI',
        'Chennai Super Kings': 'CSK',
        'Royal Challengers Bangalore': 'RCB',
        'Royal Challengers Bengaluru': 'RCB',
        'Kolkata Knight Riders': 'KKR',
        'Delhi Capitals': 'DC',
        'Delhi Daredevils': 'DC',
        'Punjab Kings': 'PBKS',
        'Kings XI Punjab': 'PBKS',
        'Rajasthan Royals': 'RR',
        'Sunrisers Hyderabad': 'SRH',
        'Lucknow Super Giants': 'LSG',
        'Gujarat Titans': 'GT'
    }
    return team_codes.get(team_name, team_name)

def get_home_venue(team):
    """Return the home venue(s) for each IPL team"""
    home_venues = {
        'Mumbai Indians': ['Wankhede Stadium, Mumbai'],
        'Chennai Super Kings': ['MA Chidambaram Stadium, Chepauk', 'MA Chidambaram Stadium', 'MA Chidambaram Stadium, Chennai'],
        'Royal Challengers Bengaluru': ['M Chinnaswamy Stadium, Bengaluru', 'M Chinnaswamy Stadium'],
        'Kolkata Knight Riders': ['Eden Gardens, Kolkata'],
        'Delhi Capitals': ['Arun Jaitley Stadium, Delhi'],
        'Punjab Kings': ['IS Bindra Stadium, Mohali', 'Himachal Pradesh Cricket Association Stadium, Dharamsala', 'Himachal Pradesh Cricket Association Stadium'],
        'Rajasthan Royals': ['Sawai Mansingh Stadium, Jaipur'],
        'Sunrisers Hyderabad': ['Rajiv Gandhi International Stadium, Uppal'],
        'Lucknow Super Giants': ['Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium, Lucknow'],
        'Gujarat Titans': ['Narendra Modi Stadium, Ahmedabad']
    }
    return home_venues.get(team, [])

def calculate_team_stats():
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
    
    # Initialize data structures to store team statistics
    team_stats = defaultdict(lambda: {
        'matches': [],  
        'batting_scores': [],  
        'bowling_scores': [],  
        'wickets_data': [],  
        'venues_played': set()  
    })
    
    # Get all JSON files from ipl_data directory and sort them chronologically
    json_files = sorted([f for f in os.listdir('ipl_data') if f.endswith('.json')])
    print(f"Total JSON files found: {len(json_files)}")
    
    # Debug counters
    match_counts = defaultdict(int)
    skipped_matches = []
    
    for file_name in json_files:
        with open(os.path.join('ipl_data', file_name), 'r') as f:
            match_data = json.load(f)
            
        # Skip if the match doesn't have innings data
        if 'innings' not in match_data or not match_data['innings']:
            continue
            
        match_date = datetime.strptime(match_data['info']['dates'][0], '%Y-%m-%d')
        teams = [TEAM_NAME_MAPPING.get(team, team) for team in match_data['info']['teams']]
        venue = match_data['info'].get('venue', '')
        
        # Skip matches involving excluded teams
        if any(team in EXCLUDED_TEAMS for team in teams):
            continue
            
        winner = match_data['info'].get('outcome', {}).get('winner', None)
        if winner:
            winner = TEAM_NAME_MAPPING.get(winner, winner)
            
        # Process first innings
        if len(match_data['innings']) >= 1:
            first_innings = match_data['innings'][0]
            first_innings_team = TEAM_NAME_MAPPING.get(first_innings['team'], first_innings['team'])
            
            # Calculate phase-wise scores and wickets
            powerplay_runs = 0
            death_overs_runs = 0
            total_wickets = 0
            
            for over in first_innings['overs']:
                over_num = over['over']
                over_runs = sum(d.get('runs', {}).get('total', 0) for d in over['deliveries'])
                over_wickets = sum(1 for d in over['deliveries'] if 'wickets' in d)
                
                if over_num < 6:  # Powerplay
                    powerplay_runs += over_runs
                elif over_num >= 15:  # Death overs
                    death_overs_runs += over_runs
                    
                total_wickets += over_wickets
            
            first_innings_score = sum(
                delivery.get('runs', {}).get('total', 0)
                for over in first_innings['overs']
                for delivery in over['deliveries']
            )
            
            # Update first innings team stats
            margin = 0
            if winner:
                margin = first_innings_score - sum(
                    delivery.get('runs', {}).get('total', 0)
                    for over in match_data['innings'][1]['overs']
                    for delivery in over['deliveries']
                ) if winner == first_innings_team else -(first_innings_score - sum(
                    delivery.get('runs', {}).get('total', 0)
                    for over in match_data['innings'][1]['overs']
                    for delivery in over['deliveries']
                ))
            
            # Check if it's a home game
            home_venues = get_home_venue(first_innings_team)
            is_home_game = any(home_venue in venue for home_venue in home_venues)
            
            team_stats[first_innings_team]['matches'].append((
                match_date,
                1 if first_innings_team == winner else 0,
                margin,
                True,  # batting_first
                'home' if is_home_game else 'away'
            ))
            
            team_stats[first_innings_team]['batting_scores'].append((
                match_date,
                first_innings_score,
                powerplay_runs,
                death_overs_runs
            ))
            
            team_stats[first_innings_team]['wickets_data'].append((
                match_date,
                0,  # wickets_taken (will be updated in second innings)
                total_wickets  # wickets_lost
            ))
            
            team_stats[first_innings_team]['venues_played'].add(venue)
            
            # Process second innings similarly
            if len(match_data['innings']) >= 2:
                second_innings = match_data['innings'][1]
                second_innings_team = TEAM_NAME_MAPPING.get(second_innings['team'], second_innings['team'])
                
                powerplay_runs = 0
                death_overs_runs = 0
                total_wickets = 0
                
                for over in second_innings['overs']:
                    over_num = over['over']
                    over_runs = sum(d.get('runs', {}).get('total', 0) for d in over['deliveries'])
                    over_wickets = sum(1 for d in over['deliveries'] if 'wickets' in d)
                    
                    if over_num < 6:
                        powerplay_runs += over_runs
                    elif over_num >= 15:
                        death_overs_runs += over_runs
                        
                    total_wickets += over_wickets
                
                second_innings_score = sum(
                    delivery.get('runs', {}).get('total', 0)
                    for over in second_innings['overs']
                    for delivery in over['deliveries']
                )
                
                # Check if it's a home game for second innings team
                home_venues = get_home_venue(second_innings_team)
                is_home_game = any(home_venue in venue for home_venue in home_venues)
                
                team_stats[second_innings_team]['matches'].append((
                    match_date,
                    1 if second_innings_team == winner else 0,
                    -margin,  # Negative of first innings margin
                    False,  # batting_first
                    'home' if is_home_game else 'away'
                ))
                
                team_stats[second_innings_team]['batting_scores'].append((
                    match_date,
                    second_innings_score,
                    powerplay_runs,
                    death_overs_runs
                ))
                
                team_stats[second_innings_team]['wickets_data'].append((
                    match_date,
                    total_wickets,  # wickets_taken
                    0  # wickets_lost (will be updated)
                ))
                
                team_stats[second_innings_team]['venues_played'].add(venue)
                
                # Update wickets_taken for first innings team
                team_stats[first_innings_team]['wickets_data'][-1] = (
                    match_date,
                    total_wickets,  # Update wickets_taken
                    team_stats[first_innings_team]['wickets_data'][-1][2]  # Keep wickets_lost
                )

    # Create output directory if it doesn't exist
    output_dir = Path('data/raw/teams')
    output_dir.mkdir(parents=True, exist_ok=True)

    # Prepare final statistics for CSV
    final_stats = []
    for team, stats in team_stats.items():
        if not stats['matches']:
            continue
            
        # Sort all lists by date and get recent matches (last 7)
        recent_matches = sorted(stats['matches'], key=lambda x: x[0], reverse=True)[:7]
        recent_count = len(recent_matches)
        
        # Core Metadata
        team_code = get_team_code(team)
        matches_played = len(stats['matches'])
        
        # Match Outcome Stats
        all_matches = sorted(stats['matches'], key=lambda x: x[0], reverse=True)
        win_percentage_overall = sum(1 for _, result, _, _, _ in all_matches if result == 1) / matches_played * 100
        win_percentage_last_7 = sum(result for _, result, _, _, _ in recent_matches) / recent_count * 100
        
        # Batting first vs Chasing stats
        batting_first_matches = [(date, result) for date, result, _, batting_first, _ in all_matches if batting_first]
        chasing_matches = [(date, result) for date, result, _, batting_first, _ in all_matches if not batting_first]
        recent_batting_first = [(date, result) for date, result in batting_first_matches][:7]
        recent_chasing = [(date, result) for date, result in chasing_matches][:7]
        
        batting_first_win_rate_overall = (sum(result for _, result in batting_first_matches) / len(batting_first_matches) * 100) if batting_first_matches else 0
        chasing_win_rate_overall = (sum(result for _, result in chasing_matches) / len(chasing_matches) * 100) if chasing_matches else 0
        batting_first_win_rate_last_7 = (sum(result for _, result in recent_batting_first) / len(recent_batting_first) * 100) if recent_batting_first else 0
        chasing_win_rate_last_7 = (sum(result for _, result in recent_chasing) / len(recent_chasing) * 100) if recent_chasing else 0
        
        # Batting Performance
        batting_scores = sorted(stats['batting_scores'], key=lambda x: x[0], reverse=True)
        recent_batting = batting_scores[:7]
        
        avg_batting_score_overall = sum(score for _, score, _, _ in batting_scores) / len(batting_scores)
        avg_batting_score_last_7 = sum(score for _, score, _, _ in recent_batting) / len(recent_batting)
        avg_powerplay_score_last_7 = sum(pp_score for _, _, pp_score, _ in recent_batting) / len(recent_batting)
        avg_death_overs_score_last_7 = sum(death_score for _, _, _, death_score in recent_batting) / len(recent_batting)
        
        # Recent wickets stats
        recent_wickets = sorted(stats['wickets_data'], key=lambda x: x[0], reverse=True)[:7]
        wickets_lost_avg_last_7 = sum(wl for _, _, wl in recent_wickets) / len(recent_wickets)
        wickets_taken_avg_last_7 = sum(wt for _, wt, _ in recent_wickets) / len(recent_wickets)
        
        # Advanced Contextual Features
        recent_margins = [margin for _, _, margin, _, _ in recent_matches]
        margin_of_victory_mean_last_7 = sum(recent_margins) / len(recent_margins)
        
        # Home/Away stats
        home_matches = [(date, result) for date, result, _, _, venue_type in all_matches if venue_type == 'home']
        away_matches = [(date, result) for date, result, _, _, venue_type in all_matches if venue_type == 'away']
        
        home_win_rate_overall = (sum(result for _, result in home_matches) / len(home_matches) * 100) if home_matches else 0
        away_win_rate_overall = (sum(result for _, result in away_matches) / len(away_matches) * 100) if away_matches else 0
        
        # Calculate venue adaptability score (0-100)
        venue_count = len(stats['venues_played'])
        venue_adaptability_score = min(100, (venue_count / 10) * 100)  # Normalize to max of 100
        
        # Calculate momentum score (0-100)
        recent_win_weight = 0.4
        margin_weight = 0.3
        consistency_weight = 0.3
        
        recent_win_component = win_percentage_last_7
        margin_component = min(100, abs(margin_of_victory_mean_last_7) * 10)
        consistency_component = 100 - (np.std([result for _, result, _, _, _ in recent_matches]) * 100)
        
        momentum_score = (recent_win_component * recent_win_weight +
                        margin_component * margin_weight +
                        consistency_component * consistency_weight)
        
        final_stats.append({
            # Core Metadata
            'team_name': team_code,
            'matches_played': matches_played,
            'recent_matches_count': recent_count,
            
            # Match Outcome Stats
            'win_percentage_overall': round(win_percentage_overall, 2),
            'win_percentage_last_7': round(win_percentage_last_7, 2),
            'batting_first_win_rate_overall': round(batting_first_win_rate_overall, 2),
            'chasing_win_rate_overall': round(chasing_win_rate_overall, 2),
            'batting_first_win_rate_last_7': round(batting_first_win_rate_last_7, 2),
            'chasing_win_rate_last_7': round(chasing_win_rate_last_7, 2),
            
            # Batting Performance
            'avg_batting_score_overall': round(avg_batting_score_overall, 2),
            'avg_batting_score_last_7': round(avg_batting_score_last_7, 2),
            'avg_powerplay_score_last_7': round(avg_powerplay_score_last_7, 2),
            'avg_death_overs_score_last_7': round(avg_death_overs_score_last_7, 2),
            'wickets_lost_avg_last_7': round(wickets_lost_avg_last_7, 2),
            
            # Bowling Performance
            'wickets_taken_avg_last_7': round(wickets_taken_avg_last_7, 2),
            'bowling_economy_powerplay_last_7': round(avg_powerplay_score_last_7 / 6, 2),  # Runs per over in PP
            'bowling_economy_death_last_7': round(avg_death_overs_score_last_7 / 5, 2),  # Runs per over in death
            
            # Advanced Contextual Features
            'margin_of_victory_mean_last_7': round(margin_of_victory_mean_last_7, 2),
            'momentum_score': round(momentum_score, 2),
            'home_win_rate_overall': round(home_win_rate_overall, 2),
            'away_win_rate_overall': round(away_win_rate_overall, 2),
            'venue_adaptability_score': round(venue_adaptability_score, 2)
        })

    # Save to CSV
    df = pd.DataFrame(final_stats)
    df.to_csv('data/raw/teams/team_performance.csv', index=False)

if __name__ == "__main__":
    calculate_team_stats()