import unittest
import pymongo
import mongomock
from datetime import datetime

from simple_calendar_service.db.mongodb_client import MongoDBClient
from simple_calendar_service.dto.event import Event


class TestMongoDBClient(unittest.TestCase):

    @mongomock.patch(servers=(("localhost", 27017),))
    def setUp(self):
        client = pymongo.MongoClient(host="localhost", port=27017)

        client["test-db"]["test-collection"].drop()

        self.mongodb_client = MongoDBClient(
            database="test-db", collection="test-collection"
        )

    def test_insert_documents(self):
        res = self.mongodb_client.insert_documents(
            documents=[
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

        self.assertEqual(len(res["created"]), 1)

    def test_get_document_by_id(self):
        document = {
            "_id": 1,
            "id": 1,
            "description": "test-1",
            "time": datetime.strptime("2024-01-01T00:00:00", "%Y-%m-%dT%H:%M:%S"),
        }

        self.mongodb_client.insert_documents(documents=[Event(**document)])

        retrieved_item = self.mongodb_client.get_document(query={"id": 1})

        self.assertEqual(document, retrieved_item)

    def test_get_document_by_missing_id(self):
        retrieved_item = self.mongodb_client.get_document(query={"id": 1})

        self.assertIsNone(retrieved_item)

    def test_get_documents_by_date_range(self):
        # TODO: Decouple Event DTO from irrelevant unit tests using a TestDTO
        documents = [
            Event(
                id=1, time=datetime.strptime("2024-01-10T00:00:00", "%Y-%m-%dT%H:%M:%S")
            ),
            Event(
                id=2, time=datetime.strptime("2024-01-15T00:00:00", "%Y-%m-%dT%H:%M:%S")
            ),
            Event(
                id=3, time=datetime.strptime("2024-01-20T00:00:00", "%Y-%m-%dT%H:%M:%S")
            ),
        ]

        res = self.mongodb_client.insert_documents(documents=documents)

        self.assertEqual(len(res["created"]), 3)

        with self.assertRaises(ValueError):
            self.mongodb_client.get_documents_by_date_range(
                datetime_field="datetime_field",
            )

        with self.assertRaises(TypeError):
            self.mongodb_client.get_documents_by_date_range(
                datetime_field="datetime_field", datetime_lower="2024-01-01"
            )

        self.assertEqual(
            [
                document["id"]
                for document in self.mongodb_client.get_documents_by_date_range(
                    datetime_field="time",
                    datetime_lower=datetime.strptime(
                        "2024-01-10T00:00:00", "%Y-%m-%dT%H:%M:%S"
                    ),
                    datetime_upper=datetime.strptime(
                        "2024-01-16T00:00:00", "%Y-%m-%dT%H:%M:%S"
                    ),
                )
            ],
            [1, 2],
        )

        self.assertEqual(
            [
                document["id"]
                for document in self.mongodb_client.get_documents_by_date_range(
                    datetime_field="time",
                    datetime_lower=datetime.strptime(
                        "2024-01-14T00:00:00", "%Y-%m-%dT%H:%M:%S"
                    ),
                    datetime_upper=datetime.strptime(
                        "2024-01-21T00:00:00", "%Y-%m-%dT%H:%M:%S"
                    ),
                )
            ],
            [2, 3],
        )
