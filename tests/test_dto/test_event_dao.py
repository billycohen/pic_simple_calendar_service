import unittest

from simple_calendar_service.dto.event import Event

from pydantic import ValidationError


class TestEventDTO(unittest.TestCase):

    def test_init(self):

        with self.assertRaises(ValidationError):
            Event()

        with self.assertRaises(ValidationError):
            Event(description="")

        with self.assertRaises(ValidationError):
            Event(id="dafdafdsa")

        with self.assertRaises(ValidationError):
            Event(id=1, time="fdsafdsfdsa")

    def test_format_time(self):

        event = Event(
            **{
                "id": 4,
                "description": "Numquam quisquam quiquia consectetur consectetur modi quaerat tempora.",
                "time": "2024-01-04T00:00:00"
            }
        )
        self.assertEqual(event.format_time()["time"], "2024-01-04T00:00:00")
        self.assertEqual(event.format_time("%Y-%m-%d %H:%M:%S")["time"], "2024-01-04 00:00:00")
        self.assertEqual(event.format_time("%I %p %S")["time"], "12 AM 00")

