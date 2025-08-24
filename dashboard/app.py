from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index():
    # TODO return stats here
    return render_template("index.html", stats=None)


if __name__ == "__main__":
    app.run(debug=True)
