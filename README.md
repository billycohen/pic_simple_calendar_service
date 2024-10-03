# Calendar Service

## Submission notes
I have left TODOs within the comments in the app - with more time I would be looking to add these as improvements.

With additional time, i would also look to implement additional unit tests to cover edge cases, specifically related to
parsing different datetime formats

---

## Running the app
### Pre-requisites
You must have the following technologies installed in order to run the app
- Python
- Docker
- MongoDB (If running from outside the container)

### Instructions

#### Running the app
From pic_simple_calendar_service directory:

```bash
docker-compose up
```

Navigate to http://localhost:8000/apidocs/ to access Swagger UI

Note: Sample events can be found within ./tests/data/events.json

#### Running tests

Install python libraries

```bash
pip install --upgrade -r requirements.txt
```

Run tests with coverage
```bash
python -m coverage report run -m unittest discover .
```

Get coverage report
```bash
coverage report -m
```

---

## Intro
The aim of this exercise is to write a simple calendar service. The service has to accept calendar events comprised of a
date-time and description, in JSON format, and save them persistently. On request, the service should return the saved 
calendar events in a JSON format aligned to the input one. The full protocol implemented by the service is provided
below.

### Exercise Objectives
- Provide a calendar service implementation in Python.
- Provide a Dockerfile for packaging of the service.
- Provide instructions or a script code for building and running the containerised application.

---
## Protocol
### Endpoints
- /events (POST): Accepts events in event payload format. Returns the inserted event as JSON object.

- /events/<ID>[?datetime_format=<STRPTIME FORMAT>] (GET): Returns the named event in event payload format. 
The optional query parameter datetime_format is described in arguments. Returns the event with matching id as 
JSON object.

- /events[?][datetime_format=<STRPTIME FORMAT>][&][from_time=<DATE TIME>][&][to_time=<DATE TIME>] (GET): Returns all events falling within a date range. Where the date range defaults to "today" at 00:00:00 to now. The optional query parameters are described in arguments. Returns a list of matching event JSON objects.

---
## Event Payload Format
The format for insertion and return of calendar events is:
{
"description": "<FREE FORM EVENT DESCRIPTION>",
"time": "<DATE TIME>",
"id": "<NUMERIC ID>"
}
where the id field not only contained in queries.

### Arguments
- datetime_format: Date-time format for parsing/printing of dates. Compatible with strptime /strftime  format specification. The default value for this argument is %Y-%m-%dT%H:%M:%S, e.g. 2024-01-01T00:00:00.
- from_time: Specifies the start of a date range. The exptected date time format is goverened by the value/default of the datetime_format argument. Defaults to start of the current day.
- to_time: Specifies the end of a date range. The exptected date time format is goverened by the value/default of the datetime_format argument. Defaults to the datetime of request receipt.

