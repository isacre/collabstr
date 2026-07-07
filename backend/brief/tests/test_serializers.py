from django.test import SimpleTestCase

from brief.config import BriefRequestSerializer

VALID = {
    "target": "Instagram",
    "goal": "Awareness",
    "tone": "Friendly",
    "brand_name": "Acme",
}


class BriefRequestSerializerTests(SimpleTestCase):
    def test_accepts_valid_payload(self):
        self.assertTrue(BriefRequestSerializer(data=VALID).is_valid())

    def test_rejects_bad_enum(self):
        s = BriefRequestSerializer(data={**VALID, "target": "Facebook"})
        self.assertFalse(s.is_valid())
        self.assertIn("target", s.errors)

    def test_rejects_blank_brand(self):
        s = BriefRequestSerializer(data={**VALID, "brand_name": "  "})
        self.assertFalse(s.is_valid())
        self.assertIn("brand_name", s.errors)
