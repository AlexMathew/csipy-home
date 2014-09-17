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
        ret = wrapped(cur, *args, **kwargs)
        conn.commit()
        cur.close()
        conn.close()
        return ret
    return inner


def mailgun_send(email):
    key = os.environ["MAILGUN_KEY"]
    r = requests.post(
                 "https://api.mailgun.net/v2/sandboxaafd9ee615e54f49af424db82ccf028a.mailgun.org/messages",
                 auth=("api", key),
                 data={"from": "Alex Mathew <alexmathew003@gmail.com>",
                       "to": email,
                       "subject": "Welcome to CSIPy!",
                       "text": os.environ["WELCOME_MAIL"]})
    return


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/participants')
@connectDB
def participants(*args):
    cur = args[0]
    cur.execute('SELECT REG, NAME FROM PARTICIPANTS WHERE REGISTERED IS true ORDER BY REG')
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
    cur = args[0]
    try:
        regno = int(request.form['regno'])
    except Exception:
        return render_template('failure.html', error_msg="Please enter a valid register number.")
    cur.execute('SELECT REG FROM PARTICIPANTS')
    complete = cur.fetchall()
    cur.execute('SELECT REG FROM PARTICIPANTS WHERE REGISTERED IS true')
    registered = cur.fetchall()
    if (regno,) not in complete:
        return render_template('failure.html', error_msg="We're sorry, but the workshop is currently \
                                open only to members registed to CSI. Try getting links to the resources \
                                from your friends who are attending the workshop. We'll keep you \
                                posted if we plan an open Python workshop. Thanks for your interest !")
    elif (regno,) in registered:
        return render_template('failure.html', error_msg="You're already registered.")
    else:
        cur.execute('UPDATE PARTICIPANTS SET REGISTERED=true WHERE REG=%s', (regno,))
        cur.execute('SELECT EMAIL FROM PARTICIPANTS WHERE REG=%s', (regno,))
        email = cur.fetchall()[0]
        mailgun_send(email)
        return render_template('success.html')
