#!/usr/bin/python

from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt


articles_app = Flask(__name__)

#Config MariaDB
articles_app.config["MYSQL_HOST"] = "localhost"
articles_app.config["MYSQL_USER"] = "root"
articles_app.config["MYSQL_PASSWORD"] = "mariadpulmunen"
articles_app.config["MYSQL_DB"] = "articles"
articles_app.config["MYSQL_CURSORCLASS"] = "DictCursor"

#init MariaDB
mariaDb = MySQL(articles_app)

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
    confirm = PasswordField("Confirm password")

@articles_app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm(request.form)

    if request.method == "POST" and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        #Cursor
        cur = mariaDb.connection.cursor()
        
        cur.execute("INSERT INTO User(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

        #Commit to database
        mariaDb.connection.commit()

        cur.close()

        flash("Register successful! Sign into your account", "success")
        
        return redirect(url_for("index"))
    return render_template("register.html", form=form)



if __name__ == '__main__':
    articles_app.secret_key="secret123"
    articles_app.run(debug=True)