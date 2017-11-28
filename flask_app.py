#!/usr/bin/python

from flask import Flask, render_template

flask_app = Flask(__name__)

@flask_app.route("/")
def index():
    return render_template("index.html")


if __name__ == '__main__':
    flask_app.run(debug=True)