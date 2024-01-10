import json
import logging

import pandas as pd
from requests_html import HTMLSession


class ZPSession:
    def __init__(self, login_data: dict):
        """Init for class
        login dictionary is a dict of {"username":"YOUR USERNAME", "password":YOUr PASSWORD"}
        """
        self.login_data = login_data
        self.zp_url = "https://zwiftpower.com"
        self.session = None
        # User Agent required or will be blocked at some apis
        self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"

    def check_status(self):
        if self.session is None:
            return False
        else:
            r = self.session.get(self.zp_url)
            status_code = r.status_code == 200
            login_required = "Login Required" in r.text
            print(f"Status: {status_code} Login Required: {login_required}")
            return bool(status_code and not login_required)

    def login(self):
        s = HTMLSession()
        self.login_data.update({"rememberMe": "on"})
        print(self.login_data)
        s.headers.update({"User-Agent": self.user_agent})
        s.get("https://zwiftpower.com/")
        r2 = s.get("https://zwiftpower.com/ucp.php?mode=login&login=external&oauth_service=oauthzpsso")
        post_url = r2.html.find("form", first=True).attrs["action"]
        print(post_url)

        logging.info(f"Post URL: {post_url}")
        r3 = s.post(post_url, data=self.login_data)
        logging.info(f"Post LOGIN URL: {r3.url}")
        print(f"Post LOGIN URL: {r3.url}")
        try:  # make sure we are logged in
            assert "'https://secure.zwift.com/" not in r3.url
            assert "https://zwiftpower.com/events.php" in r3.url
            assert "invalid username or password." not in r3.text.lower()
        except Exception as e:
            logging.error(f"Failed to login to ZP:\n{e}")
            print(f"Failed to login to ZP(1):\n{e}")
            self.session = None
            return None
        logging.info("Logged in session created")
        self.session = s

    def get_session(self):
        if self.check_status():
            return self.session
        else:
            try:
                self.login()
                return self.session
            except Exception as e:
                logging.error(f"Failed to login to ZP and get session:\n{e}")
                return None

    def get_api(self, id: int | None, api: str) -> json:
        """
        The Api(s) to fetch are based on matching the api to the key in the dict
        """

        if self.get_session():
            self.session.get("https://zwiftpower.com/events.php")
            self.apis = dict(
                team_riders=f"{self.zp_url}/api3.php?do=team_riders&id={id}",
                team_pending=f"{self.zp_url}/api3.php?do=team_pending&id={id}",
                team_results=f"{self.zp_url}/api3.php?do=team_results&id={id}",
                profile_profile=f"{self.zp_url}/cache3/profile/{id}_all.json",
                profile_victims=f"{self.zp_url}/cache3/profile/{id}_rider_compare_victims.json",
                profile_signups=f"{self.zp_url}/cache3/profile/{id}_signups.json",
                all_results=f"{self.zp_url}/cache3/lists/0_zwift_event_list_results_3.json",  # The main events result list
                event_results_view=f"{self.zp_url}/cache3/results/{id}_view.json",  # The results of an event
                event_results_zwift=f"{self.zp_url}/cache3/results/{id}_zwift.json",  # The results of an event
                event_race_history=f"{self.zp_url}/cache3/lists/0_race_history.json",  # The results of an event
            )
            data_set = dict()
            for k, v in self.apis.items():
                if api in k:
                    logging.info(f"Get {k} data from: {v}")
                    print(f"Get {k} data from: {v}")
                    try:
                        raw = self.session.get(v)
                        data = json.loads(raw.text)
                        assert "data" in data
                        data_set[k] = data
                    except Exception as e:
                        logging.error(f"Failed to get data from ZP: {e}\n {raw.text}")
                        data_set[k] = None
            return data_set

    def get_primes_from_url(self, url, cat, format):
        """Get primes for an event
        https://zwiftpower.com/events.php?zid=4073983
        https://zwiftpower.com/api3.php?do=event_primes&zid=4073983&category=B&prime_type=msec
        https://zwiftpower.com/api3.php?do=event_primes&zid=4073983&category=&prime_type=elapsed&_=1704824582380

        """
        if self.get_session():
            self.session.get("https://zwiftpower.com/events.php")
            id = url.split("=")[1]
            event_prime_results = f"{self.zp_url}/api3.php?do=event_primes&zid={id}&category={cat}&prime_type={format}"
            print(event_prime_results)
            raw = self.session.get(event_prime_results)
            print(f"Raw: {raw.text}")
            data = json.loads(raw.text)["data"]
            data = format_prime_data(data)
            df = pd.DataFrame(data)
            return df


def flatten_row(row: dict) -> dict:
    update_row = {}
    for k, v in row.items():
        try:
            if isinstance(v, list) and len(v) == 2:
                update_row[f"{k}"] = v[0]
                update_row[f"{k}_1"] = v[1]
        except:
            print(k, v)
    return update_row


def format_prime_data(data: list) -> dict:
    """Format the prime data to be a list of dicts"""
    primes = []
    for row in data:
        prime_details = {k.replace("name", "prime_name"): v for k, v in row.items() if "rider_" not in k}
        print(prime_details)
        for k, v in row.items():
            if "rider_" in k:
                new_row = {"place": k.split("_")[1]}
                new_row.update(prime_details)
                new_row.update(v)
                primes.append(new_row)

    return primes
