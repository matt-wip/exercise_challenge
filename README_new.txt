
# Fitness Challenge App

## Requires python and pandas
## Optional: google, excel
PYTHON 3.10+

Powered by Strava

## SETUP

1. Create new Strava API App and fillout "app_settings.py"
Follow the below link
https://medium.com/swlh/using-python-to-connect-to-stravas-api-and-analyse-your-activities-dummies-guide-5f49727aac86


3. Test - Strava API App with your own credentials

4. Get others to sign up! Send this to people
    You need to update the below URL with your Strava Client ID for your App. (STRAVA_CLIENT_ID in settings.py)
    # Example of clicking link:
    https://www.strava.com/oauth/authorize?client_id=164452&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=profile:read_all,activity:read_all

    # Then they update this link
    #http://localhost/exchange_token?state=&code=82f80d1d03c4f700d1e7bd354df16e0e13da0725&scope=read,activity:read_all,profile:read_all

*** BE SURE TO ADD THEIR AUTHENTICATION TOKENS!!! ***
Run "strava_app_api.py" --> save_user_token(user_id, user_code)
Don't be afraid to run it again, the function does not overwrite existing files
The list of tokens is written to "user_tokens/". All of this strava_app behavior is centered around this.
User not appearing? Check if token exists for them or not working

Optional: get automatic script Setup or write Python script to import lists

5. 
## How it works? Data processing flow 
1) Get others to sign up with API link and add their tokens to 'user_tokens'
  Either by hand or script - call 'strava_app_api.save_user_token("user_id", "user_code")