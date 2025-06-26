from datetime import datetime

# Private information for Exercise Challenge

# DO NOT SHARE THIS FILE
#-------------------------------------------
## Exercise challenge settings
CHALLENGE_NAME          = 'Summer_2025'       # name of the challenge (for the output file)
TOKEN_LOCATION          = 'user_tokens/'    # folder path to save tokens to. End with '/'
INTERMEDIATE_LOCATION   = 'output/'         # folder path to save retrieved/processed data from Strava. Prevents excess API calls. End with '/'

START = int(datetime(2024, 10, 15).timestamp())  # year,month,day
END =   int(datetime(2025, 7, 25).timestamp())
# PERMISSIONS='read_all'  # 'read', 'read_all'  # not used at the moment


## Strava API credentials -  DO NOT SHARE THESE  -
# This is used to access the API Application and is unique per app.
# Note: These do not change after being created.
STRAVA_CLIENT_ID     = 0                                       # eg. "123456"
STRAVA_CLIENT_SECRET = ""   # eg. "0kdg1354ksld0a23nldlsh1asdkb1k3k3"


## 3rd party credentials - not needed unless exporting to these services
# Excel Sheet credentials
# Google Doc credentials







