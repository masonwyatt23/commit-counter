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
    def __init__(self, payload, link=""):
        self._payload = json.dumps(payload).encode()
        self.headers = {"Link": link}

    def read(self):
        return self._payload


class CommitCounterTests(unittest.TestCase):
    def test_last_page_is_commit_count(self):
        response = FakeResponse(
            [{"sha": "abc"}],
            '<https://api.github.com/repositories/1/commits?per_page=1&page=42>; rel="last"',
        )
        with patch.object(counter, "urlopen", return_value=response):
            self.assertEqual(counter.count_commits_for_repo({"full_name": "org/repo"}), 42)

    def test_single_commit_without_link_header(self):
        with patch.object(counter, "urlopen", return_value=FakeResponse([{"sha": "abc"}])):
            self.assertEqual(counter.count_commits_for_repo({"full_name": "org/repo"}), 1)

    def test_empty_repository_is_zero(self):
        error = HTTPError("https://api.github.com", 409, "empty", {}, BytesIO())
        with patch.object(counter, "urlopen", side_effect=error):
            self.assertEqual(counter.count_commits_for_repo({"full_name": "org/empty"}), 0)

    def test_other_api_errors_fail_closed(self):
        error = HTTPError("https://api.github.com", 403, "forbidden", {}, BytesIO())
        with patch.object(counter, "urlopen", side_effect=error):
            with self.assertRaisesRegex(RuntimeError, "Could not count commits"):
                counter.count_commits_for_repo({"full_name": "org/repo"})


if __name__ == "__main__":
    unittest.main()
