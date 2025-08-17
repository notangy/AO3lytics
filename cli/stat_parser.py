import json
import re
import requests
from bs4 import BeautifulSoup
import time
import os
from dotenv import load_dotenv
from dataclasses import dataclass, asdict

load_dotenv()

USERNAME = os.getenv("AO3_USERNAME", "")
PASSWORD = os.getenv("AO3_PASSWORD", "")
DEBUG_MODE = bool(os.getenv("DEBUG_MODE", 0))

base_url = "https://archiveofourown.org"
users_url = base_url + "/users/"

login_url = base_url + "/users/login"

all_works = []

# used for adding timestamp to file names
timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")


# Each story is a work
@dataclass
class Work:
    id: str
    title: str
    fandoms: list
    kudos: int
    word_count: int
    hits: int
    subscriptions: int
    bookmarks: int
    comment_threads: int

    # Convert object list to dict for json export
    def to_dict(self):
        data = asdict(self)
        return data


# save global stats here
@dataclass
class User:
    user_subscriptions: int
    kudos: int
    comment_threads: int
    bookmarks: int
    subscriptions: int
    word_count: int
    hits: int

    def to_dict(self):
        data = asdict(self)
        return data


# Built in retries & backoff
def safe_request(
    session,
    url,
    max_retries=3,
    method="GET",
    data=None,
    backoff=5,
):
    for attempt in range(1, max_retries + 1):
        try:
            if method.upper() == "GET":
                response = session.get(url)
            elif method.upper() == "POST":
                response = session.post(url, data=data)
            else:
                raise ValueError("Unsupported method: only 'GET' or 'POST' allowed")

            response.raise_for_status()  # Raises HTTPError for bad responses
            return response

        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt} failed: {e}")
            # Reset session after failure
            session.close()
            session = requests.Session()
            time.sleep(backoff**attempt)

    print("All retries failed.")
    return None


def login(session):

    request = safe_request(session, login_url)

    # html of login page
    login_soup = BeautifulSoup(request.text, features="html.parser")
    auth_token = login_soup.find("input", {"name": "authenticity_token"})["value"]

    print("[INFO] Attempting login...")

    login_attempt = safe_request(
        session,
        login_url,
        method="POST",
        data={
            "authenticity_token": auth_token,
            "user[login]": USERNAME,
            "user[password]": PASSWORD,
        },
    )

    time.sleep(2)  # Give AO3 time to load

    if login_attempt.status_code != 200:
        raise requests.exceptions.RequestException("AO3 is experiencing issues!")
    if "Please try again" in login_attempt.text:
        raise RuntimeError("Error logging in - wrong username and password.")

    print("[INFO] Login successful!")


