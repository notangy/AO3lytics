from login_client import login
from stat_parser import get_stats
from bookmark_savior import get_bookmarks
import requests
import time


from consts import USERNAME


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
        # get_stats(session)
        print(f"[INFO] Statistics gathered for {USERNAME}.")
        time.sleep(5)
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
