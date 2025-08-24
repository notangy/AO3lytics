import json
import requests
from bs4 import BeautifulSoup
import os

from consts import USERS_URL, TIMESTAMP, OUTPUT_DIR, WorkStats, User
from utils import safe_request, extract_work_id


all_works = []

filename = f"{TIMESTAMP}_work_stats.json"
filepath = os.path.join(OUTPUT_DIR, filename)


def get_stats(session):
    """
    AO3 has no publically available API, so we must do things the old fashioned way...
    By going to your own stat page and manually extracting the numbers from the HTML

    All data gathered here is fed into a local database with timestamps
    """

    stats_url = USERS_URL + "/stats?flat_view=true&sort_column=date&year=All+Years"

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
    with open(f"{TIMESTAMP}_user_stats.json", "w", encoding="utf-8") as f:
        json.dump(user.to_dict(), f, indent=4)

    stat_box = stat_soup.find("ul", class_="statistics index group")

    # class=None is a required check; otherwise we only grab the first stat entry
    stat_items = stat_box.find_all("dl", attrs={"class": None})

    for item in stat_items:
        # These are the actual stats for each work

        work_link_elem = item.find("a")
        title = work_link_elem.text

        work_link = work_link_elem.get("href")

        work_id = extract_work_id(work_link)

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

        work = WorkStats(
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

    print(f"[INFO] Stats gathered for {TIMESTAMP}. Now writing to file.")
    # Eventually this info will be pushed to a database, but for now I just want it in a file
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(works_dicts, f, indent=4)
