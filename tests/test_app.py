import unittest
import json

from app import app


class TestApp(unittest.TestCase):
    def setUp(self):
        self.ctx = app.app_context()
        self.ctx.push()
        self.client = app.test_client()

    def testDown(self):
        self.ctx.pop()

    def test_app(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.data), {"Message": "Health endpoint is reachable"}
        )
