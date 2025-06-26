import json
import os
import time
import requests

import strava_app_settings

"""
Module for:
1) Strava API token handling
2) Strava API data retrieving
"""

# Make Strava auth API call with your: client_code, client_secret, user_id, and user_code
token_save_location = strava_app_settings.TOKEN_LOCATION
client_id =     str(strava_app_settings.STRAVA_CLIENT_ID)
client_secret = str(strava_app_settings.STRAVA_CLIENT_SECRET)


def get_user_path(user_id: str) -> str:
    """
    Return token path for user_id if it exists
    Returns None if no file found
    """
    path = token_save_location + f"strava_tokens_{user_id}.json"
    if not os.path.exists(path):
        return None
    return path


def get_token_list():
    """
    Returns list of token/user ids based on files in token save location
    """
    token_files = [f for f in os.listdir(token_save_location) if f.startswith("strava_tokens_")]
    return [f.rsplit('.')[0].rsplit('_')[-1] for f in token_files]


def save_user_token(user_id: str, user_code: str, overwrite=False) -> bool:
    """
    Requests user_id token and saves it to a file
    Note: skips if token file already exists
    @param user_id str Strava ID for user
    @param user_code str Strava user code for this App
    @param overwrite bool True to force file save
    @return bool True if token exists or token saved. False otherwise. 
        Note: overwrite=True will ignore check for file
    """
    user_file = get_user_path(user_id);
    if (not overwrite) and user_file:
        return True

    response = requests.post(
                        url='https://www.strava.com/oauth/token',
                        data={
                              'client_id': client_id,
                              'client_secret': client_secret,
                              'code': user_code,
                              'grant_type': 'authorization_code'
                              },
                        timeout=20,
                        )
    if response.ok:
        strava_tokens = response.json()
        path = token_save_location + f"strava_tokens_{user_id}.json"
        with open(path, 'w') as outfile:
            json.dump(strava_tokens, outfile)
    else:
        print(f"Error requesting {user_id}'s token.")

    return response.ok


def get_user_token(user_id: str) -> str:
    """
    Retrieves user access token and refreshes saved token if need be
    None if file does not exist or error refreshing/retrieving token
    """
    user_token_path = get_user_path(user_id)
    if not user_token_path:
        return None
    
    # Get the tokens from file to connect to Strava
    token = None
    with open(user_token_path) as token_file:
        token = json.load(token_file)

    # Check if token expired and refresh it
    if token['expires_at'] < time.time():
        # Make Strava auth API call with current refresh token
        response = requests.post(
            url='https://www.strava.com/oauth/token',
            data={
                'client_id': client_id,
                'client_secret': client_secret,
                'grant_type': 'refresh_token',
                'refresh_token': token['refresh_token']
            }
        )

        if response.ok:
            token = response.json()
            with open(user_token_path, 'w') as outfile:
                json.dump(token, outfile)
        else:
            print(f"Error refreshing {user_id}'s token.")
            return None

    return token['access_token']


def get_user_activities(user_id:str):
    """
    Retrieves user Strava activities from Challenge start and stop dates
    """
    user_token = get_user_token(user_id)
    if not user_token:
        return False

    strava_url = "https://www.strava.com/api/v3/activities"
    strava_params = {
        'access_token'  : user_token,
        'per_page'      : '200',
        'page'          : '1',
        'before'        : str(strava_app_settings.END),
        'after'         : str(strava_app_settings.START),
    }

    activities_req = requests.get(url=strava_url, params=strava_params)
    
    if not activities_req.ok:
        print(f"Failed to retrieve {user_id}'s data")
        return False

    return activities_req.json()