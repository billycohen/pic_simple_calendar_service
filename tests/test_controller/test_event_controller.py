import os
import unittest
import json
from datetime import datetime
from unittest import mock
from unittest.mock import MagicMock

from simple_calendar_service.controller.event_controller import DAO
from simple_calendar_service.dto.event import Event

class TestEventController(unittest.TestCase):

    def setUp(self):
        with open(os.path.join(os.path.dirname(__file__), "../data/events.json")) as events_json:
            self.events = json.load(events_json)
            events_json.close()


        os.environ['MONGODB_EVENTS_COLLECTION_NAME'] = ""
        os.environ['MONGODB_DATABASE'] = ""
        from app import app
        self.app = app


    @mock.patch("simple_calendar_service.controller.event_controller.DAO")
    def test_events_post(self, mocked_dao):

        mocked_instance = MagicMock()
        mocked_instance.create_events.return_value= {"created": self.events[:6], "updated": self.events[6:]}
        mocked_dao.return_value = mocked_instance

        with self.app.test_client() as client:
            res = client.post("/events", json=self.events)

        print(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(json.loads(res.data)["createdEvents"]), 6)
        self.assertEqual(len(json.loads(res.data)["updatedEvents"]), 13)


    def test_events_post_invalid_data(self):

        with mock.patch.object(DAO, 'create_events', return_value=self.events):
            with self.app.test_client() as client:
                res = client.post("/events", json=[{"invalid":"record"}])

        self.assertEqual(res.status_code, 400)
        self.assertEqual(json.loads(res.data)["message"], "Exception raised when attempting to create Event records, check body contains valid events: 'id'")


    @mock.patch("simple_calendar_service.controller.event_controller.DAO")
    def test_get_record_by_id(self, mocked_dao):
        mocked_instance = MagicMock()

        event = Event(
            id=1,
            description="test description",
            time=datetime.strptime("2024-01-01T00:00:00", "%Y-%m-%dT%H:%M:%S")
        )

        mocked_instance.get_event_by_id.return_value = event
        mocked_dao.return_value = mocked_instance

        with self.app.test_client() as client:
            res = client.get("/event/1")

        self.assertEqual(res.status_code, 200)
        self.assertEqual(Event(**json.loads(res.data)['retrievedEvent']), event)


    @mock.patch("simple_calendar_service.controller.event_controller.DAO")
    def test_get_record_by_id_with_formatting(self, mocked_dao):
        mocked_instance = MagicMock()

        event = Event(
            id=1,
            description="test description",
            time=datetime.strptime("2024-01-01T00:00:00", "%Y-%m-%dT%H:%M:%S")
        )

        mocked_instance.get_event_by_id.return_value=event
        mocked_dao.return_value = mocked_instance

        with self.app.test_client() as client:
            res = client.get("/event/1?datetime_format=%Y-%m-%d")

        retrieved_event = json.loads(res.data)['retrievedEvent']

        self.assertEqual(retrieved_event['time'], '2024-01-01')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(Event(**retrieved_event), event)


    @mock.patch("simple_calendar_service.controller.event_controller.DAO")
    def test_get_record_by_id_missing_record(self, mocked_dao):
        mocked_instance = MagicMock()
        mocked_instance.get_event_by_id.return_value=None
        mocked_dao.return_value = mocked_instance

        with self.app.test_client() as client:
            res = client.get("/event/1")

        print(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(json.loads(res.data)['message'], 'No record found')

    @mock.patch("simple_calendar_service.controller.event_controller.DAO")
    def test_get_records_by_time_range(self, mocked_dao):
        mocked_instance = MagicMock()
        events = [
            Event(
                id=1,
                time=datetime.strptime("2024-01-01T00:00:00", "%Y-%m-%dT%H:%M:%S")
            ),
            Event(
                id=2,
                time=datetime.strptime("2024-01-01T00:00:00", "%Y-%m-%dT%H:%M:%S")
            ),
            Event(
                id=3,
                time=datetime.strptime("2024-01-01T00:00:00", "%Y-%m-%dT%H:%M:%S")
            )
        ]

        mocked_instance.get_events_by_time_range.return_value=events
        mocked_dao.return_value = mocked_instance

        with self.app.test_client() as client:
            res = client.get("/events?from_date=2024-01-01T00:00:00&to_date=2024-01-20T00:00:00&datetime_format=%Y-%m-%d")

        self.assertTrue(all([event["time"] == "2024-01-01" for event in [event for event in json.loads(res.data)["retrievedEvents"]]]))
        self.assertTrue(res.status_code, 200)
