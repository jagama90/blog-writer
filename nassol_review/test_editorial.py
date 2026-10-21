"""Run with: python -m unittest discover -s nassol_review -p 'test_*.py'"""
import unittest
from editorial import build

class EditorialTests(unittest.TestCase):
    def setUp(self):
        self.data = {
            "person": "28기 영자",
            "title": "[지니지구 생각] 나는솔로 28기 영자 근황",
            "sources": [{"date": "2026-07-31", "url": "https://example.com/story", "claim": "공개된 발표가 있었다."}],
            "editorial": {"take": "내 생각은 이렇다.", "ending": "각자의 일상을 응원한다."},
        }

    def test_single_final_title_and_no_prefix(self):
        title, body = build(self.data)
        self.assertEqual(title, "나는솔로 28기 영자 근황")
        self.assertEqual(body.count("# 나는솔로 28기 영자 근황"), 1)

    def test_missing_opinion_is_rejected(self):
        self.data["editorial"].pop("take")
        with self.assertRaises(ValueError):
            build(self.data)

    def test_missing_source_url_is_rejected(self):
        self.data["sources"][0].pop("url")
        with self.assertRaises(ValueError):
            build(self.data)

if __name__ == "__main__":
    unittest.main()
