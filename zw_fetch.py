import json
import logging

import pandas as pd
import requests

from utils import flatten_dict

# Add a console logger
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", handlers=[logging.StreamHandler()]
)

# from . import zwift_messages_pb2

"""
membership status: https://us-or-rly101.zwift.com/api/profiles/12345/membership-status
me: https://us-or-rly101.zwift.com/api/profiles/me
my_clubs: https://us-or-rly101.zwift.com/api/clubs/club/list/my-clubs?
goals: https://us-or-rly101.zwift.com/api/profiles/12345/goals
activity feed ALL: https://us-or-rly101.zwift.com/api/activity-feed/feed/?limit=30&includeInProgress=false&feedType=FOLLOWEES
activity feed favorites: https://us-or-rly101.zwift.com/api/activity-feed/feed/?limit=30&includeInProgress=false&feedType=FAVORITES
activity feed just me: https://us-or-rly101.zwift.com/api/activity-feed/feed/?limit=30&includeInProgress=false&feedType=JUST_ME
power_profile: https://us-or-rly101.zwift.com/api/power-curve/power-profile
"""

API_OPTIONS = [
    "Me",
    "not implemented: Membership Status",
    "My Clubs",
    "not implemented: Goals",
    "Activity Feeds (partial)",
    "not implemented: Activity Feed ALL",
    "not implemented: Activity Feed FAVORITES",
    "not implemented: Activity Feed JUST ME",
    "Power Profile",
    "not implemented: Download fit",
    "not implemented: Download fit as csv",
    "not implemented: Analyze activity fit",
    "Event",
    "Event Results",
]


def zwprofile(username, password):
    try:
        get_token = requests.get(
            f"https://z00pbp8lig.execute-api.us-west-1.amazonaws.com/latest/zwiftId?username={username}&pw={password}"
        )
        return get_token.json()
    except Exception as e:
        logging.error(e)


class BaseZwiftAPIClientException(Exception):
    pass


class ZwiftAPIResponseException(BaseZwiftAPIClientException):
    def __init__(self, status_code, reason, response):
        self.args = status_code, reason, response.text
        self.status_code = status_code
        self.reason = reason
        self.response = response


