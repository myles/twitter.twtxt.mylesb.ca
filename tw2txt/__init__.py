import os

from flask import Flask

from flask_appconfig import HerokuConfig

from .frontend import frontend


def create_app(configfile=None):
    app = Flask(__name__)

    HerokuConfig(app, configfile)

    app.register_blueprint(frontend)

    env_variables = ['TWITTER_USERNAME', 'TWITTER_CONSUMER_KEY',
                     'TWITTER_CONSUMER_SECRET', 'TWITTER_ACCESS_TOKEN_KEY',
                     'TWITTER_ACCESS_TWOKEN_SECRET']

    for variable in env_variables:
        app.config[variable] = os.environ.get(variable)

    return app


app = create_app()

port = int(os.environ.get("PORT", 5000))
app.run(host='0.0.0.0', port=port, debug=True)