def get_stats(session):
    """
    AO3 has no publically available API, so we must do things the old fashioned way...
    By going to your own stat page and manually extracting the numbers from the HTML

    All data gathered here is fed into a local database with timestamps
    """

    stats_url = (
        users_url + USERNAME + "/stats?flat_view=true&sort_column=date&year=All+Years"
    )

    stats_request = safe_request(session, stats_url)

    if stats_request.status_code != 200:
        raise requests.exceptions.RequestException("AO3 is experiencing issues!")

    # using lxml for faster parsing
    stat_soup = BeautifulSoup(stats_request.text, "lxml")

    # Global stats handled here

    global_statbox = stat_soup.find("dl", attrs={"class": "statistics meta group"})
    user_threads = global_statbox.find(
        "dd", attrs={"class": "comment thread count"}
    ).text.replace(",", "")
    user_wordcount = global_statbox.find("dd", attrs={"class": "words"}).text.replace(
        ",", ""
    )
    user_hits = global_statbox.find("dd", attrs={"class": "hits"}).text.replace(",", "")
    user_subs = global_statbox.find(
        "dd", attrs={"class": "subscriptions"}
    ).text.replace(",", "")
    user_kudos = global_statbox.find("dd", attrs={"class": "kudos"}).text.replace(
        ",", ""
    )
    user_bookmarks = global_statbox.find(
        "dd", attrs={"class": "bookmarks"}
    ).text.replace(",", "")
    global_subs = global_statbox.find(
        "dd", attrs={"class": "user subscriptions"}
    ).text.replace(",", "")

    user = User(
        global_subs,
        user_kudos,
        user_threads,
        user_bookmarks,
        user_subs,
        user_wordcount,
        user_hits,
    )

    # save user stats to file
    with open(f"{timestamp}_user_stats.json", "w", encoding="utf-8") as f:
        json.dump(user.to_dict(), f, indent=4)

    stat_box = stat_soup.find("ul", class_="statistics index group")

    # class=None is a required check; otherwise we only grab the first stat entry
    stat_items = stat_box.findChildren("dl", attrs={"class": None})

    for item in stat_items:
        # These are the actual stats for each work

        work_id = ""  # placeholder value: we need to extract it from the work URL

        work_link_elem = item.find("a")
        title = work_link_elem.text

        work_link = work_link_elem.get("href")

        # Match the work ID after /works/ in the URL
        match = re.search(r"/works/(\d+)", work_link)
        if match:
            work_id = match.group(1)

        fandom = (
            item.find("span", attrs={"class": "fandom"})
            .text.replace("(", "")
            .replace(")", "")
        )

        word_count = (
            item.find("span", attrs={"class": "words"})
            .text.replace("(", "")
            .replace("words)", "")
            .replace(",", "")
            .strip()
        )

        child_stats = item.find("dl")

        try:
            sub_count = child_stats.find("dd", attrs={"class": "subscriptions"}).text
        except AttributeError:
            # For when a work doesn't have any subscriptions yet.
            sub_count = 0

        hits = child_stats.find("dd", attrs={"class": "hits"}).text.replace(",", "")
        kudos = child_stats.find("dd", attrs={"class": "kudos"}).text.replace(",", "")
        comment_threads = child_stats.find(
            "dd", attrs={"class": "comments"}
        ).text.replace(",", "")
        bookmarks = child_stats.find("dd", attrs={"class": "bookmarks"}).text.replace(
            ",", ""
        )

        # Now that we've gathered all the stats of a given work...

        work = Work(
            work_id,
            title,
            fandom,
            kudos,
            word_count,
            hits,
            sub_count,
            bookmarks,
            comment_threads,
        )
        all_works.append(work)

    works_dicts = [work.to_dict() for work in all_works]

    # Eventually this info will be pushed to a database, but for now I just want it in a file
    with open(f"{timestamp}_work_stats.json", "w", encoding="utf-8") as f:
        json.dump(works_dicts, f, indent=4)


if __name__ == "__main__":

    # Keep track of whether the last result was a failure or not (prevent login blocking)
    previous_error = False

    print(
        """
    =================
          
    ▄▖▄▖▄▖▖ ▖▖▄▖▄▖▄▖▄▖
    ▌▌▌▌▄▌▌ ▌▌▐ ▐ ▌ ▚ 
    ▛▌▙▌▄▌▙▖▐ ▐ ▟▖▙▖▄▌
          
    =================
                       
        """
    )
    try:
        session = requests.Session()
        login(session)
        get_stats(session)
        if previous_error is True:
            print("AO3 back up! Got stats and resuming normal functions.")
            previous_error = False
            if DEBUG_MODE is True:
                print("Got stats! Sleeping 30 minutes...")
            time.sleep(1800)
    except RuntimeError:
        # Throw an error and quit.
        print("Login failed! Your creds might be wrong :/")
        exit(1)
    except requests.exceptions.RequestException:
        # AO3 likely experiencing issues. Sleep, but not as long so that stats update in a timely
        # fashion when it comes back.
        print(
            "AO3 is experiencing issues! Backing off for a while... We'll check again in 10 minutes."
        )
        previous_error = True
