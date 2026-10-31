import unittest
import json
from app import app
import database as db

class TestFlaskEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        db.init_db()

    def test_pages_load(self):
        routes = ['/', '/attendance', '/analytics', '/suggestions', '/settings']
        for r in routes:
            resp = self.client.get(r)
            self.assertEqual(resp.status_code, 200, f"Route {r} failed with status {resp.status_code}")

    def test_api_session_lifecycle(self):
        # 1. Create session
        create_res = self.client.post('/api/sessions/create', json={
            "title": "Automated Unit Test Session",
            "class_name": "Test Class",
            "instructor": "Tester"
        })
        self.assertEqual(create_res.status_code, 200)
        sess_data = json.loads(create_res.data)
        sess_id = sess_data["session"]["id"]

        # 2. Multimodal telemetry step
        step_res = self.client.post('/api/telemetry/multimodal_step', json={
            "session_id": sess_id,
            "elapsed_seconds": 10,
            "rms": 0.03,
            "peak": 0.05
        })
        self.assertEqual(step_res.status_code, 200)

        # 3. Export CSV and JSON
        att_res = self.client.get(f'/api/export/attendance/{sess_id}')
        self.assertEqual(att_res.status_code, 200)
        self.assertIn("text/csv", att_res.content_type)

        json_res = self.client.get(f'/api/export/json/{sess_id}')
        self.assertEqual(json_res.status_code, 200)
        self.assertIn("application/json", json_res.content_type)

if __name__ == '__main__':
    unittest.main()
