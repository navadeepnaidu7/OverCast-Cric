# 🏏 OverCast-Cric Project

<div align="center">
  
![Cricket](https://img.shields.io/badge/Cricket-Analytics-blue?style=for-the-badge&logo=cricket)
[![Python Version](https://img.shields.io/badge/Python-3.7%2B-brightgreen)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Data Coverage](https://img.shields.io/badge/IPL-2008--2023-orange)](https://www.iplt20.com/)
[![Data Source](https://img.shields.io/badge/Data-Cricsheet-red)](https://cricsheet.org/)
[![Status](https://img.shields.io/badge/Status-Active-success)](https://github.com/navadeepnaidu7/OverCast-Cric)

</div>

A comprehensive open-source data analytics and prediction platform for Indian Premier League (IPL) cricket. The OverCast-Cric project analyzes match data to uncover insights and predict detailed match outcomes in various scenarios.

## 🔍 Project Overview

The OverCast-Cric Project aims to provide cricket enthusiasts, analysts, researchers, and teams with powerful tools to analyze IPL cricket data. The project is focused on IPL T20 cricket due to its rich dataset and popularity.

Our platform processes detailed match data to extract meaningful insights about team performances, player contributions, match dynamics, and generate nuanced predictions for future matches under various scenarios.

### ✨ Key Features

- **IPL Cricket Analysis**: 
  - Focused on IPL T20 cricket (2008-2023)
  - Comprehensive metrics for IPL performance analysis
  - Year-by-year trends and team evolution
  
- **Team Performance Analytics**: 
  - Track wins/losses in different match scenarios (chasing/defending)
  - Analyze performance trends across seasons and venues
  - Identify team strengths in pressure situations (last-ball finishes)
  
- **Player Impact Metrics**: 
  - Batting milestones and consistency tracking
  - Bowling effectiveness in different match phases
  - Match-winning contribution analysis (Man of the Match awards)
  - Clutch performance metrics in high-pressure situations
  
- **Detailed Scenario-Based Predictions**: 
  - Projected scores under optimal conditions
  - Performance forecasting with key player absences
  - Impact of early wickets on final scores
  - Pressure situation performance modeling
  - Weather and pitch condition adjustments
  
- **Interactive Visualizations**: 
  - Generate compelling charts, graphs and tables
  - Track trends and patterns across cricket history
  - Export visualizations for presentations and reports

## 📊 Project Structure

```
OverCast-Cric/
├── data/                  # Data storage directory
│   ├── processed/         # Cleaned and transformed data
│   ├── raw/               # Original source data
│   │   ├── matches/       # Match JSON files
│   │   ├── players/       # Player performance data
│   │   ├── teams/         # Team performance data
│   │   └── weather/       # Weather data for match days
│   └── squads/            # Team squad information
├── notebooks/             # Jupyter notebooks for analysis
│   └── prediction_model.py # Machine learning model for predictions (Python module)
├── scripts/               # Processing and analysis scripts
│   ├── fetch_matches.py   # Scripts to retrieve match data
│   ├── fetch_players.py   # Scripts to retrieve player data
│   ├── fetch_teams.py     # Scripts to retrieve team data
│   ├── fetch_weather.py   # Scripts to retrieve weather data
│   ├── process_pipeline.py # Main data processing pipeline
│   └── test_weather.py    # Unit tests for weather data processing
└── requirements.txt       # Project dependencies
```

## ✨ Current Analytics Capabilities

Our project currently offers analysis in several key areas, with IPL data serving as our initial focus before expanding to all cricket formats:

### 1. Scenario-Based Outcome Analysis

We analyze how teams perform in various match situations:
- Projected scores in optimal conditions vs. actual outcomes
- Impact of losing key batters in early overs
- Performance in clutch situations and pressure moments
- Team-wise wins and losses in last-ball situations
- Win percentage in different match scenarios and conditions

### 2. Last-Ball Finish Analysis

We track teams' performances in nail-biting finishes that go down to the final delivery:
- Team-wise wins and losses in last-ball situations
- Separate metrics for chasing and defending scenarios
- Recent history of last-ball matches for each team
- Detailed analysis of match context and pressure situations
- Win percentage in matches decided on the last ball

### 3. Man of the Match Distribution

We analyze how different players contribute to team success:
- Distribution of Man of the Match awards across teams
- Identifying teams with diverse match-winners vs. teams relying on a few stars
- Yearly analysis of teams with most different players winning match awards
- Correlation between MoM diversity and championship success
- Evolution of match-winner diversity across IPL seasons

### 4. Batters' Milestone & Clutch Analysis

We track batting performance metrics with emphasis on clutch situations:
- Number of 50+ scores by batters (team-wise and player-wise)
- Century counts and conversion rates from 50s to 100s
- Strike rates at different score milestones
- Performance in different phases of innings (Powerplay, Middle, Death)
- Clutch batting analysis in high-pressure situations
- Impact scores that weigh runs based on match situation
- Performance after losing key wickets early

### 5. Weather & Conditions Impact Analysis

We examine how external factors affect match outcomes:
- Match outcomes and total scores under different conditions
- Team strategies and toss decisions based on weather
- Player performances under different conditions
- Historical analysis of rain-affected matches
- Dew factor impact on chasing teams
- Pitch condition influence on team performance

### 6. Franchise Evolution Analysis

We analyze how IPL teams have evolved over the seasons:
- Team performance trends through different IPL seasons
- Strategy shifts across different phases of IPL history
- Player retention impact analysis
- Team auction strategy evaluation

### 7. Data Normalization & Standardization

We handle identity resolution across cricket history:
- Team name normalization for consistent analysis (e.g., Delhi Daredevils → Delhi Capitals)
- Player identity resolution across formats and over time
- Proper aggregation of statistics despite name changes
- Historical continuity for renamed franchises and tournaments

## 🚀 Getting Started

### Prerequisites

- Python 3.7+
- pip (Python package installer)
- IPL match data (JSON format)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/navadeepnaidu7/OverCast-Cric.git
cd OverCast-Cric
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Set up the data directory structure:
```bash
mkdir -p data/raw/matches data/raw/players data/raw/teams data/raw/weather data/processed data/squads
```

4. Place your IPL match data files in the data directory:
```bash
# Example structure for match data
cp /path/to/your/ipl-matches/*.csv data/raw/matches/
```

5. Run the data processing pipeline:
```bash
python scripts/process_pipeline.py
```

### Data Sources

The project works with various IPL cricket data sources:

1. **Match metadata**: CSV files containing detailed match information and results
2. **Player statistics**: IPL player performance data and statistics
3. **Team information**: Team composition and historical performance records
4. **Weather data**: Historical weather information for match days and venues
5. **Pitch reports**: Historical pitch condition data and venue characteristics


## 🎯 Project Vision & Goals

The OverCast-Cric Project aims to create the most comprehensive cricket analytics platform that can:

1. **Predict Detailed Match Scenarios**
   - Forecast scores under optimal conditions for any team
   - Model the impact of losing key batters early in an innings
   - Predict performance in clutch situations (final overs, death bowling)
   - Adjust predictions based on pitch, weather, and match context
   - Generate win probability at any point in the match

2. **Historical IPL Analysis**
   - Analyze IPL evolution across different eras
   - Track team and player performance across seasons
   - Identify trends and pattern changes in IPL cricket
   - Compare team strategies between different IPL seasons

## 🔮 Future Development Goals

The OverCast-Cric team is actively working to expand the project's capabilities:

1. **Enhanced Predictive Models**
   - Implement machine learning models for scenario-based predictions
   - Develop ball-by-ball prediction capabilities
   - Create tournament simulation features with alternative outcomes
   - Incorporate player form, team momentum, and matchup-specific metrics
   - Model "what-if" scenarios for team selection and order changes

2. **Interactive Dashboards**
   - Build web-based visualization tools
   - Develop real-time analytics during live matches
   - Create customizable player and team comparison dashboards
   - Enable parameter-based simulation of match scenarios
   - Live win probability calculator with adjustable parameters

3. **Player Rating Systems**
   - Create comprehensive player rating algorithms across formats
   - Track player evolution across seasons and competitions
   - Predict future player performances in specific conditions
   - Develop fantasy cricket scoring optimization tools
   - Phase-wise performance breakdown (Powerplay, Middle, Death)

4. **Strategic Analysis**
   - Analyze team strategies in different match situations
   - Identify optimal player combinations
   - Recommend tactical approaches for specific opponents
   - Head-to-head matchup analysis for players
   - Pitch and venue-specific strategy recommendations

## 📊 Data Processing Pipeline

Our data processing pipeline consists of several key components:

1. **Data Collection**
   - `fetch_matches.py`: Processes IPL match metadata from CSV files
   - `fetch_players.py`: Collects player statistics from IPL matches
   - `fetch_teams.py`: Gathers team-level information and historical performance
   - `fetch_weather.py`: Obtains weather data for match venues and conditions

2. **Data Processing**
   - `process_pipeline.py`: Main data transformation and feature engineering pipeline
   - Handles team name standardization and player identity resolution
   - Creates match-level feature sets for analysis and prediction
   - Prepares data for cross-format compatibility (T20, ODI, Test)

3. **Analytics & Visualization**
   - Various analysis scripts for specific metrics and scenarios
   - Generates tables, charts and statistical summaries
   - Outputs in multiple formats (CSV, PNG, HTML)
   - Scenario-based visualization for different match situations

4. **Predictive Modeling**
   - `notebooks/prediction_model.py`: ML models for detailed outcome predictions
   - Scenario-based modeling (early wicket impact, clutch situations)
   - Feature importance analysis for different match contexts
   - Model evaluation and performance metrics
   - Confidence intervals for predictions

## 🔧 Technical Features

- **IPL Data Processing**: Framework designed for IPL T20 cricket analysis
- **Team Name Normalization**: Handles team rebranding (e.g., Delhi Daredevils → Delhi Capitals)
- **Edge Cases Handling**:
  - D/L method matches and rain-affected games
  - Super overs and tie-breakers
  - Abandoned and shortened matches
  - Team name changes across seasons
- **Scenario-Based Prediction**:
  - Early wicket impact modeling
  - Different pitch and weather conditions
  - Clutch situation performance analysis
  - Alternative player selection outcomes
- **Statistical Methods**:
  - Time series analysis for performance trends
  - Significance testing for comparative analysis
  - Bayesian inference for performance predictions
  - Monte Carlo simulations for match outcomes

## 🤝 Contributing

Contributions are welcome! Whether you're a cricket enthusiast, data scientist, or developer, there's room for everyone to help improve this project.

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes and commit**:
   ```bash
   git commit -m "Add some feature or fix"
   ```
4. **Push to your branch**:
   ```bash
   git push origin feature/your-feature-name
   ```
5. **Open a Pull Request**

### Current Contribution Needs

- Advanced statistical analysis features
- Improved data visualization capabilities
- Expansion of predictive modeling components
- Additional data sources integration
- Documentation enhancements
- Unit tests and code quality improvements
- Feature requests and bug reports

## 📝 License

This project is licensed under the MIT License. A LICENSE file will be added soon.

## 📬 Contact

For questions or suggestions, please open an issue on GitHub or contact the project maintainers:

- Project Lead: [Navadeep Naidu](mailto:navadeepnaidu7@protonmail.com)

---

<div align="center">
  
### Star ⭐ this repository if you find it useful!
  
</div>

---

*This project is not affiliated with, maintained, authorized, endorsed, or sponsored by the Indian Premier League, the Board of Control for Cricket in India, or any cricket governing body. It uses publicly available data from Cricsheet for analytical purposes.*