import argparse
from login_client import login
from stat_parser import get_stats
from bookmark_savior import get_all_bookmarks
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

    parser = argparse.ArgumentParser(
        description="Helper tool for gathering personal AO3 stats!"
    )
    parser.add_argument(
        "--skip_stats",
        help="Use this if you want to skip gathering statistics",
        action="store_true",
    )
    parser.add_argument(
        "--skip_bookmarks",
        help="Use this if you want to skip gathering bookmarks",
        action="store_true",
    )

    args = parser.parse_args()

    try:
        session = requests.Session()
        login(session)
        if not args.skip_stats:
            get_stats(session)
            print(f"[INFO] Statistics gathered for {USERNAME}.")
            time.sleep(5)
        if not args.skip_bookmarks:
            get_all_bookmarks(session)
            print(f"[INFO] Bookmarks gathered for {USERNAME}.")
        print(f"[INFO] All done!")
        exit(0)
    except RuntimeError:
        # Throw an error and quit.
        print("[ERROR] Login failed! Your creds might be wrong :/")
        exit(1)
    except requests.exceptions.RequestException:
        # AO3 likely experiencing issues
        print(
            "[ERROR] AO3 is experiencing issues! Check if it's down before trying again!"
        )
        exit(1)
