from flask import Flask, render_template, redirect
import psycopg2
import os
import urlparse

app = Flask(__name__)


# def connectDB(wrapped):
#     def inner(*args, **kwargs):
#         api_token = os.environ["API_TOKEN"]
#         urlparse.uses_netloc.append("postgres")
#         url = urlparse.urlparse(os.environ["DATABASE_URL"])
#         conn = psycopg2.connect(
#             database=url.path[1:],
#             user=url.username,
#             password=url.password,
#             host=url.hostname,
#             port=url.port
#         )
#         cur = conn.cursor()
#         ret = wrapped(*args, **kwargs)
#         return ret
#     return inner


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/participants')
@connectDB
def participants():
    return render_template('participants.html')


@app.route('/setup')
def setup():
    return render_template('setup.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/complete', methods=['POST'])
@connectDB
def complete():
    return redirect('/')
