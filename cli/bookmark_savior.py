import json
import re
import requests
from bs4 import BeautifulSoup
import time
import os
from dataclasses import dataclass, asdict

from ao3lytics import USERS_URL, safe_request

# Like stat parser, but it saves bookmarks :D
# If a work is deleted from the source, this will at least hold details about what was there.

all_bookmarks = []

# used for adding timestamp to file names
timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")

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


def get_bookmarks(session):
    """
    This one will require some rate-limiting handling...
    If you have many bookmarks, we'll only try to grab the first three pages by default. To increase this limit, change the variable MAX_PAGES
    """

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

    # save bookmarks to file
    with open(f"./stat_output/{timestamp}_bookmarks.json", "w", encoding="utf-8") as f:
        json.dump(all_bookmarks.to_dict(), f, indent=4)
