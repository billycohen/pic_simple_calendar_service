from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from simple_calendar_service.db.mongodb_client import MongoDBClient
from simple_calendar_service.dto.event import Event


class EventDAO:
    def __init__(self, database, collection, client=None):
        if not client:
            self.db_client: MongoDBClient = MongoDBClient(
                database=database,
                collection=collection
            )
        else:
            self.db_client = client

    def create_events(self, events: List[Event]) -> Dict[str, List[Event]]:
        res: Dict[str, Any] = self.db_client.insert_documents(events)

        for category, events in res.items():
            res[category] = [Event(**event) for event in events]

        return res

    def get_event_by_id(self, id: int) -> Optional[Event]:
        res = self.db_client.get_document({"id": id})

        if not res:
            return None

        return Event(**res)

    def get_events_by_time_range(
        self, from_time: Optional[str] = None, to_time: Optional[str] = None
    ) -> List[Event]:
        from_time_datetime, to_time_datetime = EventDAO.get_time_ranges(
            from_time, to_time
        )

        res = self.db_client.get_documents_by_date_range(
            datetime_field="time",
            datetime_lower=from_time_datetime,
            datetime_upper=to_time_datetime,
        )

        events = []
        for event in res:
            events.append(Event(**event))

        return events

    @staticmethod
    def get_time_ranges(
        from_time: Optional[str], to_time: Optional[str]
    ) -> Tuple[datetime, datetime]:
        """
        Exists to enable easier testing of setting default values for time range
        :param from_time:
        :param to_time:
        :return:
        """

        if not from_time:
            # Default from time is start of current day:
            from_time = datetime.combine(datetime.today(), datetime.min.time())
        else:
            from_time = datetime.strptime(from_time, "%Y-%m-%dT%H:%M:%S")

        if not to_time:
            # Default to time is current time:
            to_time = datetime.now()
        else:
            to_time = datetime.strptime(to_time, "%Y-%m-%dT%H:%M:%S")

        return from_time, to_time
