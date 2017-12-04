#!/usr/bin/python

from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps


articles_app = Flask(__name__)

#Config MariaDB
articles_app.config["MYSQL_HOST"] = "localhost"
articles_app.config["MYSQL_USER"] = "root"
articles_app.config["MYSQL_PASSWORD"] = "*************"
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
    return render_template("articles.html", articles=Articles)

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

@articles_app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password_candidate = request.form["password"]

        cur = mariaDb.connection.cursor()
        result = cur.execute("SELECT * FROM User WHERE username = %s", [username])

        if result > 0:
            data = cur.fetchone()
            password = data["password"]

            if sha256_crypt.verify(password_candidate, password):
                session["logged_in"] = True
                session["username"] = username

                flash("You are now logged in", "success")
                return redirect(url_for("dashboard"))
            else:
                error = "Invalid login"
            return render_template("login.html", error=error)
        
            cur.close()

        else:
            error = "Username not found"
            return render_template("login.html", error=error)

    return render_template("login.html")

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Unauthorized", "danger")
            return redirect(url_for("login"))
    return wrap

@articles_app.route("/dashboard")
@is_logged_in
def dashboard():
    return render_template("dashboard.html")

class ArticleForm(Form):
    title = StringField("Title", [validators.Length(min=1, max=200)])
    body = TextAreaField("Body", [validators.Length(min=1)])
    
@articles_app.route("/add_article", methods=["GET", "POST"])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == "POST" and form.validate():
        title = form.title.data
        body = form.body.data

        cur = mariaDb.connection.cursor()
        cur.execute("INSERT INTO Article(title, author, body) VALUES(%s, %s, %s)", (title, session["username"], body))
        mariaDb.connection.commit()
        cur.close()
        flash("Article Created", "success")

        return redirect(url_for("dashboard"))
    return render_template("add_article.html", form=form)

@articles_app.route("/logout")
@is_logged_in
def logout():
    session.clear()
    flash("You are now logged out", "success")
    return redirect(url_for("login"))

if __name__ == '__main__':
    articles_app.secret_key="secret123"
    articles_app.run(debug=True)