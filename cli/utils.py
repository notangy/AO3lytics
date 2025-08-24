import time
import requests
import re
import os
from consts import OUTPUT_DIR


def extract_work_id(link):
    # Match the work ID after /works/ in the URL
    match = re.search(r"/works/(\d+)", link)
    if match:
        return match.group(1)


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


def write_output(filename):
    return os.path.join(OUTPUT_DIR, filename)
