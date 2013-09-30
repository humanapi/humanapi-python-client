 from os import environ as env

try:
    # OAuth2 client ID and secret
    CLIENT_ID = env['HUMANAPI_ID']
    CLIENT_SECRET = env['HUMANAPI_SECRET']

    # Use client secret as key for signing session cookies
    SECRET_KEY = CLIENT_SECRET

except KeyError:
    raise ImportError(
        'You need to set CLIENT_ID and CLIENT_SECRET in the environment for this app, '
        'e.g `CLIENT_ID=XXXX CLIENT_SECRET=YYYY python app.py`'
    )