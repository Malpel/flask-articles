#!/usr/bin/python

from flask import Flask, render_template
from data import Articles

articles_app = Flask(__name__)
Articles = Articles()

@articles_app.route("/")
def index():
    return render_template("index.html")

@articles_app.route("/articles")
def articles():
    return render_template("articles.html", articles = Articles)

@articles_app.route("/articles/<string:id>/")
def article(id):
    return render_template("article.html", id=id)

@articles_app.route("/about")
def about():
    return render_template("about.html")


if __name__ == '__main__':
    articles_app.run(debug=True)