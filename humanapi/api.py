import requests, os.path, logging, sys, time
from rauth import OAuth2Service
import settings

from datetime import date
try:
    import ujson as json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        import json

class Error(Exception):
    pass
class ValidationError(Error):
    pass
class ServerMethodUnknownError(Error):
    pass
class ServerInvalidParametersError(Error):
    pass
class UnknownExceptionError(Error):
    pass
class RequestTimedOutError(Error):
    pass
class TooManyConnectionsError(Error):
    pass
class ParseExceptionError(Error):
    pass
class InvalidApiKeyError(Error):
    pass
class InvalidAppKeyError(Error):
    pass
class InvalidIPError(Error):
    pass
class InvalidURLError(Error):
    pass
class UserUnknownError(Error):
    pass
class UserDisabledError(Error):
    pass
class UserDoesNotExistError(Error):
    pass
class UserNotApprovedError(Error):
    pass

ROOT = 'https://api.humanapi.co/v1/human'
ERROR_MAP = {
    'ValidationError': ValidationError,
    'ServerError_MethodUnknown': ServerMethodUnknownError,
    'ServerError_InvalidParameters': ServerInvalidParametersError,
    'Unknown_Exception': UnknownExceptionError,
    'Request_TimedOut': RequestTimedOutError,
    'Too_Many_Connections': TooManyConnectionsError,
    'Parse_Exception': ParseExceptionError,
    'Invalid_ApiKey': InvalidApiKeyError,
    'Invalid_AppKey': InvalidAppKeyError,
    'Invalid_IP': InvalidIPError,
    'Invalid_URL': InvalidURLError,
    'User_Unknown': UserUnknownError,
    'User_Disabled': UserDisabledError,
    'User_DoesNotExist': UserDoesNotExistError,
    'User_NotApproved': UserNotApprovedError,
}

logger = logging.getLogger('humanapi')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stderr))

class HumanAPI(object):
    def __init__(self, accessToken=None, debug=False):
        '''Initialize the API client

        Args:
           accessToken (str|None): provide your HumanAPI Access Token.
           debug (bool): set to True to log all the request and response information to
           the "humanapi" logger at the INFO level.  When set to false, it will log at the DEBUG level.
           By default it will write log entries to STDERR
       '''

        # self.session = requests.session()
        if debug:
            self.level = logging.INFO
        else:
            self.level = logging.DEBUG
        self.last_request = None

        if accessToken is None:
            if 'HUMANAPI_ACCESS_TOKEN' in os.environ:
                accessToken = os.environ['HUMANAPI_ACCESS_TOKEN']
            else:
                accessToken = self.read_configs()

        if accessToken is None: raise Error('You must provide a HumanAPI Access Token')
        self.accessToken = accessToken
        global ROOT

        # Profile resources
        self.profile = Profile(self)
        self.human = Human(self)

        # Measurement resources
        self.blood_glucose = BloodGlucose(self)
        self.blood_pressure = BloodPressure(self)
        self.bmi = Bmi(self)
        self.body_fat = BodyFat(self)
        self.heart_rate = HeartRate(self)
        self.height = Height(self)
        self.weight = Weight(self)

        # Periodical resources
        self.activity = Activity(self)
        self.location = Location(self)
        self.sleep = Sleep(self)

        # Other resources
        self.genetic_trait = GeneticTrait(self)

    def call(self, url, params=None):
        '''Actually make the API call with the given params - this should only be called by the namespace methods - use the helpers in regular usage like m.helper.ping()'''
        if params is None: params = {}
        # params['access_token'] = self.accessToken
        params = json.dumps(params)
        self.log('GET  %s%s %s' % (ROOT, url, params))
        start = time.time()
        r = requests.get('%s%s' % (ROOT, url), headers={
            'Authorization':'Bearer ' +self.accessToken,
            'accept': 'application/json',
            'user-agent': 'HumanAPI-Python/1.0.0'
            })
        try:
            remote_addr = r.raw._original_response.fp._sock.getpeername() # grab the remote_addr before grabbing the text since the socket will go away
        except:
            remote_addr = (None, None) #we use two private fields when getting the remote_addr, so be a little robust against errors

        # sys.stdout.write("Response: %s%%   \r" % (r) )
        # sys.stdout.flush()
        response_body = r.text
        complete_time = time.time() - start
        self.log('Received %s in %.2fms: %s' % (r.status_code, complete_time * 1000, r.text))
        self.last_request = {'url': url, 'request_body': params, 'response_body': r.text, 'remote_addr': remote_addr, 'response': r, 'time': complete_time}

        result = json.loads(response_body)
        if r.status_code != requests.codes.ok:
            raise self.cast_error(result)
        return result

    def cast_error(self, result):
        '''Take a result representing an error and cast it to a specific exception if possible (use a generic humanapi.Error exception for unknown cases)'''
        if not 'status' in result or result['status'] != 'error' or not 'name' in result:
            raise Error('We received an unexpected error: %r' % result)

        if result['name'] in ERROR_MAP:
            return ERROR_MAP[result['name']](result['error'])
        return Error(result['error'])

    def read_configs(self):
        '''Try to read the Access Token from a series of files if it's not provided in code'''
        paths = [os.path.expanduser('~/.humanapi.token'), '/etc/humanapi.token']
        for path in paths:
            try:
                f = open(path, 'r')
                accessToken = f.read().strip()
                f.close()
                if accessToken != '':
                    return accessToken
            except:
                pass

        return None

    def log(self, *args, **kwargs):
        '''Proxy access to the humanapi logger, changing the level based on the debug setting'''
        logger.log(self.level, *args, **kwargs)

    def __repr__(self):
        return '<HumanAPI %s>' % self.accessToken


