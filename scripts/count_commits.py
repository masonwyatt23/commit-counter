#!/usr/bin/env python3
import json
import os
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


GITHUB_GRAPHQL_URL = 'https://api.github.com/graphql'
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
DEFAULT_OWNERS = ('masonwyatt23', 'ashlrai', 'Cash-Margin-Partners')
GITHUB_OWNERS = tuple(
    owner.strip()
    for owner in os.getenv('GITHUB_OWNERS', ','.join(DEFAULT_OWNERS)).split(',')
    if owner.strip()
)
SCOPE = (
    'default-branch commits across non-fork repositories owned by '
    'masonwyatt23, ashlrai, and Cash-Margin-Partners'
)

REPOSITORY_HISTORY_QUERY = '''
query($login: String!, $cursor: String) {
  repositoryOwner(login: $login) {
    repositories(
      first: 100
      after: $cursor
      ownerAffiliations: [OWNER]
      orderBy: {field: NAME, direction: ASC}
    ) {
      nodes {
        isFork
        defaultBranchRef {
          target {
            ... on Commit {
              history(first: 1) {
                totalCount
              }
            }
          }
        }
      }
      pageInfo {
        hasNextPage
        endCursor
      }
    }
  }
}
'''


def get_headers():
    """Return authenticated headers for private repository GraphQL queries."""
    if not GITHUB_TOKEN:
        raise RuntimeError('GITHUB_TOKEN is required to count private repository commits')

    return {
        'Accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {GITHUB_TOKEN}',
        'Content-Type': 'application/json',
        'User-Agent': 'masonwyatt23-commit-counter',
        'X-GitHub-Api-Version': '2022-11-28',
    }


def request_owner_page(owner, cursor=None):
    """Fetch one page of repository history totals for an owner."""
    body = json.dumps({
        'query': REPOSITORY_HISTORY_QUERY,
        'variables': {'login': owner, 'cursor': cursor},
    }).encode()
    request = Request(
        GITHUB_GRAPHQL_URL,
        data=body,
        headers=get_headers(),
        method='POST',
    )

    try:
        response = urlopen(request, timeout=30)
        payload = json.loads(response.read().decode())
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
        raise RuntimeError(f'GitHub repository history query failed for {owner}: {error}') from error

    if not isinstance(payload, dict) or payload.get('errors'):
        raise RuntimeError(f'GitHub returned errors for repository owner {owner}')

    data = payload.get('data')
    owner_data = data.get('repositoryOwner') if isinstance(data, dict) else None
    repositories = owner_data.get('repositories') if isinstance(owner_data, dict) else None
    if not isinstance(repositories, dict):
        raise RuntimeError(f'GitHub returned invalid repository data for {owner}')

    nodes = repositories.get('nodes')
    page_info = repositories.get('pageInfo')
    if not isinstance(nodes, list) or not isinstance(page_info, dict):
        raise RuntimeError(f'GitHub returned invalid pagination data for {owner}')

    return nodes, page_info


def get_owner_totals(owner):
    """Count default-branch history across an owner's non-fork repositories."""
    total_commits = 0
    total_repositories = 0
    cursor = None

    while True:
        nodes, page_info = request_owner_page(owner, cursor)
        for repository in nodes:
            if not isinstance(repository, dict) or repository.get('isFork') is not False:
                continue

            default_branch = repository.get('defaultBranchRef')
            if default_branch is None:
                continue

            count = (
                default_branch.get('target', {})
                .get('history', {})
                .get('totalCount')
            ) if isinstance(default_branch, dict) else None
            if not isinstance(count, int) or count < 0:
                raise RuntimeError(f'GitHub returned an invalid commit total for {owner}')

            total_commits += count
            total_repositories += 1

        has_next_page = page_info.get('hasNextPage')
        next_cursor = page_info.get('endCursor')
        if has_next_page is False:
            break
        if has_next_page is not True or not isinstance(next_cursor, str) or not next_cursor:
            raise RuntimeError(f'GitHub returned invalid pagination state for {owner}')
        cursor = next_cursor

    return total_commits, total_repositories


def get_combined_totals(owners=GITHUB_OWNERS):
    """Combine repository history totals across configured owners."""
    if not owners:
        raise RuntimeError('At least one GitHub repository owner is required')

    total_commits = 0
    total_repositories = 0
    for owner in owners:
        owner_commits, owner_repositories = get_owner_totals(owner)
        total_commits += owner_commits
        total_repositories += owner_repositories

    return total_commits, total_repositories


def main():
    total_commits, total_repositories = get_combined_totals()
    output = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'scope': SCOPE,
        'total_commits': total_commits,
        'total_repositories': total_repositories,
    }

    with open('commit_stats.json', 'w') as output_file:
        json.dump(output, output_file, indent=2)
        output_file.write('\n')

    print(f'Total default-branch commits: {total_commits:,}')
    print(f'Non-fork repositories counted: {total_repositories:,}')
    print('Saved aggregate-only stats to commit_stats.json')


if __name__ == '__main__':
    main()
