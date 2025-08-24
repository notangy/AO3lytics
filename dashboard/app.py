import json
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
from os.path import isfile, join

app = Flask(__name__)
load_dotenv()

username = os.environ.get("AO3_USERNAME")


# Find stat output folder in parent dir
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
stat_folder = os.path.join(parent_dir, "stat_output")

"""

TODO

1. Parse existing folders in ./stat_output for their dates, allow them to be selected in the dashboard date picker
And load in the relevant files in those folders

2. Store stats in database instead of fetching from folder

"""


@app.route("/")
def index():
    # TODO return stats here
    return render_template("index.html", username=username, stats=None)


# We expect the date format to be the same as the stat folder names
# e.g /api/stats?date=2025-08-24
@app.route("/api/stats")
def get_all_stats():

    date = request.args.get("date")  # reads ?date=...

    if not date:
        return jsonify({"error": "No date provided"}), 400

    folder = f"{stat_folder}/{date}"

    if os.path.exists(folder) and os.path.isdir(folder):

        stats = {}
        stat_groups = ["work_stats", "user_stats", "bookmarks"]

        # Get all stat files in this folder
        for entry in os.listdir(folder):
            full_path = os.path.join(folder, entry)

            matched = False

            for s in stat_groups:
                if s in entry.lower():
                    with open(full_path, "r", encoding="utf-8") as f:
                        stats[s] = json.load(f)
                    matched = True
                    break

            if not matched:
                print(f"Unable to categorise file {entry}, skipping...")

        return (
            jsonify(stats),
            200,
        )
    else:
        return jsonify({"error": "Stats not found"}), 400


if __name__ == "__main__":
    app.run(debug=True)
