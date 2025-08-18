import time
import requests


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
