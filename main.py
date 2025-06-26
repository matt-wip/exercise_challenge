import strava_app_api
import strava_app_scoring as scorer
import strava_app_team as teams
from strava_app_settings import INTERMEDIATE_LOCATION
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def process_user(token):
    """Process a single user's data and return the UserEC object or None if failed."""
    try:
        user_ec = scorer.UserEC(token)
        if user_ec.calculate_points():
            return user_ec
        else:
            print(f"Error obtaining Strava data for user {token}")
            return None
    except Exception as e:
        print(f"Exception processing user {token}: {e}")
        return None

def main():
    # Get Exercise Challenge users from token files
    # Any users not in the token list will be skipped
    token_list = strava_app_api.get_token_list()
    if not token_list:
        print("No tokens found. Please check saved token files. Exiting...")
        return

    # Process each user's activities and calculate their points
    user_results = []
    max_workers = min(10, len(token_list))  # Thread pool size
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_token = {executor.submit(process_user, token): token for token in token_list}
        
        # Collect results as they complete
        for future in as_completed(future_to_token):
            token = future_to_token[future]
            try:
                user_ec = future.result()
                if user_ec:
                    user_results.append(user_ec)
            except Exception as e:
                print(f"Exception for user {token}: {e}")
    
    if not user_results:
        print("No Strava data retrieved. Exiting...")
        return
    
    # Convert to DataFrame, sort by points, add user rankings
    df = scorer.create_dataframe_from_users(user_results)
    df = df.sort_values('Total_Points', ascending=False).reset_index(drop=True)
    df['Rank'] = df.index + 1

    # Calculate team points and rankings
    teams.generate_user_data()
    if input("Please manually update team assignments in 'users.json'.\n"
             "Proceed with generating team stats? (y/n): ").lower() == "y":
        # Calculate team statistics using the new function
        team_stats = teams.calculate_team_statistics(df)
        teams.save(team_stats, "team_rankings.csv")

    # Save to file
    # TODO: save to google sheet or excel
    df.to_csv(INTERMEDIATE_LOCATION + 'user_rankings.csv', index=False)
   
    print("Strava App Complete")

# CLI
if __name__=="__main__":
    main()