from os import environ as env

try:
    # OAuth2 client ID and secret
    CLIENT_ID = env['CLIENT_ID']
    CLIENT_SECRET = env['CLIENT_SECRET']

    # Just use client secret as key for signing session cookies
    SECRET_KEY = CLIENT_SECRET

except KeyError:
    print 'You need to set CLIENT_ID and CLIENT_SECRET in the environment for this app'
    print 'e.g `CLIENT_ID=XXXX CLIENT_SECRET=YYYY python app.py`'
    exit(1)

