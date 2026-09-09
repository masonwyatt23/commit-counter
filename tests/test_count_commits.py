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

    def test_counts_nonfork_default_branch_history_across_pages(self):
        first_page = FakeResponse({
            "data": {
                "repositoryOwner": {
                    "repositories": {
                        "nodes": [
                            {
                                "isFork": False,
                                "defaultBranchRef": {
                                    "target": {"history": {"totalCount": 100}}
                                },
                            },
                            {
                                "isFork": True,
                                "defaultBranchRef": {
                                    "target": {"history": {"totalCount": 5000}}
                                },
                            },
                            {"isFork": False, "defaultBranchRef": None},
                        ],
                        "pageInfo": {"hasNextPage": True, "endCursor": "next"},
                    }
                }
            }
        })
        second_page = FakeResponse({
            "data": {
                "repositoryOwner": {
                    "repositories": {
                        "nodes": [
                            {
                                "isFork": False,
                                "defaultBranchRef": {
                                    "target": {"history": {"totalCount": 25}}
                                },
                            }
                        ],
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                    }
                }
            }
        })
        with (
            patch.object(counter, "GITHUB_TOKEN", "test-token"),
            patch.object(counter, "urlopen", side_effect=[first_page, second_page]),
        ):
            self.assertEqual(counter.get_owner_totals("example"), (125, 2))

    def test_combines_configured_owners(self):
        with patch.object(
            counter,
            "get_owner_totals",
            side_effect=[(2417, 35), (33175, 71), (1898, 2)],
        ) as get_owner_totals:
            self.assertEqual(
                counter.get_combined_totals(counter.DEFAULT_OWNERS),
                (37490, 108),
            )
            self.assertEqual(
                [call.args[0] for call in get_owner_totals.call_args_list],
                list(counter.DEFAULT_OWNERS),
            )

    def test_graphql_errors_fail_closed(self):
        response = FakeResponse({"errors": [{"message": "forbidden"}]})
        with patch.object(counter, "GITHUB_TOKEN", "test-token"), patch.object(
            counter, "urlopen", return_value=response
        ):
            with self.assertRaisesRegex(RuntimeError, "returned errors"):
                counter.request_owner_page("example")

    def test_api_errors_fail_closed(self):
        error = HTTPError("https://api.github.com", 403, "forbidden", {}, BytesIO())
        with (
            patch.object(counter, "GITHUB_TOKEN", "test-token"),
            patch.object(counter, "urlopen", side_effect=error),
        ):
            with self.assertRaisesRegex(RuntimeError, "history query failed"):
                counter.request_owner_page("example")


if __name__ == "__main__":
    unittest.main()
