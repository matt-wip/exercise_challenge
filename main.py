import json
import pandas as pd
from typing import List, Dict, Any

import strava_app_api
import strava_app_scoring as scorer
import strava_app_team as teams

# For testing purposes. Put your own info in here:
#temp_userid = 85915778
#temp_code = "d2a0727934c004d3adafb80847918b3dc64a99d7"
#temp_act = 'temp_activites.json'

def main():
    # Get users
    token_list = strava_app_api.get_token_list()
    token_count = len(token_list)
    print(f"Found {token_count} tokens to process")
    if not token_count:
        return

    # Collect all user results
    user_results = []
    for token in token_list:
        user_ec = scorer.UserEC(token)
        user_ec.calculate_points()
        if user_ec._has_points:  # Check if processing was successful
            user_results.append(user_ec)
        else:
            print(f"Error calculating points for user {token}")
    
    # Convert to DataFrame 
    df = scorer.create_dataframe_from_users(user_results)
    print(f"Processed {len(df)} users")

    # Sort by points and add ranks
    df = df.sort_values('Total_Points', ascending=False).reset_index(drop=True)
    df['Rank'] = df.index + 1

    # Calculate team points and rankings
    teams.generate_user_data()
    if input("Please manually update team assignments in 'output/users.json'.\n"
             "Proceed with generating team stats? (y/n): ").lower() == "y":
        # Generate team data 
        user_data = teams.load_user_data()
        for user in user_data:
            df.loc[df['User_ID'] == user['user_id'], 'Name'] = user['name']
            df.loc[df['User_ID'] == user['user_id'], 'Team'] = user['team']

        team_data = teams.generate_team_data()
        min_members = min(len(team['members']) for team in team_data)

        # Team #, Name, MemberCount, ALL_Ave_Rank, XC_Ave_Rank 
        team_stats = []
        for team in team_data:
            member_rank = df[df['Team'] == team['team']]['Rank'].sort_values()
            ave_rank = member_rank.mean()
            xc_rank  = member_rank.head(min_members).mean()
            team_stats.append([team['team'], team['name'], len(team['members']), ave_rank, xc_rank, min_members])
            
        team_stats = pd.DataFrame(team_stats, columns=['Team', 'Name', 'MemberCount', 'ALL_Ave_Rank', 'XC_Ave_Rank', 'Min_Team_Size'])
        team_stats = team_stats.sort_values('XC_Ave_Rank').reset_index(drop=True)
        
        team_stats.to_csv('output/team_rankings.csv', index=False)

    # Save to file
    #df.to_csv('output/user_rankings.csv', index=False)
   
    print("DONE")

# CLI
if __name__=="__main__":
    main()