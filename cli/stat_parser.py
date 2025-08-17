import re
import requests
from bs4 import BeautifulSoup
import time
import os
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv("AO3_USERNAME", "")
PASSWORD = os.getenv("AO3_PASSWORD", "")
DEBUG_MODE = bool(os.getenv("DEBUG_MODE", 0))

base_url = "https://archiveofourown.org"
users_url = base_url + "/users/"

login_url = base_url + "/users/login"

all_works = []

# Each story is a work


class Work:
    def __init__(
        self,
        id,
        title,
        fandoms,
        kudos,
        word_count,
        hits,
        subscriptions,
        bookmarks,
        comment_threads,
    ):
        self.title = title
        self.id = id
        self.age = fandoms
        self.kudos = kudos
        self.word_count = word_count
        self.hits = hits
        self.subscriptions = subscriptions
        self.bookmarks = bookmarks
        self.comment_threads = comment_threads


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

    stat_box = stat_soup.find("ul", class_="statistics index group")

    stat_items = stat_box.findChildren("ul", attrs={"class": "index group"})

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
        )

        child_stats = item.find("dl")
        try:
            sub_count = child_stats.find("dd", attrs={"class": "subscriptions"}).text
        except AttributeError:
            # For when a work doesn't have any subscriptions yet.
            sub_count = 0
            hits = child_stats.find("dd", attrs={"class": "hits"}).text.replace(",", "")
            kudos = child_stats.find("dd", attrs={"class": "kudos"}).text.replace(
                ",", ""
            )
            comment_threads = child_stats.find(
                "dd", attrs={"class": "comments"}
            ).text.replace(",", "")
            bookmarks = child_stats.find(
                "dd", attrs={"class": "bookmarks"}
            ).text.replace(",", "")

        # Get the global stats too.
        # global_statbox = stat_soup.find('dl', attrs={'class': 'statistics meta group'})
        # metrics.ao3_user_threads.set(int(global_statbox.find('dd', attrs={'class': 'comment thread count'}).text.replace(',', '')))
        # metrics.ao3_user_wordcount.set(int(global_statbox.find('dd', attrs={'class': 'words'}).text.replace(',', '')))
        # metrics.ao3_user_hits.set(int(global_statbox.find('dd', attrs={'class': 'hits'}).text.replace(',', '')))
        # #metrics.user_subs.set(int(global_statbox.find('dd', attrs={'class': 'subscriptions'}).text.replace(',', '')))
        # metrics.ao3_user_kudos.set(int(global_statbox.find('dd', attrs={'class': 'kudos'}).text.replace(',', '')))
        # metrics.ao3_user_bookmarks.set(int(global_statbox.find('dd', attrs={'class': 'bookmarks'}).text.replace(',', '')))
        # metrics.ao3_user_global_subs.set(int(global_statbox.find('dd', attrs={'class': 'user subscriptions'}).text.replace(',', '')))

        # Now that we've gathered all the stats of a given work...

        work = Work(
            title,
            work_id,
            fandom,
            kudos,
            word_count,
            hits,
            sub_count,
            bookmarks,
            comment_threads,
        )
        all_works.append(work)


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
