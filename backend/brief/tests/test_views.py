from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.test import APIClient

from brief.config import BriefOutput

URL = "/api/v1/generate-brief/"
VALID = {
    "target": "Instagram",
    "goal": "Awareness",
    "tone": "Friendly",
    "brand_name": "Acme",
}


def _fake_response():
    return SimpleNamespace(
        model="gpt-4o-mini",
        status="completed",
        output_parsed=BriefOutput(
            brief="A tailored brief.",
            angles=["a1", "a2", "a3"],
            criteria=["c1", "c2", "c3"],
        ),
        usage=SimpleNamespace(input_tokens=10, output_tokens=20, total_tokens=30),
    )


class GenerateBriefViewTests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()

    @patch("brief.services.OpenAI")
    def test_happy_path(self, mock_openai):
        mock_openai.return_value.responses.parse.return_value = _fake_response()

        res = self.client.post(URL, VALID, format="json")

        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertEqual(len(body["angles"]), 3)
        self.assertEqual(len(body["criteria"]), 3)
        self.assertEqual(body["stats"]["total_tokens"], 30)
        self.assertIn("latency_ms", body["stats"])

    def test_validation_error_returns_400(self):
        res = self.client.post(URL, {**VALID, "goal": "Nope"}, format="json")
        self.assertEqual(res.status_code, 400)
