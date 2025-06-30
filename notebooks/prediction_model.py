import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report

# Load preprocessed match + weather data (long format)
df = pd.read_csv("/data/processed/match_feature_set.csv")

# 1. Detect match type (day, day-night, or night)
# Check if 'start_time' column exists, if not, infer it
if 'start_time' not in df.columns:
    # Extract unique matches
    match_info = df[['match_id']].drop_duplicates()
    
    # For simplicity, we'll assign default times
    # In a real implementation, you might want to extract this from actual data
    # Assumption: Matches with IDs divisible by 7 are double headers with early start
    match_info['is_double_header'] = match_info['match_id'] % 7 == 0
    match_info['start_time'] = match_info['is_double_header'].apply(
        lambda x: '15:30:00' if x else '19:30:00')
    
    # Merge this information back to the main dataframe
    df = pd.merge(df, match_info[['match_id', 'start_time']], on='match_id', how='left')

# Determine match type based on start time
df['match_type'] = df['start_time'].apply(
    lambda x: 'Day' if x == '15:30:00' else 'Night')

# 2. Choose appropriate weather snapshots based on match type
# Define weather times for each match type
day_weather_times = ['15:30:00', '16:00:00', '16:30:00', '17:00:00', '17:30:00', '18:00:00', '18:30:00', '19:00:00']
night_weather_times = ['19:30:00', '20:00:00', '20:30:00', '21:00:00', '21:30:00', '22:00:00', '22:30:00', '23:00:00', '23:30:00']

# Get unique match IDs for each type
day_matches = df[df['match_type'] == 'Day']['match_id'].unique()
night_matches = df[df['match_type'] == 'Night']['match_id'].unique()

# Weather features to extract
weather_features = ['temperature', 'dew_point', 'humidity', 'wind_speed']

# Process day matches
day_pivoted = None
if len(day_matches) > 0:
    day_df = df[df['match_id'].isin(day_matches)]
    day_df = day_df[day_df['timestamp_ist'].isin(day_weather_times)]
    if not day_df.empty:
        day_pivoted = day_df.pivot(index='match_id', columns='timestamp_ist', values=weather_features)
        day_pivoted.columns = [f"{feat}_{time}" for feat, time in day_pivoted.columns]
        day_pivoted.reset_index(inplace=True)

# Process night matches
night_pivoted = None
if len(night_matches) > 0:
    night_df = df[df['match_id'].isin(night_matches)]
    night_df = night_df[night_df['timestamp_ist'].isin(night_weather_times)]
    if not night_df.empty:
        night_pivoted = night_df.pivot(index='match_id', columns='timestamp_ist', values=weather_features)
        night_pivoted.columns = [f"{feat}_{time}" for feat, time in night_pivoted.columns]
        night_pivoted.reset_index(inplace=True)

# Combine the pivoted dataframes
pivoted = pd.DataFrame()
if day_pivoted is not None:
    pivoted = pd.concat([pivoted, day_pivoted]) if not pivoted.empty else day_pivoted
if night_pivoted is not None:
    pivoted = pd.concat([pivoted, night_pivoted]) if not pivoted.empty else night_pivoted

# 3. Extract static features (drop duplicate match_id rows)
static_cols = [
    'match_id', 'team1', 'team2', 'winner', 'match_type', 'start_time',
    'team1_momentum_score', 'team2_momentum_score',
    'team1_avg_batting_score_last_7', 'team2_avg_batting_score_last_7',
    'team1_bowling_economy_death_last_7', 'team2_bowling_economy_death_last_7',
    'team1_home_win_rate_overall', 'team2_home_win_rate_overall',
    'team1_away_win_rate_overall', 'team2_away_win_rate_overall',
    'team1_batting_first_win_rate_last_7', 'team1_chasing_win_rate_last_7',
    'team2_batting_first_win_rate_last_7', 'team2_chasing_win_rate_last_7',
    'team1_margin_of_victory_mean_last_7', 'team2_margin_of_victory_mean_last_7'
]

static_df = df[static_cols].drop_duplicates('match_id')

# Merge with flattened weather
merged = pd.merge(static_df, pivoted, on='match_id', how='inner')

# 4. Encode labels: winner = 1 if team1 wins, else 0
merged['label'] = (merged['winner'] == merged['team1']).astype(int)

# 5. Feature Engineering
# Create dynamic weather features based on match type
merged['match_type_encoded'] = merged['match_type'].apply(lambda x: 1 if x == 'Night' else 0)

# Create a function to get primary weather time based on match type
def get_primary_time(row):
    return '19:30:00' if row['match_type'] == 'Night' else '15:30:00'

merged['primary_time'] = merged.apply(get_primary_time, axis=1)

# Create dynamic weather features
for match_type in ['Day', 'Night']:
    matches = merged[merged['match_type'] == match_type]
    
    if not matches.empty:
        primary_time = '15:30:00' if match_type == 'Day' else '19:30:00'
        # Create primary weather features if columns exist
        temp_col = f"temperature_{primary_time}"
        dew_col = f"dew_point_{primary_time}"
        humidity_col = f"humidity_{primary_time}"
        
        if temp_col in merged.columns and dew_col in merged.columns:
            col_name = f"{match_type.lower()}_dew_difference"
            merged.loc[matches.index, col_name] = matches[temp_col] - matches[dew_col]
        
        if humidity_col in merged.columns and dew_col in merged.columns:
            col_name = f"{match_type.lower()}_humidity_x_dew"
            merged.loc[matches.index, col_name] = matches[humidity_col] * matches[dew_col]

# Add common feature engineering
merged['momentum_diff'] = merged['team1_momentum_score'] - merged['team2_momentum_score']
merged['batting_vs_bowling'] = merged['team1_avg_batting_score_last_7'] - merged['team2_bowling_economy_death_last_7']

# 6. Drop identifiers and unused columns
X = merged.drop(columns=['match_id', 'team1', 'team2', 'winner', 'label', 'match_type', 'start_time', 'primary_time'])
y = merged['label']

# Drop rows with any missing values
X.dropna(inplace=True)
y = y[X.index]  # Align y with X after dropna

# 7. Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 8. Train XGBoost Classifier
model = XGBClassifier(n_estimators=100, learning_rate=0.1, max_depth=3, eval_metric='logloss')
model.fit(X_train, y_train)

# 9. Evaluate
y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Classification Report:\n", classification_report(y_test, y_pred))

# 10. Feature importance analysis
feature_importance = pd.DataFrame({
    'Feature': X.columns,
    'Importance': model.feature_importances_
}).sort_values(by='Importance', ascending=False)

print("\nTop 10 Important Features:")
print(feature_importance.head(10))
