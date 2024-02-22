from werkzeug.exceptions import HTTPException


errors = {
    "BotNotFound": {
        "ok": False,
        "message": "Given bot_id not found",
        "status": 404,
    },
    "InvalidToken": {
            "ok": False,
            "message": "Token invalid",
            "status": 400,
        },
}


class BotNotFound(HTTPException):
    code = 404
    description = "Given bot_id not found"


class InvalidToken(HTTPException):
    code = 400
    description = "Token invalid"
