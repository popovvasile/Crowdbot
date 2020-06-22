import logging

from flask import Flask
from flask_restful import Api
from rest_api.api.errors import errors
from .resources import CrowdRobot, UserBots, AllBots, RevokeToken


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app():
    api = Api(errors=errors)
    new_app = Flask(__name__)
    new_app.config["BUNDLE_ERRORS"] = True
    new_app.config["API_KEY"] = (
        "1aa189ce-9a96-4b5d-9c23-d39e49175e21-7a01f777-a969-4d2a-a3f5-4d5c92913286")

    api.add_resource(CrowdRobot, "/crowdbot")  # post, delete, get

    api.add_resource(UserBots, "/user_bots")  # get

    api.add_resource(AllBots, "/crowdbots")  # get

    api.add_resource(RevokeToken, "/revoke_token")  # patch

    api.init_app(new_app)

    return new_app


if __name__ == '__main__':
    app = create_app()
    app.run(host="127.0.0.1",
            port=8000,
            debug=True)
