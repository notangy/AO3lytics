import json
import re
import requests
from bs4 import BeautifulSoup


from consts import USERS_URL, TIMESTAMP, WorkDetails

from utils import safe_request, extract_work_id


# Like stat parser, but it saves bookmarks :D
# If a work is deleted from the source, this will at least hold details about what was there.

all_bookmarks = []

MAX_PAGES = 3


"""
This one will require some rate-limiting handling...
If you have many bookmarks, we'll only try to grab the first three pages by default. To increase this limit, change the variable MAX_PAGES
"""


# Remove newlines & other html stuff
def normalize_whitespace(text):
    return re.sub(r"\s+", " ", text).strip()


# Return stripped text if element exists, else empty string
def safe_text(soup, selector):
    el = soup.select_one(selector)
    return normalize_whitespace(el.get_text()) if el else ""


def gather_tags(soup, target_class):
    tag_links = soup.find_all("li", class_=target_class)
    tags = []

    for r in tag_links:
        tags.append(normalize_whitespace(r.text))
    return tags


def get_bookmarks(session=None):

    # bookmarks_url = USERS_URL + "/bookmarks"

    # bookmarks_request = safe_request(session, bookmarks_url)

    # if bookmarks_request.status_code != 200:
    #     raise requests.exceptions.RequestException("AO3 is experiencing issues!")

    # bookmark_soup = BeautifulSoup(bookmarks_request.text, "lxml")

    with open("./bookmarks_test.html") as fp:
        bookmark_soup = BeautifulSoup(fp, "lxml")

    current_page = 1
    next_link = None

    next_elem = bookmark_soup.find("a", string=re.compile(r"^\s*Next"))

    # If the 'Next ->' button is a link, more than one page exists
    if next_elem:
        next_link = next_elem["href"]

    # Go through all works on this page

    bookmarks = bookmark_soup.find_all("li", attrs={"class": "bookmark"})

    for b in bookmarks:

        # title & author heading
        heading = b.find("h4", class_="heading")
        links = heading.find_all("a")
        # First <a> = title
        title = links[0].get_text(strip=True)

        work_link = links[0].get("href")

        work_id = extract_work_id(work_link)

        # Remaining <a>s = authors
        authors = [a.get_text(strip=True) for a in links[1:]]

        # fandom tags
        fandoms_heading = b.find("h5", class_="fandoms")
        fandoms = [a.get_text(strip=True) for a in fandoms_heading.find_all("a")]

        required_tags = b.find_all("a", attrs={"title": "Symbols key"})

        rating = required_tags[0].text
        warnings = required_tags[1].text
        category = required_tags[2].text

        complete = False
        if required_tags[3].text == "Complete Work":
            complete = True

        # Gathering other tags

        relationships = gather_tags(b, "relationships")
        characters = gather_tags(b, "characters")
        tags = gather_tags(b, "freeforms")

        summary = safe_text(b, "blockquote.userstuff.summary")

        language = safe_text(b, "dd.language")
        word_count = safe_text(b, "dd.words")
        kudos = safe_text(b, "dd.kudos")
        hits = safe_text(b, "dd.hits")

        current_chapters = safe_text(b, "dd.chapters")

        bookmark = WorkDetails(
            work_id,
            title,
            fandoms,
            kudos,
            word_count,
            hits,
            authors,
            rating,
            warnings,
            category,
            complete,
            relationships,
            characters,
            tags,
            summary,
            current_chapters,
            language,
        )

        all_bookmarks.append(bookmark)

    bookmarks_dicts = [bookmark.to_dict() for bookmark in all_bookmarks]
    # save bookmarks to file
    print(f"[INFO] Bookmarks gathered. Now writing to file.")
    with open(f"./stat_output/{TIMESTAMP}_bookmarks.json", "w", encoding="utf-8") as f:
        json.dump(bookmarks_dicts, f, indent=4)


if __name__ == "__main__":
    get_bookmarks()
