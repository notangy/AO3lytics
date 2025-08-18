from datetime import date
import os
import time

from dotenv import load_dotenv
from dataclasses import dataclass, asdict

load_dotenv()

USERNAME = os.getenv("AO3_USERNAME", "")
PASSWORD = os.getenv("AO3_PASSWORD", "")

BASE_URL = "https://archiveofourown.org"
USERS_URL = BASE_URL + "/users/" + USERNAME
LOGIN_URL = BASE_URL + "/users/login"

TIMESTAMP = time.strftime("%Y-%m-%d_%H-%M-%S")


# Save global user stats here
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


# Each story is a work
@dataclass
class Work:
    id: str
    title: str
    fandoms: list
    kudos: int
    word_count: int
    hits: int

    # Convert object list to dict for json export
    def to_dict(self):
        data = asdict(self)
        return data


# WorkStats are only applicable to our own stories
@dataclass
class WorkStats(Work):
    subscriptions: int
    bookmarks: int
    comment_threads: int


@dataclass
class WorkDetails(Work):
    authors: list
    rating: str
    warnings: list
    category: list
    complete: bool

    relationships: list
    characters: list
    tags: list

    summary: str
    current_chapters: str
    language: str
    date_updated: str


@dataclass
class Bookmark(WorkDetails):
    date_saved: str
