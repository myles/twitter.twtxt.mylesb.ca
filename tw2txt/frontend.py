from flask import Blueprint, Response, current_app as app

import pytz
import tweepy

frontend = Blueprint('frontend', __name__)


def get_tweets():
    auth = tweepy.OAuthHandler(app.config['TWITTER_CONSUMER_KEY'],
                               app.config['TWITTER_CONSUMER_SECRET'])

    auth.set_access_token(app.config['TWITTER_ACCESS_TOKEN_KEY'],
                          app.config['TWITTER_ACCESS_TWOKEN_SECRET'])

    api = tweepy.API(auth)

    tweets = api.user_timeline(app.config['TWITTER_USERNAME'])

    return tweets


@frontend.route('/')
def index():
    twtxt = []

    for tweet in get_tweets():
        response = "{0}\t{1}\n".format(
                    pytz.utc.localize(tweet.created_at).isoformat(),
                    tweet.text.replace('\n', ' '))
        twtxt.append(response)

    return Response(''.join(twtxt), mimetype='text/plain')
