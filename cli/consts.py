import os
import time

from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv("AO3_USERNAME", "")
PASSWORD = os.getenv("AO3_PASSWORD", "")

BASE_URL = "https://archiveofourown.org"
USERS_URL = BASE_URL + "/users/" + USERNAME
LOGIN_URL = BASE_URL + "/users/login"

TIMESTAMP = time.strftime("%Y-%m-%d_%H-%M-%S")
