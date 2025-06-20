import json
import os
import pandas as pd
from collections import defaultdict
from datetime import datetime
import numpy as np
from pathlib import Path

def determine_role(player_stats):
    """Determine player role based on their statistics"""
    total_runs = sum(match['runs'] for match in player_stats['batting_performances'])
    total_wickets = sum(match['wickets'] for match in player_stats['bowling_performances'])
    total_matches = len(set(match['match_id'] for match in player_stats['batting_performances'] + player_stats['bowling_performances']))
    
    # Basic classification logic
    if total_wickets > total_matches * 0.5:  # Average more than 0.5 wickets per match
        if total_runs > total_matches * 15:  # Also scores runs regularly
            return 'All-rounder'
        return 'Bowler'
    elif total_runs > total_matches * 15:  # Average more than 15 runs per match
        return 'Batsman'
    return 'All-rounder'  # Default to all-rounder if unclear

def calculate_player_consistency(stats, role):
    """Calculate player consistency score based on role and recent performances"""
    batting_perfs = sorted(stats['batting_performances'], key=lambda x: x['date'], reverse=True)[:7]
    bowling_perfs = sorted(stats['bowling_performances'], key=lambda x: x['date'], reverse=True)[:7]
    
    # Calculate batting consistency if relevant
    consistency_bat = 0
    if role in ['Batsman', 'All-rounder']:
        if batting_perfs:
            # Get last 7 matches stats
            runs_per_match = [p['runs'] for p in batting_perfs]
            total_runs = sum(runs_per_match)
            total_balls = sum(p['balls'] for p in batting_perfs)
            boundaries = sum(p['fours'] + p['sixes'] for p in batting_perfs)
            
            # Calculate metrics
            avg_last_7 = total_runs / len(batting_perfs)
            strike_rate_last_7 = (total_runs / total_balls * 100) if total_balls > 0 else 0
            boundaries_per_match = boundaries / len(batting_perfs)
            std_dev_runs = np.std(runs_per_match) if len(runs_per_match) > 1 else 0
            
            # Normalize values
            normalized_avg = min(avg_last_7 / 50 * 100, 100)  # Consider 50+ average as max
            normalized_sr = min(strike_rate_last_7 / 200 * 100, 100)  # Consider 200+ SR as max
            normalized_boundaries = min(boundaries_per_match * 10, 100)  # 10 boundaries per match as max
            volatility_score = 100 - min((std_dev_runs / (avg_last_7 if avg_last_7 > 0 else 1)) * 100, 100)
            
            # Calculate batting consistency
            consistency_bat = (
                0.4 * normalized_avg +
                0.3 * normalized_sr +
                0.2 * normalized_boundaries +
                0.1 * volatility_score
            )
    
    # Calculate bowling consistency if relevant
    consistency_bowl = 0
    if role in ['Bowler', 'All-rounder']:
        if bowling_perfs:
            # Get last 7 matches stats
            wickets_per_match = [p['wickets'] for p in bowling_perfs]
            total_wickets = sum(wickets_per_match)
            total_runs_conceded = sum(p['runs_conceded'] for p in bowling_perfs)
            total_overs = sum(p['overs'] for p in bowling_perfs)
            total_dots = sum(p['dots'] for p in bowling_perfs)
            total_balls = total_overs * 6
            
            # Calculate metrics
            economy_per_match = [(p['runs_conceded'] / p['overs']) if p['overs'] > 0 else 0 for p in bowling_perfs]
            avg_economy = (total_runs_conceded / total_overs) if total_overs > 0 else 0
            dot_ball_pct = (total_dots / total_balls * 100) if total_balls > 0 else 0
            std_dev_economy = np.std(economy_per_match) if len(economy_per_match) > 1 else 0
            
            # Normalize values
            normalized_wickets = min(total_wickets / len(bowling_perfs) * 20, 100)  # 5 wickets per match as max
            normalized_dots = dot_ball_pct  # Already a percentage
            normalized_economy = max(0, 100 - (avg_economy * 10))  # Economy of 10+ gets 0, 0 gets 100
            volatility_score = 100 - min((std_dev_economy / (avg_economy if avg_economy > 0 else 1)) * 100, 100)
            
            # Calculate bowling consistency
            consistency_bowl = (
                0.4 * normalized_wickets +
                0.3 * normalized_dots +
                0.2 * normalized_economy +
                0.1 * volatility_score
            )
    
    # Calculate final consistency score based on role
    if role == 'Batsman':
        return consistency_bat
    elif role == 'Bowler':
        return consistency_bowl
    else:  # All-rounder
        return (consistency_bat + consistency_bowl) / 2