class Profile(object):
    def __init__(self, master):
        self.master = master

    def get(self):
        """Retrive user's profile information

        Args:

        Returns:

        Raises:
        """
        _params = {}
        return self.master.call('/profile', _params)



class Human(object):
    def __init__(self, master):
        self.master = master

    def get(self):
        """
        Returns:
            object. the current health status of a human
        """
        _params = {}
        return self.master.call('/', _params)



class GeneticTrait(object):
    def __init__(self, master):
        self.master = master
        self.resouceUrl = '/genetic/traits'

    def list(self):
        """
        Returns:
            object. the current health status of a human
        """
        _params = {}
        return self.master.call(self.resouceUrl, _params)


"""
Base class for data types that are discrete measurements and occur at a point in time.

"""
class Measurement(object):

    def __init__(self, master, resouceUrl):
        self.master = master
        self.resouceUrl = resouceUrl

    def latest(self):
        _params = {}
        return self.master.call(self.resouceUrl, _params)

    def readings(self):
        _params = {}
        return self.master.call(self.resouceUrl + '/readings', _params)

    def reading(self, id):
        _params = {}
        return self.master.call(self.resouceUrl + '/readings/' + id, _params)

    def daily(self, day=None):
        if day is None:
            day = date.today().isoformat()
        _params = {}
        return self.master.call(self.resouceUrl + '/readings/daily/' + day, _params)


class BloodGlucose(Measurement):
    def __init__(self, master):
        Measurement.__init__(self, master, '/blood_glucose')


class BloodPressure(Measurement):
    def __init__(self, master):
        Measurement.__init__(self, master, '/blood_pressure')


class Bmi(Measurement):
    def __init__(self, master):
        Measurement.__init__(self, master, '/bmi')


class BodyFat(Measurement):
    def __init__(self, master):
        Measurement.__init__(self, master, '/body_fat')


class HeartRate(Measurement):
    def __init__(self, master):
        Measurement.__init__(self, master, '/heart_rate')


class Height(Measurement):
    def __init__(self, master):
        Measurement.__init__(self, master, '/height')


class Weight(Measurement):
    def __init__(self, master):
        Measurement.__init__(self, master, '/weight')




"""
Base class for data types that occur in time periods with a start and end time.

These can be things such as a walk, sleep, or location, that start at a certain time and end at a certain time.
"""
class Periodical(object):

    def __init__(self, master, resouceUrl):
        self.master = master
        self.resouceUrl = resouceUrl

    def list(self):
        _params = {}
        return self.master.call(self.resouceUrl, _params)

    def get(self, id):
        _params = {}
        return self.master.call(self.resouceUrl + '/' + id, _params)

    def daily(self, day=None):
        if day is None:
            day = date.today().isoformat()
        _params = {}
        return self.master.call(self.resouceUrl + '/daily/' + day, _params)

    def summary(self, day=None):
        if day is None:
            day = date.today().isoformat()
        _params = {}
        return self.master.call(self.resouceUrl + '/summary/' + day, _params)

    def summaries(self):
        _params = {}
        return self.master.call(self.resouceUrl + '/summaries', _params)



class Activity(Periodical):
    def __init__(self, master):
        Periodical.__init__(self, master, '/activities')

class Location(Periodical):
    def __init__(self, master):
        Periodical.__init__(self, master, '/locations')

class Sleep(Periodical):
    def __init__(self, master):
        Periodical.__init__(self, master, '/sleeps')

