import json
import os

from strava_app_settings import INTERMEDIATE_LOCATION
import strava_app_api

user_data_file = INTERMEDIATE_LOCATION + 'users.json'
team_data_file = INTERMEDIATE_LOCATION + 'teams.json'

# Example data structure
# users_data = [
#     {"user_id": "12345", "name": "John Doe", "team": 1},
#     {"user_id": "67890", "name": "Jane Smith", "team": 2},
# ]

# team_data = [
#     {"team": 1, "name": "Team A", "members": ["12345", "67890"]},
#     {"team": 2, "name": "Team B", "members": ["12345", "67890"]},
# ]

def load_user_data():
    """
    Loads user data from the users.json file
    """
    if not os.path.exists(user_data_file):
        return []

    with open(user_data_file, 'r') as f:
        user_data = json.load(f)
    return user_data


def load_team_data():
    """
    Loads team data from the teams.json file
    """
    if not os.path.exists(team_data_file):
        return []
    
    with open(team_data_file, 'r') as f:
        team_data = json.load(f)
    return team_data


def generate_user_data():
    """Adds users to users.json if they are not already in it.
    Function uses 'user_tokens/' list to create user list"""
    # Load existing user data
    user_data = load_user_data()

    # For each token, add to user_data if not already in user_data
    tokens = strava_app_api.get_token_list()
    for token in tokens:
        if token not in [user['user_id'] for user in user_data]:
            user_data.append({"user_id": token, "name": "Unknown", "team": 0})
    
    # Save user_data
    with open(user_data_file, 'w') as f:
        json.dump(user_data, f)


def generate_team_data():
    # Generate team data from users.json (generate_user_data() should be called first)
    users = load_user_data()
    
    # Build a dict for teams keyed by team_id
    team_data = load_team_data()
    teams = {team['team']: team for team in team_data}

    # Build teams dict: {team_id: {"team": team_id, "name": f"Team", "members": [user_ids]}}
    for user in users:
        team_id = user.get("team", 0)
        if team_id == 0:
            continue  # skip users not assigned to a team
        if team_id not in teams:
            teams[team_id] = {
                "team": team_id,
                "name": f"Team {team_id}",
                "members": []
            }
        if user["user_id"] not in teams[team_id]["members"]:
            teams[team_id]["members"].append(user["user_id"])

    # Save to teams.json
    team_data = list(teams.values())
    with open(team_data_file, 'w') as f:
        json.dump(team_data, f, indent=2)

    return team_data