class ZwiftAPIClient:
    FIT_FILE_PATTERN = "https://{bucket_name}.s3.amazonaws.com/{file_key}"
    auth_url = "/auth/realms/zwift/tokens/access/codes"
    headers = {"User-Agent": "Zwift/115 CFNetwork/758.0.2 Darwin/15.0.0"}
    auth_info = None
    session = None
    # username = None
    # password = None

    def __init__(
        self,
        username: str,
        password: str,
        secure_server_url="https://secure.zwift.com",
        api_server_url="https://us-or-rly101.zwift.com",
    ):
        self.secure_server_url = secure_server_url
        self.api_server_url = api_server_url
        self.username = username
        self.password = password

    def abs_url(self, endpoint):
        return "{0}/{1}".format(self.api_server_url.rstrip("/"), endpoint.lstrip("/"))

    @staticmethod
    def get_json(response):
        if not response.ok:
            raise ZwiftAPIResponseException(response.status_code, response.reason, response)
        return response.json()

    @staticmethod
    def get_proto(response, proto_class):
        if not response.ok:
            raise ZwiftAPIResponseException(response.status_code, response.reason, response)
        proto_object = proto_class()
        proto_object.ParseFromString(response.content)
        return proto_object

    def authenticate(self) -> json:
        data = {
            "username": self.username,
            "password": self.password,
            "client_id": "Zwift_Mobile_Link",
            "grant_type": "password",
        }
        self.session = requests.Session()
        abs_auth_url = "{0}/{1}".format(self.secure_server_url.rstrip("/"), self.auth_url.lstrip("/"))
        headers = self.make_headers(extra_headers={"Accept": "application/json"}, auth=False)
        response = self.session.post(abs_auth_url, headers=headers, data=data)
        res = self.get_json(response)
        self.auth_info = res
        return self.auth_info

    def re_authenticate(self):
        return self.authenticate()

    @property
    def is_authenticated(self):
        return True if (self.auth_info and self.auth_info.get("access_token")) else False

    def make_headers(self, extra_headers=None, auth=True):
        headers = self.headers.copy()
        if auth:
            access_token = self.auth_info and self.auth_info.get("access_token")
            assert access_token, "Authentication required!"
            token = f"Bearer {access_token}"
            headers.update({"Authorization": token})
        headers.update(extra_headers or {})
        return headers

    def download_file(self, url, raw_response=False, auth=False, **kwargs):
        headers = self.make_headers(auth=auth)
        response = requests.get(url, headers=headers)
        if not raw_response:
            if not response.ok:
                raise ZwiftAPIResponseException(response.status_code, response.reason, response)
            response = response.content
        return response

    def json_request(self, endpoint, method="get", headers=None, raw_response=False, auth=True, **kwargs):
        if not self.is_authenticated:
            self.re_authenticate()
        method = method.lower()
        assert method in ("get", "put", "post", "delete")
        extra_headers = {"Accept": "application/json"}
        extra_headers.update(headers or {})
        headers = self.make_headers(extra_headers=extra_headers, auth=auth)

        func = getattr(requests, method)
        response = func(self.abs_url(endpoint), headers=headers, **kwargs)
        if not raw_response:
            response = self.get_json(response)
        return response

    def proto_request(self, proto_class, endpoint, method="get", headers=None, raw_response=False, auth=True, **kwargs):
        method = method.lower()
        assert method in ("get", "put", "post", "delete")
        extra_headers = {"Accept": "application/x-protobuf-lite"}
        extra_headers.update(headers or {})
        headers = self.make_headers(extra_headers=extra_headers, auth=auth)

        func = getattr(requests, method)
        response = func(self.abs_url(endpoint), headers=headers, **kwargs)
        if not raw_response:
            response = self.get_proto(response, proto_class)
        return response

    # def get_player_status(self, zwid, world=1, params=None, **kwargs):
    #     if params:
    #         kwargs["params"] = params
    #     res = self.proto_request(zwift_messages_pb2.PlayerState, f"/relay/worlds/{world}/players/{zwid}", **kwargs)
    #     return json_format.MessageToDict(res)

    def get_players(self, world=1, params=None, **kwargs):
        if params:
            kwargs["params"] = params
        return self.json_request(f"/relay/worlds/{world}", **kwargs)

    def get_profile(self, zwid_or_public_id="me", **kwargs):
        return self.json_request(f"/api/profiles/{zwid_or_public_id}", **kwargs)

    def get_power_profile(self):
        """
        power_profile: https://us-or-rly101.zwift.com/api/power-curve/power-profile
        :return:
        """
        return self.json_request("/api/power-curve/power-profile")

    def get_profile_followees(self, zwid, params=None, **kwargs):
        if params:
            kwargs["params"] = params
        return self.json_request(f"/api/profiles/{zwid}/followees", **kwargs)

    def get_profile_followers(self, zwid, params=None, **kwargs):
        if params:
            kwargs["params"] = params
        return self.json_request(f"/api/profiles/{zwid}/followers", **kwargs)

    def get_profile_links(self, zwid, params=None, **kwargs):
        if params:
            kwargs["params"] = params
        return self.json_request(f"/api/profiles/{zwid}/link", **kwargs)

    def get_activities(self, zwid, params=None, **kwargs):
        """
            activity feed ALL: https://us-or-rly101.zwift.com/api/activity-feed/feed/?limit=30&includeInProgress=false&feedType=FOLLOWEES
        activity feed favorites: https://us-or-rly101.zwift.com/api/activity-feed/feed/?limit=30&includeInProgress=false&feedType=FAVORITES
        activity feed just me: https://us-or-rly101.zwift.com/api/activity-feed/feed/?limit=30&includeInProgress=false&feedType=JUST_ME
            :param params: allowed request query parameters are:
                - start = pagination start index
                - limit = pagination page size
                - fetchRideons = true|false
                - name = ALL|JUST_ME|FAVORITES
                - component = ?
                - includeSelf = true|false
                - includeFollowees = true|false
                - includeInProgress = true|false
                - before = unix timestamp to query before this time
                - after = unix timestamp to query after this time
        """
        if params:
            kwargs["params"] = params
        return self.json_request(f"/api/profiles/{zwid}/activities", **kwargs)

    def get_activity(self, zwid, activity_id, **kwargs):
        return self.json_request(f"/api/profiles/{zwid}/activities/{activity_id}", **kwargs)

    def get_activity_file(self, zwid, activity, **kwargs):
        if not isinstance(activity, dict):
            activity = self.get_activity(zwid, activity)
        fit_file_bucket = activity["fitFileBucket"]
        fit_file_key = activity["fitFileKey"]
        fit_file_url = self.FIT_FILE_PATTERN.format(bucket_name=fit_file_bucket, file_key=fit_file_key)
        return self.download_file(fit_file_url, **kwargs)

    def get_activity_rideon(self, zwid, activity_id, **kwargs):
        return self.json_request(f"/api/profiles/{zwid}/activities/{activity_id}/rideon", **kwargs)

    def add_activity_rideon(self, zwid, activity_id, profile_id, **kwargs):
        return self.json_request(
            f"/api/profiles/{zwid}/activities/{activity_id}/rideon", method="post", json={"profileId": profile_id}
        )

    def get_events_upcoming(self, params=None, **kwargs):
        if params:
            kwargs["params"] = params
        if "auth" not in kwargs:
            kwargs["auth"] = False
        return self.json_request("/api/public/events/upcoming", **kwargs)

    def get_event(self, event_id, **kwargs):
        return self.json_request(f"/api/events/{event_id}", **kwargs)

    def get_private_events_feed(self, params=None, **kwargs):
        if params:
            kwargs["params"] = params
        return self.json_request("/api/private_event/feed", **kwargs)

    def get_private_event(self, event_id, **kwargs):
        return self.json_request(f"/api/private_event/{event_id}", **kwargs)

    def get_event_subgroup_results(self, id, params=None, **kwargs):
        """id: subgroup id"""
        if params:
            kwargs["params"] = params
        return self.json_request(f"/api/race-results/entries?event_subgroup_id={id}", **kwargs)

    def get_my_clubs(self, params=None, **kwargs):
        """my_clubs: https://us-or-rly101.zwift.com/api/clubs/club/list/my-clubs?"""
        if params:
            kwargs["params"] = params
        return self.json_request("/api/clubs/club/list/my-clubs", **kwargs)


if __name__ == "__main__":
    import os

    from dotenv import load_dotenv

    load_dotenv()
    world = 1
    c = ZwiftAPIClient(os.getenv("zw_user"), os.getenv("zw_pass"))
    c.authenticate()
    event_ids = [4123413, 4123432]
    for event in event_ids:
        event_json = c.get_event(4123413)
        with open(f"event_id_{event}.json", "w") as j:
            json.dump(event_json, j, indent=4)
        eventSubgroups_ids = [sg_id["id"] for sg_id in event_json["eventSubgroups"]]
        print(f"Subgroup ids: {eventSubgroups_ids}")
        print("###########")
        for sg_id in eventSubgroups_ids:
            results_json = c.get_event_subgroup_results(5137507)["entries"]
            with open(f"event_{event}_subgroup_id_{sg_id}.json", "w") as j:
                json.dump(results_json, j, indent=4)
            results = [flatten_dict(row) for row in results_json]
            pd.DataFrame(results).to_csv(f"event_{event}_subgroup_id_{sg_id}.csv")