def process_wicket(delivery):
    """Process wicket information from a delivery to count only bowler's wickets"""
    if 'wickets' not in delivery:
        return 0
        
    wicket_count = 0
    for wicket in delivery['wickets']:
        # Direct bowler wickets
        if wicket.get('kind') in {'bowled', 'lbw', 'stumped', 'hit wicket'}:
            wicket_count += 1
        # Caught wickets - credit to bowler
        elif wicket.get('kind') in {'caught', 'caught and bowled'}:
            wicket_count += 1
        # Ignore run outs, retired hurt, etc.
            
    return wicket_count

def process_player_stats():
    # Initialize player statistics
    player_stats = defaultdict(lambda: {
        'name': '',
        'teams': set(),
        'batting_performances': [],
        'bowling_performances': [],
        'latest_team': ''
    })
    
    # Get all JSON files from ipl_data directory and sort them chronologically
    json_files = sorted([f for f in os.listdir('ipl_data') if f.endswith('.json')])
    print(f"Processing {len(json_files)} match files...")
    
    for file_name in json_files:
        with open(os.path.join('ipl_data', file_name), 'r') as f:
            match_data = json.load(f)
            
        # Skip if the match doesn't have innings data
        if 'innings' not in match_data or not match_data['innings']:
            continue
            
        match_date = datetime.strptime(match_data['info']['dates'][0], '%Y-%m-%d')
        match_id = file_name.split('.')[0]
        
        # Process each innings
        for innings in match_data['innings']:
            if 'overs' not in innings:
                continue
                
            batting_team = innings['team']
            bowling_team = [team for team in match_data['info']['teams'] if team != batting_team][0]
            
            # Initialize per-innings player stats
            innings_stats = defaultdict(lambda: {'runs': 0, 'balls': 0, 'fours': 0, 'sixes': 0, 'dots': 0})
            bowler_stats = defaultdict(lambda: {'overs': 0, 'runs_conceded': 0, 'wickets': 0, 'dots': 0})
            
            # Process each over
            for over in innings['overs']:
                for delivery in over.get('deliveries', []):
                    batter = delivery['batter']
                    bowler = delivery['bowler']
                    
                    # Update batter stats
                    runs = delivery.get('runs', {})
                    batter_runs = runs.get('batter', 0)
                    total_runs = runs.get('total', 0)
                    
                    innings_stats[batter]['runs'] += batter_runs
                    innings_stats[batter]['balls'] += 1
                    innings_stats[batter]['fours'] += 1 if batter_runs == 4 else 0
                    innings_stats[batter]['sixes'] += 1 if batter_runs == 6 else 0
                    innings_stats[batter]['dots'] += 1 if total_runs == 0 else 0
                    
                    # Update bowler stats with new wicket calculation
                    bowler_stats[bowler]['overs'] += 1/6
                    bowler_stats[bowler]['runs_conceded'] += total_runs
                    bowler_stats[bowler]['wickets'] += process_wicket(delivery)
                    bowler_stats[bowler]['dots'] += 1 if total_runs == 0 else 0
            
            # Add innings stats to overall player stats
            for batter, stats in innings_stats.items():
                player_stats[batter]['name'] = batter
                player_stats[batter]['teams'].add(batting_team)
                player_stats[batter]['latest_team'] = batting_team
                player_stats[batter]['batting_performances'].append({
                    'match_id': match_id,
                    'date': match_date,
                    **stats
                })
            
            for bowler, stats in bowler_stats.items():
                player_stats[bowler]['name'] = bowler
                player_stats[bowler]['teams'].add(bowling_team)
                player_stats[bowler]['latest_team'] = bowling_team
                player_stats[bowler]['bowling_performances'].append({
                    'match_id': match_id,
                    'date': match_date,
                    **stats
                })
    
    # Calculate final statistics for each player
    final_stats = []
    for player_id, stats in player_stats.items():
        # Sort performances by date
        batting_perfs = sorted(stats['batting_performances'], key=lambda x: x['date'], reverse=True)
        bowling_perfs = sorted(stats['bowling_performances'], key=lambda x: x['date'], reverse=True)
        
        # Determine player role
        role = determine_role(stats)
        
        # Check if batsman has bowled in the last 3 years
        current_year = 2025
        three_years_ago = current_year - 3
        has_bowled_recently = False
        
        if role == 'Batsman':
            # Check if player has bowled any overs in the last 3 years
            for perf in bowling_perfs:
                perf_year = perf['date'].year
                if perf_year >= three_years_ago and perf['overs'] > 0:
                    has_bowled_recently = True
                    break
        
        recent_batting = batting_perfs[:7]
        recent_bowling = bowling_perfs[:7]
        
        # Calculate overall batting stats
        total_career_runs = sum(p['runs'] for p in batting_perfs)
        total_career_balls = sum(p['balls'] for p in batting_perfs)
        total_career_fours = sum(p['fours'] for p in batting_perfs)
        total_career_sixes = sum(p['sixes'] for p in batting_perfs)
        
        # Calculate recent batting stats
        recent_runs = sum(p['runs'] for p in recent_batting)
        recent_balls = sum(p['balls'] for p in recent_batting)
        recent_fours = sum(p['fours'] for p in recent_batting)
        recent_sixes = sum(p['sixes'] for p in recent_batting)
        recent_batting_dots = sum(p['dots'] for p in recent_batting)
        
        # Calculate recent bowling stats only if:
        # 1. There are bowling performances, AND
        # 2. Player is either a Bowler/All-rounder OR a Batsman who has bowled in the last 3 years
        if recent_bowling and (role != 'Batsman' or has_bowled_recently):
            recent_wickets = sum(p['wickets'] for p in recent_bowling)
            recent_overs = sum(p['overs'] for p in recent_bowling)
            recent_runs_conceded = sum(p['runs_conceded'] for p in recent_bowling)
            recent_bowling_dots = sum(p['dots'] for p in recent_bowling)
            recent_economy = (recent_runs_conceded / recent_overs) if recent_overs > 0 else 0
        else:
            recent_wickets = 0
            recent_overs = 0
            recent_runs_conceded = 0
            recent_bowling_dots = 0
            recent_economy = 0
        
        # Calculate overall bowling stats
        total_career_wickets = sum(p['wickets'] for p in bowling_perfs)
        total_career_overs = sum(p['overs'] for p in bowling_perfs)
        total_career_runs_conceded = sum(p['runs_conceded'] for p in bowling_perfs)
        
        # Calculate metrics
        matches_played = len(set(p['match_id'] for p in stats['batting_performances'] + stats['bowling_performances']))
        recent_matches = len(set(p['match_id'] for p in recent_batting + recent_bowling))
        
        career_avg = total_career_runs / matches_played if matches_played > 0 else 0
        career_sr = (total_career_runs / total_career_balls * 100) if total_career_balls > 0 else 0
        
        recent_avg = recent_runs / recent_matches if recent_matches > 0 else 0
        recent_sr = (recent_runs / recent_balls * 100) if recent_balls > 0 else 0
        
        career_economy = (total_career_runs_conceded / total_career_overs) if total_career_overs > 0 else 0
        
        # Ensure recent_overs is always a number (0 if there are no bowling performances)
        total_recent_deliveries = recent_balls + (recent_overs * 6)
        dot_ball_pct = ((recent_batting_dots + recent_bowling_dots) / total_recent_deliveries * 100) if total_recent_deliveries > 0 else 0
        
        # Calculate player consistency score using the new method
        player_consistency_score = calculate_player_consistency(stats, role)
        
        final_stats.append({
            'player_name': stats['name'],
            'matches_played': matches_played,
            'role': role,
            
            # Career stats
            'total_runs': total_career_runs,
            'career_average': round(career_avg, 2),
            'career_strike_rate': round(career_sr, 2),
            'total_wickets': total_career_wickets,
            'career_economy': round(career_economy, 2),
            'total_4s': total_career_fours,
            'total_6s': total_career_sixes,
            
            # Recent form (last 7 matches)
            'runs_last_7': recent_runs,
            'avg_last_7': round(recent_avg, 2),
            'strike_rate_last_7': round(recent_sr, 2),
            'wickets_last_7': recent_wickets,
            'economy_last_7': round(recent_economy, 2),
            '4s_6s_last_7': recent_fours + recent_sixes,
            'dot_ball_pct_last_7': round(dot_ball_pct, 2),
            'player_consistency_score': round(player_consistency_score, 2)
        })
    
    # Create output directory if it doesn't exist
    output_dir = Path('data/raw/players')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save to CSV
    df = pd.DataFrame(final_stats)
    df.to_csv('data/raw/players/players_performance.csv', index=False)
    print(f"Processed {len(final_stats)} players statistics")

if __name__ == "__main__":
    process_player_stats()