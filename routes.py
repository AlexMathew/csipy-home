from flask import Flask, render_template, redirect, request, session, escape, url_for
import psycopg2
from functools import wraps
import os
import urlparse
import requests


app = Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']


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


def accessSession(wrapped):
    @wraps(wrapped)
    def inner(*args, **kwargs):
        msgclass = session['msgclass']
        text = session['text']
        ret = wrapped(msgclass, text, *args)
        session['msgclass'] = session['text'] = None
        return ret
    return inner


def mailgun_operations(name, email):
    key = os.environ["MAILGUN_KEY"]
    r = requests.post(
                     "https://api.mailgun.net/v2/sandboxaafd9ee615e54f49af424db82ccf028a.mailgun.org/messages",
                     auth=("api", key),
                     data={"from": "Alex Mathew <alexmathew003@gmail.com>",
                           "to": email,
                           "subject": "Welcome to CSIPy!",
                           "text": os.environ["WELCOME_MAIL"]})
    r = requests.post(
                     "https://api.mailgun.net/v2/lists/csipy@sandboxaafd9ee615e54f49af424db82ccf028a.mailgun.org/members",
                     auth=('api', key),
                     data={'subscribed': True,
                           'address': email,
                           'name': name,
                           'description': '',
                           'vars': '{"name": "' + name + '"}'})
    return


@app.route('/')
def home():
    if 'msgclass' not in session:
        session['msgclass'] = session['text'] = None
    return render_template('home.html')


@app.route('/participants')
@connectDB
def participants(*args):
    cur = args[0]
    cur.execute('SELECT REG, NAME FROM PARTICIPANTS WHERE REGISTERED IS true ORDER BY REG')
    parts = cur.fetchall()
    return render_template('participants.html', participants=parts)


@app.route('/setup')
def setup():
    return render_template('setup.html')


@app.route('/register')
@accessSession
def register(*args):
    msgclass, text = args[0], args[1]
    return render_template('register.html', msgclass=msgclass, text=text)


@app.route('/complete', methods=['POST'])
@connectDB
def complete(*args):
    cur = args[0]
    try:
        regno = int(request.form['regno'])
    except Exception:
        session['msgclass'] = "alert alert-danger"
        session['text'] = "Please enter a valid register number."        
        return redirect(url_for('register'))
    cur.execute('SELECT REG FROM PARTICIPANTS')
    complete = cur.fetchall()
    cur.execute('SELECT REG FROM PARTICIPANTS WHERE REGISTERED IS true')
    registered = cur.fetchall()
    if (regno,) not in complete:
        session['msgclass'] = "alert alert-danger"
        session['text'] = "We're sorry, but the workshop is currently \
                           open only to members registed to CSI. Try getting links to the resources \
                           from your friends who are attending the workshop. We'll keep you \
                           posted if we plan an open Python workshop. Thanks for your interest !"
    elif (regno,) in registered:
        session['msgclass'] = "alert alert-danger"
        session['text'] = "You've already registered."
    else:
        session['msgclass'] = "alert alert-success"
        session['text'] = "<strong>Welcome onboard !</strong> You have registered for the workshop. \
                           We'll keep you posted on what to do before the workshop."
        cur.execute('UPDATE PARTICIPANTS SET REGISTERED=true WHERE REG=%s', (regno,))
        cur.execute('SELECT NAME, EMAIL FROM PARTICIPANTS WHERE REG=%s', (regno,))
        name, email = cur.fetchone()
        mailgun_operations(name, email)
    return redirect(url_for('register'))
