import json
import os
import re
from datetime import datetime
from typing import List, Dict
from flask import request, Response, Blueprint
from pydantic.json import pydantic_encoder
from simple_calendar_service.db.dao.event import EventDAO
from simple_calendar_service.dto.event import Event

events_page = Blueprint(
    "events_page",
    __name__,
)

MONGODB_EVENTS_COLLECTION_NAME = os.getenv("MONGODB_EVENTS_COLLECTION_NAME")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE")

DAO = EventDAO


@events_page.route("/events", methods=["POST"])
def create_events():
    """
    Create new calendar events
    ---
    summary: Create new calendar events.
    description: Accepts events in event payload format. Returns the inserted event as JSON object.
    tags:
        - Event
    requestBody:
        required: true
        content:
            application/json:
                schema:
                    type: array
                    items:
                        type: object
    responses:
        200:
            description: OK
            content:
                application/json:
                    schema:
                        type: object
        400:
            description: Bad request error in provided JSON
            content:
                application/json:
                    schema: Error
    """
    json_body = request.get_json()

    try:
        events = []
        for item in json_body:
            events.append(
                Event(
                    id=item["id"],
                    description=item.get("description", ""),
                    time=datetime.strptime(item["time"], "%Y-%m-%dT%H:%M:%S"),
                )
            )

        res: Dict[str, List[Event]] = DAO(
            database=MONGODB_DATABASE,
            collection=MONGODB_EVENTS_COLLECTION_NAME
        ).create_events(events=events)

        return Response(
            response=json.dumps(
                {
                    "createdEvents": res["created"],
                    "updatedEvents": res["updated"],
                    "message": "Successfully created events",
                },
                default=pydantic_encoder,
            ),
            status=200,
        )

    except KeyError as e:
        return Response(
            response=json.dumps(
                {
                    "message": f"Exception raised when attempting to create Event records, check body contains valid events: {str(e)}"
                }
            ),
            status=400,
        )


@events_page.route("/event/<int:id>", methods=["GET"])
def get_event_by_id(id: int):
    """
    Get calendar event by ID
    ---
    summary: Get calendar event by ID.
    description: Returns the specified event in event payload format. The optional query parameter datetime_format is described in arguments. Returns the event with matching id as JSON object.
    tags:
        - Event
    parameters:
        - in: path
          name: id
          description: id of event record
          required: true
          schema:
            type: integer
        - in: query
          name: datetime_format
          description:  Date-time format for parsing/printing of dates. Compatible with strptime/strftime format specification. The default value for this argument is %Y-%m-%dT%H:%M:%S, e.g. 2024-01-01T00:00:00.
          required: false
          schema:
            type: string
    responses:
        200:
            description: OK
            content:
                application/json:
                    schema:
                        type: Event
        400:
            description: Record not found
            content:
                application/json:
                    schema: Error
        422:
            description: Invalid datetime_format
            content:
                application/json:
                    schema: Error
    """
    datetime_format = request.args.get("datetime_format")

    try:
        res: Event = DAO(
            database=MONGODB_DATABASE,
            collection=MONGODB_EVENTS_COLLECTION_NAME
        ).get_event_by_id(id=id)

        if not res:
            return Response(
                response=json.dumps({"message": "No record found"}), status=400
            )

        formatted_event = res.format_time(datetime_format)

        return Response(
            response=json.dumps(
                {
                    "retrievedEvent": formatted_event,
                    "message": "Successfully retrieved event",
                },
                default=pydantic_encoder,
            ),
            status=200,
        )
    except re.error:
        return Response(
            response=json.dumps(
                {
                    "message": f"Error formatting retrieved record with the specified datetime_format: {datetime_format}"
                }
            ),
            status=422,
        )


@events_page.route("/events", methods=["GET"])
def get_events_by_time_range():
    """
    Get calendar events by date range.
    ---
    summary: Get calendar events by date range.
    description: Returns all events falling within a date range. Where the date range defaults to "today" at 00:00:00 to now. The optional query parameters are described in arguments. Returns a list of matching event JSON objects.
    tags:
        - Event
    parameters:
        - in: query
          name: from_time
          description: lower date range boundary
          required: false
          schema:
            type: string
        - in: query
          name: to_time
          description: upper date range boundary
          required: false
          schema:
            type: string
        - in: query
          name: datetime_format
          description:  Date-time format for parsing/printing of dates. Compatible with strptime/strftime format specification. The default value for this argument is %Y-%m-%dT%H:%M:%S, e.g. 2024-01-01T00:00:00.
          required: false
          schema:
            type: string
    responses:
        200:
            description: OK
        400:
            description: Unable to query using specified datetime_format
            content:
                application/json:
                    schema: Error
    """

    datetime_format = request.args.get("datetime_format")
    from_time = request.args.get("from_time")
    to_time = request.args.get("to_time")

    try:
        res: List[Event] = DAO(
            database=MONGODB_DATABASE,
            collection=MONGODB_EVENTS_COLLECTION_NAME
        ).get_events_by_time_range(from_time, to_time)

        if not res:
            return Response(
                response=json.dumps({"message": "No records found"}), status=400
            )

        formatted_events = [event.format_time(datetime_format) for event in res]

        return Response(
            response=json.dumps(
                {
                    "retrievedEvents": formatted_events,
                    "message": "Successfully retrieved event",
                },
                default=pydantic_encoder,
            ),
            status=200,
        )
    except re.error:
        return Response(
            response=json.dumps(
                {
                    "message": f"Error formatting retrieved record with the specified datetime_format: {datetime_format}"
                }
            ),
            status=422,
        )
