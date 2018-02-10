from flask import Flask, jsonify
from credentials import value
from flask_ask import Ask, statement, question
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, db

import logging

from datetime import datetime

app = Flask(__name__)
CORS(app)
ask = Ask(app, "/dogpictures")


@app.route('/')
def homepage():
    return 'hi you, how ya doin?'


# admin json key values exported from firebase portal
cred = credentials.Certificate(value)

default_app = firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://alexa-dogpictures.firebaseio.com/'
})

app.config.update(dict(
    DEBUG=True,
    RDB_HOST='localhost',
    RDB_PORT='28015',
    RDB_DB='dogpictures'
))


def update_dog(number):
    ref = db.reference('DogPictures').child('1')
    print(ref)
    values = {
        'dogPicture': number
    }
    ref.update(values)
    return 'success!'


@app.route('/getdog')
def getdog():
    try:
        ref = db.reference('DogPictures').child('1').get()
        print(ref)
        result = jsonify(ref)
        return result
    except Exception as err:
        return {'error': err.message}


log = logging.getLogger()
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)
logging.getLogger("flask_ask").setLevel(logging.DEBUG)


@ask.launch
def start_skill():
    welcome_message = 'Welcome to dog pictures, you can ask for a dog picture by saying dog number 1'
    return question(welcome_message)


@ask.intent("AMAZON.NoIntent")
def no_intent():
    bye_text = "Thank you... bye"
    return statement(bye_text)


@ask.intent("AMAZON.StopIntent")
def StopIntent():
    return statement('Stopping,bye bye, have a nice day')


@ask.intent("AMAZON.CancelIntent")
def CancelIntent():
    return statement('Cancelling, bye bye, have a nice day')


@ask.intent("AMAZON.YesIntent")
def YesIntent():
    yes_message = "Please confirm which dog picture you will like to see?"
    return question(yes_message)


@ask.intent("AMAZON.HelpIntent")
def HelpIntent():
    help_message = "You can search for dog picture by saying all pictures or dog number 1,...  please state what will you like to search?"
    return question(help_message)


# @ask.intent("ShowAllDogPicturesIntent")
# def all_dogs():
#     msg = '{}, Do you want to search more'.format('all dogs')
#     return question(msg)


@ask.intent("ShowDogPictureIntent")
def share_dog_picture(number):
    update_dog(number)
    msg = 'You said number {}, Do you want to search more'.format(number)
    return question(msg)


@ask.session_ended
def session_ended():
    log.debug("Session Ended")
    return "", 200


if __name__ == '__main__':
    app.run(debug=True)
