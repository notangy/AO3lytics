import requests
import time
from bs4 import BeautifulSoup
import os

from ao3lytics import BASE_URL, USERNAME, safe_request


PASSWORD = os.getenv("AO3_PASSWORD", "")

LOGIN_URL = BASE_URL + "/users/login"
USERS_URL = BASE_URL + "/users/" + USERNAME


def login(session):

    request = safe_request(session, LOGIN_URL)

    # html of login page
    login_soup = BeautifulSoup(request.text, features="html.parser")
    auth_token = login_soup.find("input", {"name": "authenticity_token"})["value"]

    print("[INFO] Attempting login...")

    login_attempt = safe_request(
        session,
        LOGIN_URL,
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
