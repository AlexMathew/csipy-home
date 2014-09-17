from flask import Flask, render_template, redirect, request
import psycopg2
from functools import wraps
import os
import urlparse


app = Flask(__name__)


def connectDB(wrapped):
    @wraps(wrapped)
    def inner(*args, **kwargs):
        urlparse.uses_netloc.append("postgres")
        url = urlparse.urlparse(os.environ["DATABASE_URL"])
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        cur = conn.cursor()
        return wrapped(cur, *args, **kwargs)
    return inner


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/participants')
@connectDB
def participants(*args):
    cur = args[0]
    cur.execute('SELECT REG, NAME FROM PARTICIPANTS WHERE REGISTERED IS true')
    parts = cur.fetchall()
    return render_template('participants.html', participants = parts)


@app.route('/setup')
def setup():
    return render_template('setup.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/complete', methods=['POST'])
@connectDB
def complete(*args):
    return render_template('/success.html')
