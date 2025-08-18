import requests
from bs4 import BeautifulSoup

from dataclasses import dataclass, asdict

from consts import USERS_URL

from utils import safe_request

# Like stat parser, but it saves bookmarks :D
# If a work is deleted from the source, this will at least hold details about what was there.

all_bookmarks = []

MAX_PAGES = 3


@dataclass
class Bookmark:
    id: str
    title: str
    fandoms: list

    relationships: list
    characters: list
    tags: list

    summary: str
    current_chapters: int
    language: str
    word_count: int

    # Convert object list to dict for json export
    def to_dict(self):
        data = asdict(self)
        return data

    """
    This one will require some rate-limiting handling...
    If you have many bookmarks, we'll only try to grab the first three pages by default. To increase this limit, change the variable MAX_PAGES
    """


def get_bookmarks(session):

    bookmarks_url = USERS_URL + "/bookmarks"

    bookmarks_request = safe_request(session, bookmarks_url)

    if bookmarks_request.status_code != 200:
        raise requests.exceptions.RequestException("AO3 is experiencing issues!")

    bookmark_soup = BeautifulSoup(bookmarks_request.text, "lxml")

    current_page = 1
    next_page = False

    # If the 'Next' button is a link, more than one page exists
    if bookmark_soup.find("a", string="Next"):
        next_page = True

    print(next_page)
    # save bookmarks to file
    # print(f"[INFO] Bookmarks gathered. Now writing to file.")
    # with open(f"./stat_output/{TIMESTAMP}_bookmarks.json", "w", encoding="utf-8") as f:
    #     json.dump(all_bookmarks.to_dict(), f, indent=4)
