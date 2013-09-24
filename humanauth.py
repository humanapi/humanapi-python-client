from rauth import OAuth2Service
import json

import settings

HumanAuth = OAuth2Service(
    client_id=settings.CLIENT_ID,
    client_secret=settings.CLIENT_SECRET,
    name='humanapi',
    authorize_url='https://user.humanapi.co/oauth/authorize',
    access_token_url='https://user.humanapi.co/oauth/token',
    base_url='https://api.humanapi.co/v1/human/')


# Wrapper functions for building authorize URL and session easily
def get_authorize_url(redirect_uri):
    return HumanAuth.get_authorize_url(
        response_type='code',
        redirect_uri=redirect_uri,
        #optional
        # user='uses@email.com',
        # mode='edit'
    )

def get_auth_session(code, scope=''):
    # retrieve the authenticated session (response is a JSON string, so we need a custom decoder)
    session = HumanAuth.get_auth_session(data={
        'scope': scope,
        'code': code,
    }, decoder=json.loads)

    return session

def recreate_session(access_token):
    return OAuth2Session(
        HumanAuth.client_id,
        HumanAuth.client_secret,
        access_token,
        HumanAuth
    )