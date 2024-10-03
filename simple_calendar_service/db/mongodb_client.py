import os
from datetime import datetime
from typing import Dict, Any, List, Optional

import pymongo
from pymongo import ReplaceOne
from pymongo.results import BulkWriteResult
from pymongo.synchronous.collection import Collection
from pymongo.synchronous.database import Database


class MongoDBClient:
    def __init__(
        self, database: str, collection: str, client: pymongo.MongoClient = None
    ):

        self.client = pymongo.MongoClient(
            host=os.getenv("MONGODB_HOSTNAME"),
            port=int(os.getenv("MONGODB_PORT", 0)),
            username=os.getenv("MONGODB_ROOT_USERNAME"),
            password=os.getenv("MONGODB_ROOT_PASSWORD"),
            authSource=os.getenv("MONGODB_AUTHSOURCE"),
        )

        self.db: Database = self.client[database]
        self.collection: Collection = self.db[collection]

    def execute_write_transaction(self, queries):
        return self.collection.bulk_write(queries)

    def insert_document(self, document: Dict[str, Any]):
        return self.collection.insert_one(document=document)

    def insert_documents(self, documents: List[Any]) -> Dict[str, Any]:
        batch_upsert_query = []
        document_with_ids = []
        for document in documents:
            document_with_id = document.convert_to_mongodb_record()
            document_with_ids.append(document_with_id)
            upsert_document_query = ReplaceOne(
                {"_id": document_with_id["_id"]}, document_with_id, upsert=True
            )
            batch_upsert_query.append(upsert_document_query)

        res: BulkWriteResult = self.execute_write_transaction(batch_upsert_query)

        upserted_ids = list(res.upserted_ids.values())
        upserted = [
            event for event in document_with_ids if event["_id"] not in upserted_ids
        ]
        created = [event for event in document_with_ids if event["_id"] in upserted_ids]

        return {"updated": upserted, "created": created}

    def get_document(self, query: Dict[str, Any]):
        """
        Get document from collection
        :param query: key value pair representing the field and value to query for
        :return:
        """
        return self.collection.find_one(filter=query)

    def get_documents_by_date_range(
        self,
        datetime_field: str,
        datetime_lower: Optional[datetime] = None,
        datetime_upper: Optional[datetime] = None,
    ):
        """
        Query documents by date range - one of either datetime_lower or datetime_upper must be provided
        :param datetime_field:
        :param datetime_lower:
        :param datetime_upper:
        :return:
        """
        if not datetime_lower and not datetime_upper:
            raise ValueError(
                "One of datetime_lower or datetime_upper must not be None!"
            )

        datetime_range_filter = {}

        if datetime_lower:
            if not isinstance(datetime_lower, datetime):
                raise TypeError("datetime_lower must be a datetime object!")
            datetime_range_filter["$gte"] = datetime_lower

        if datetime_upper:
            if not isinstance(datetime_upper, datetime):
                raise TypeError("datetime_upper must be a datetime object!")
            datetime_range_filter["$lt"] = datetime_upper

        return self.collection.find({datetime_field: datetime_range_filter})
