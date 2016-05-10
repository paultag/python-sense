from .cache import Cache
from . import __version__

import datetime as dt
import requests
import time
import os


class Sense(object):
    """
    Hello Sense API Wrapper

    Hello has not created a way to create client_id and client_secret tokens
    yet. I do not wish to publish them without their consent, so I'm afraid
    you'll have to hunt down your own in the wild.

    The Hello Sense API is an OAuth2 REST API, which speaks JSON to the client.
    The data in the app is shown via the API, and the API is very complete,
    but entirely without documentation.

    This is not complete, and is not stable, so please be careful when using
    this.
    """

    def __init__(
        self,
        cache_dir=None,
        client_id=None,
        client_secret=None,
        api_base="https://api.hello.is",
    ):
        self.cache = Cache(base_dir=cache_dir)
        self.client_id = client_id
        self.client_secret = client_secret
        self.api_base = api_base

    def login(self, username, password):
        """
        Log into the Hello Sense API, and store the OAuth2 token into the
        filesystem cache.
        """
        data = self._request("POST", "v1/oauth2/token", data={
            "grant_type": "password",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "username": username,
            "password": password,
        }, auth=False).json()
        self.cache.write("token", data)
        return data

    def timeline(self, when):
        """
        For a given time (such as `2016-04-26`), return the sleep timeline
        for that date.
        """
        return self._request("GET", "v2/timeline", when).json()

    def devices(self):
        """
        Get a list of all connected devices, including Sleep Pills, along
        with associated information, such as serial numbers and battery
        information.
        """
        return self._request("GET", "v2/devices").json()

    def insights(self):
        """
        Get the list of sleep insights tied to your account.
        """
        return self._request("GET", "v2/insights").json()

    def trends(self, duration="LAST_WEEK"):
        """
        Return the trends for a length of time.

        Valid durations are:
            - LAST_WEEK
            - MONTH
            - 3_MONTHS
        """
        return self._request("GET", "v2/trends", duration).json()

    def room_sensors(self, quantity=5):
        """
        Get a list of data readings regarding the room from all sensors on
        the Sense, such as temperature, light and sound.
        """
        from_utc = dt.datetime.utcnow()  # XXX: FIXME
        timestamp = int(time.mktime(from_utc.timetuple())) * 1000
        return self._request("GET", "v1/room/all_sensors/hours", params={
            "quantity": quantity,
            "from_utc": timestamp,
        }).json()

    def room_current(self, temp_unit="c"):
        """
        Get the current sensor readings regarding the room, as well as
        their fitness for sleeping.
        """
        return self._request("GET", "v1/room/current", params={
            "temp_unit": temp_unit,
        }).json()

    def _request(self, method, *resources, auth=True, headers=None, **kwargs):
        """
        Internal wrapper to help make API requests.
        """
        headers = {} if headers is None else headers
        headers['User-Agent'] = "python-sense/{}".format(__version__)

        if auth:
            token = self.cache.get("token")
            if token is None:
                raise ValueError("Not logged in")
            headers["Authorization"] = "Bearer {}".format(token["access_token"])

        resp = requests.request(
            method,
            self._endpoint(*resources),
            headers=headers,
            **kwargs
        )
        if (resp.status_code // 100) != 2:
            raise ValueError("Non-200 return code!")
        return resp

    def _endpoint(self, *resource):
        """
        Construct a Sense API endpoint.
        """
        return os.path.join(self.api_base, *resource)
