from flask import current_app, abort
from flask_restful import reqparse


def validate_access(value):
    if value != current_app.config["API_KEY"]:
        raise abort(401, "API_KEY invalid")
    return value


access_parser = reqparse.RequestParser()
access_parser.add_argument("API_KEY", type=validate_access, location="json", required=True)
