import importlib.util
import json
from io import BytesIO
from pathlib import Path
import unittest
from unittest.mock import patch
from urllib.error import HTTPError


SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "count_commits.py"
SPEC = importlib.util.spec_from_file_location("count_commits", SCRIPT_PATH)
counter = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(counter)


class FakeResponse:
    def __init__(self, payload):
        self._payload = json.dumps(payload).encode()

    def read(self):
        return self._payload


class CommitCounterTests(unittest.TestCase):
    def test_requires_authenticated_token(self):
        with patch.object(counter, "GITHUB_TOKEN", None):
            with self.assertRaisesRegex(RuntimeError, "GITHUB_TOKEN is required"):
                counter.get_headers()

    def test_returns_complete_author_total(self):
        response = FakeResponse({"total_count": 13574, "incomplete_results": False})
        with (
            patch.object(counter, "GITHUB_TOKEN", "test-token"),
            patch.object(counter, "urlopen", return_value=response),
        ):
            self.assertEqual(counter.get_total_commits(), 13574)

    def test_incomplete_search_fails_closed(self):
        response = FakeResponse({"total_count": 13574, "incomplete_results": True})
        with (
            patch.object(counter, "GITHUB_TOKEN", "test-token"),
            patch.object(counter, "urlopen", return_value=response),
        ):
            with self.assertRaisesRegex(RuntimeError, "incomplete or invalid"):
                counter.get_total_commits()

    def test_api_errors_fail_closed(self):
        error = HTTPError("https://api.github.com", 403, "forbidden", {}, BytesIO())
        with (
            patch.object(counter, "GITHUB_TOKEN", "test-token"),
            patch.object(counter, "urlopen", side_effect=error),
        ):
            with self.assertRaisesRegex(RuntimeError, "commit search failed"):
                counter.get_total_commits()


if __name__ == "__main__":
    unittest.main()
