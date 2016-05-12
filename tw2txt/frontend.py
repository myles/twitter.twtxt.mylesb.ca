from urllib.parse import urljoin

from flask import Blueprint, Response, url_for, request, current_app as app

from flask_piwikapi import FlaskRequest
from flask_httpauth import HTTPDigestAuth

import pytz
import tweepy
from piwikapi.tracking import PiwikTracker

frontend = Blueprint('frontend', __name__)

auth = HTTPDigestAuth()


@auth.get_password
def get_pw(username):
    if username == app.config['BASIC_AUTH_USERNAME']:
        return app.config['BASIC_AUTH_PASSWORD']
    return None


def get_tweets(username):
    auth = tweepy.OAuthHandler(app.config['TWITTER_CONSUMER_KEY'],
                               app.config['TWITTER_CONSUMER_SECRET'])

    auth.set_access_token(app.config['TWITTER_ACCESS_TOKEN_KEY'],
                          app.config['TWITTER_ACCESS_TWOKEN_SECRET'])

    api = tweepy.API(auth)

    tweets = api.user_timeline(username)

    return tweets


def process_tweet(tweet):
    timestamp = pytz.utc.localize(tweet.created_at).isoformat()

    if tweet.retweeted:
        retweet_screen_name = tweet.retweeted_status.author.screen_name
        retweet_url = urljoin(app.config['HEROKU_URL'],
                              url_for('frontend.get_user_timeline',
                                      username=retweet_screen_name))
        text = tweet.retweeted_status.text
    else:
        text = tweet.text.replace('\n', ' ¶ ')

    for url in tweet.entities.get('urls', []):
        text = text.replace(url['url'], url['expanded_url'])

    for media in tweet.entities.get('media', []):
        text = text.replace(media['url'], media['media_url_https'])

    for user_mention in tweet.entities.get('user_mentions', []):
        user_url = urljoin(app.config['HEROKU_URL'],
                           url_for('frontend.get_user_timeline',
                                   username=user_mention['screen_name']))
        mention = "@<{0} {1}>".format(user_mention['screen_name'],
                                      user_url)

        text = text.replace("@{0}".format(user_mention['screen_name']),
                            mention)

    if tweet.retweeted:
        response_text = text.replace('\n', ' ¶ ')
        return "{0}\tRT @<{1} {2}> {3}\n".format(timestamp,
                                                 retweet_screen_name,
                                                 retweet_url,
                                                 response_text)
    else:
        return "{0}\t{1}\n".format(timestamp,
                                   text.replace('\n', ' ¶ '))


def track_visit(request, page_title):
    """
    Track visits in Piwik.
    """
    piwik = PiwikTracker(app.config['PIWIK_SITE_ID'], FlaskRequest(request))
    piwik.set_api_url(app.config['PIWIK_TRACKING_API_URL'])
    piwik.set_token_auth(app.config['PIWIK_TOKEN_AUTH'])

    piwik.do_track_page_view(page_title)


@frontend.route('/')
def index():
    twtxt = []

    for tweet in get_tweets(app.config['TWITTER_USERNAME']):
        twtxt.append(process_tweet(tweet))

    # track_visit(request, app.config['TWITTER_USERNAME'])

    return Response(''.join(twtxt), mimetype='text/plain')


@frontend.route('/user/<username>')
def get_user_timeline(username):
    twtxt = []

    for tweet in get_tweets(username):
        twtxt.append(process_tweet(tweet))

    # track_visit(request, username)

    return Response(''.join(twtxt), mimetype='text/plain')
