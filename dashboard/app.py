from flask import Flask, render_template
from dotenv import load_dotenv
import os

app = Flask(__name__)
load_dotenv()

username = os.environ.get("AO3_USERNAME")


@app.route("/")
def index():
    # TODO return stats here
    return render_template("index.html", username=username, stats=None)


if __name__ == "__main__":
    app.run(debug=True)
