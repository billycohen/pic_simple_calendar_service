import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock

from simple_calendar_service.db.dao.event import EventDAO
from simple_calendar_service.dto.event import Event


class TestEventDAO(unittest.TestCase):
    @patch("simple_calendar_service.db.mongodb_client.MongoDBClient")
    def test_create_events(self, mocked_db_client: MagicMock):
        mocked_result = {
            "created": [
                {
                    "id": 1,
                    "description": "test-1",
                    "time": datetime.strptime(
                        "2024-01-01T00:00:00", "%Y-%m-%dT%H:%M:%S"
                    ),
                }
            ]
        }

        mocked_db_client.insert_documents.return_value = mocked_result

        self.assertEqual(
            (
                EventDAO(database="test-db", collection="test-col", client=mocked_db_client).create_events(
                    events=[
                        Event(
                            **{
                                "id": 1,
                                "description": "test-1",
                                "time": datetime.strptime(
                                    "2024-01-01T00:00:00", "%Y-%m-%dT%H:%M:%S"
                                ),
                            }
                        )
                    ]
                )
            ),
            mocked_result,
        )

    @patch("simple_calendar_service.db.mongodb_client.MongoDBClient")
    def test_get_event_by_id(self, mocked_db_client: MagicMock):
        mocked_result = {
            "id": 1,
            "description": "test-1",
            "time": datetime.strptime("2024-01-01T00:00:00", "%Y-%m-%dT%H:%M:%S"),
        }

        mocked_db_client.get_document.return_value = mocked_result

        self.assertEqual(
            EventDAO(database="test-db", collection="test-col", client=mocked_db_client).get_event_by_id(id=1),
            Event(**mocked_result),
        )

    @patch("simple_calendar_service.db.mongodb_client.MongoDBClient")
    def test_get_events_by_time_range(self, mocked_db_client: MagicMock):
        mocked_result = [
            {
                "id": 1,
                "description": "test-1",
                "time": datetime.strptime("2024-01-01T00:00:00", "%Y-%m-%dT%H:%M:%S"),
            }
        ]

        mocked_db_client.get_documents_by_date_range.return_value = mocked_result

        res = EventDAO(database="test-db", collection="test-col", client=mocked_db_client).get_events_by_time_range()

        self.assertEqual([Event(**event) for event in mocked_result], res)

    def test_get_time_ranges(self):
        # Test default values
        from_time, to_time = EventDAO.get_time_ranges(from_time=None, to_time=None)

        self.assertTrue(isinstance(from_time, datetime))
        self.assertTrue(isinstance(to_time, datetime))

        self.assertEqual(
            from_time, datetime.combine(datetime.today(), datetime.min.time())
        )
        self.assertEqual(to_time.date(), datetime.today().date())

        from_time, to_time = EventDAO.get_time_ranges(
            from_time="2024-01-01T00:00:00", to_time="2024-01-02T00:00:00"
        )

        self.assertEqual(
            from_time, datetime.strptime("2024-01-01T00:00:00", "%Y-%m-%dT%H:%M:%S")
        )
        self.assertEqual(
            to_time, datetime.strptime("2024-01-02T00:00:00", "%Y-%m-%dT%H:%M:%S")
        )
