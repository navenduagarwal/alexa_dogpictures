from flask import Flask, g, render_template, make_response, request, redirect, url_for, jsonify
from flask_ask import Ask, statement, question, session
import rethinkdb as r
from rethinkdb import RqlRuntimeError, RqlDriverError

import json
import requests
import time
import unidecode
import logging
from fuzzywuzzy import fuzz
import os

from datetime import datetime
from dateutil import tz
import re

app = Flask(__name__)
ask = Ask(app, "/dogpictures")


@app.route('/')
def homepage():
    return 'hi you, how ya doin?'


app.config.update(dict(
    DEBUG=True,
    RDB_HOST='localhost',
    RDB_PORT='28015',
    RDB_DB='dogpictures'
))


# db setup; only run once
def dbSetup():
    connection = r.connect(host=app.config['RDB_HOST'], port=app.config['RDB_PORT'])
    try:
        r.db_create(app.config['RDB_DB']).run(connection)
        r.db(app.config['RDB_DB']).table_create('DogPictures').run(connection)
        print 'Database setup completed'
    except RqlRuntimeError:
        print 'Database already exists'
    finally:
        connection.close()


# open connection before each request
@app.before_request
def before_request():
    try:
        g.rdb_conn = r.connect(host=app.config['RDB_HOST'], port=app.config['RDB_PORT'], db=app.config['RDB_DB'])
    except RqlDriverError:
        abort(503, "Database connection could be established.")


# close the connection after each request
@app.teardown_request
def teardown_request(exception):
    try:
        g.rdb_conn.close()
    except AttributeError:
        pass


def create_dog(number):
    data = {}
    data['id'] = 1
    data['pictureToShow'] = number
    data['updated'] = datetime.now(r.make_timezone('00:00'))
    new_dog = r.table("dogpictures").get(1).replace(data).run(g.rdb_conn)
    return 'success!'


dbSetup()

log = logging.getLogger()
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)
logging.getLogger("flask_ask").setLevel(logging.DEBUG)


@ask.launch
def start_skill():
    welcome_message = 'Welcome to dog pictures, you can ask for a dog picture by saying dog number 1'
    return question(welcome_message)


@ask.intent("NoIntent")
def no_intent():
    bye_text = "Thank you... bye"
    return statement(bye_text)


@ask.intent("AMAZON.StopIntent")
def StopIntent():
    return statement('Stopping,bye bye, have a nice day')


@ask.intent("AMAZON.CancelIntent")
def CancelIntent():
    return statement('Cancelling, bye bye, have a nice day')


@ask.intent("YesIntent")
def YesIntent():
    yes_message = "Please confirm which dog picture you will like to see?"
    return question(yes_message)


@ask.intent("AMAZON.HelpIntent")
def HelpIntent():
    help_message = "You can search for dog picture by saying all pictures or dog number 1,...  please state what will you like to search?"
    return question(help_message)


@ask.intent("ShowAllDogPicturesIntent")
def all_dogs():
    msg = '{}, Do you want to search more'.format('all dogs')
    return question(msg)


@ask.intent("ShowDogPictureIntent")
def share_dog_picture(number):
    create_dog(number)
    msg = 'You said number {}, Do you want to search more'.format(number)
    return question(msg)


@ask.session_ended
def session_ended():
    log.debug("Session Ended")
    return "", 200


if __name__ == '__main__':
    app.run(debug=True)
