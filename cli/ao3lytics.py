import os
from login_client import login
from stat_parser import get_stats
from bookmark_savior import get_bookmarks
import requests
import time


USERNAME = os.getenv("AO3_USERNAME", "")

BASE_URL = "https://archiveofourown.org"

USERS_URL = BASE_URL + "/users/" + USERNAME


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


if __name__ == "__main__":

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
        print(f"[INFO] Statistics gathered for {USERNAME}.")
        get_bookmarks(session)
        print(f"[INFO] Bookmarks gathered for {USERNAME}.")
        print(f"[INFO] All done!")
        exit(0)
    except RuntimeError:
        # Throw an error and quit.
        print("Login failed! Your creds might be wrong :/")
        exit(1)
    except requests.exceptions.RequestException:
        # AO3 likely experiencing issues
        print("AO3 is experiencing issues! Check if it's down before trying again!")
        exit(1)
