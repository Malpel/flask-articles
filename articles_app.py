#!/usr/bin/python

from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt


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

class RegisterForm(Form):
    name = StringField("Name", [validators.Length(min=1, max=50)])
    username = StringField("Username", [validators.Length(min=1, max=25)])
    email = StringField("Email", [validators.Email(message="Please provide a legit email address")])
    password = PasswordField("Password", [validators.DataRequired(), validators.EqualTo("confirm", message="Passwords don't match")])
    confirm = PasswordField("Confrim password")

@articles_app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm(request.form)
    if request.method == "POST" and form.validate():
        return render_template("register.html")
    return render_template("register.html", form=form)



if __name__ == '__main__':
    articles_app.run(debug=True)