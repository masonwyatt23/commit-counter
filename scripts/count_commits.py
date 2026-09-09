#!/usr/bin/env python3
import json
import os
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


GITHUB_API_URL = 'https://api.github.com'
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_USERNAME = os.getenv('GITHUB_USERNAME', 'masonwyatt23')


def get_headers():
    """Return authenticated headers for cross-repository commit search."""
    if not GITHUB_TOKEN:
        raise RuntimeError('GITHUB_TOKEN is required to count private repository commits')

    return {
        'Accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {GITHUB_TOKEN}',
        'User-Agent': 'masonwyatt23-commit-counter',
        'X-GitHub-Api-Version': '2022-11-28',
    }


def get_total_commits():
    """Count commits GitHub attributes to the configured user."""
    query = urlencode({
        'q': f'author:{GITHUB_USERNAME}',
        'per_page': 1,
    })
    request = Request(f'{GITHUB_API_URL}/search/commits?{query}', headers=get_headers())

    try:
        response = urlopen(request, timeout=20)
        data = json.loads(response.read().decode())
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
        raise RuntimeError(f'GitHub commit search failed: {error}') from error

    total = data.get('total_count') if isinstance(data, dict) else None
    incomplete = data.get('incomplete_results') if isinstance(data, dict) else None
    if not isinstance(total, int) or total < 0 or incomplete is not False:
        raise RuntimeError('GitHub returned incomplete or invalid commit search results')

    return total


def main():
    total_commits = get_total_commits()
    output = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'scope': f'commits authored by {GITHUB_USERNAME} across accessible repositories',
        'total_commits': total_commits,
    }

    with open('commit_stats.json', 'w') as output_file:
        json.dump(output, output_file, indent=2)
        output_file.write('\n')

    print(f'Total commits attributed to {GITHUB_USERNAME}: {total_commits:,}')
    print('Saved aggregate-only stats to commit_stats.json')


if __name__ == '__main__':
    main()
