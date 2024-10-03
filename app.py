import json
import flask
from flask import Response
from flasgger import Swagger
from simple_calendar_service.controller.event_controller import events_page

app = flask.Flask(__name__)
app.config["SWAGGER"] = {
    "title": "Simple Calendar Service",
    "uiversion": 3,
    "openapi": "3.0.2",
}
app.config["DEBUG"] = True
app.register_blueprint(events_page)
swagger = Swagger(app)


@app.route("/health", methods=["GET"])
def health():
    """
    ---
    summary: Checks health
    tags:
        - System
    responses:
        200:
            content:
                application/json:
                    schema:
                        type: object

    """
    return Response(
        response=json.dumps({"Message": "Health endpoint is reachable"}), status=200
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
