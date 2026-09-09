#!/usr/bin/env python3
import os
import json
from datetime import datetime, timezone
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
import re

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_API_URL = 'https://api.github.com'
GITHUB_USERNAME = os.getenv('GITHUB_USERNAME', 'masonwyatt23')

def get_headers():
    """Get authorization headers for GitHub API"""
    headers = {
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'masonwyatt23-commit-counter',
        'X-GitHub-Api-Version': '2022-11-28',
    }
    if GITHUB_TOKEN:
        headers['Authorization'] = f'Bearer {GITHUB_TOKEN}'
    return headers

def fetch_paginated(url, headers):
    """Fetch all paginated results from GitHub API"""
    results = []
    page = 1
    
    while True:
        try:
            pagination_url = f'{url}{"&" if "?" in url else "?"}page={page}&per_page=100'
            req = Request(pagination_url, headers=headers)
            response = urlopen(req, timeout=10)
            data = json.loads(response.read().decode())
            
            if not data or (isinstance(data, list) and len(data) == 0):
                break
            
            if isinstance(data, list):
                results.extend(data)
            else:
                results.append(data)
            
            page += 1
        except (HTTPError, URLError, TimeoutError) as e:
            raise RuntimeError(f"GitHub request failed for {url}: {e}") from e
    
    return results

def get_repos():
    """Fetch public repositories owned by the user and their public orgs."""
    repos = []
    headers = get_headers()
    
    print(f"Fetching public repositories owned by {GITHUB_USERNAME}...")
    url = f'{GITHUB_API_URL}/users/{GITHUB_USERNAME}/repos?type=owner&sort=full_name'
    personal_repos = fetch_paginated(url, headers)
    repos.extend(personal_repos)
    print(f"Found {len(personal_repos)} personal repositories")
    
    print("Fetching public organization memberships...")
    url = f'{GITHUB_API_URL}/users/{GITHUB_USERNAME}/orgs'
    orgs = fetch_paginated(url, headers)
    print(f"Found {len(orgs)} organizations")
    
    for org in orgs:
        print(f"Fetching repositories for {org['login']}...")
        url = f'{GITHUB_API_URL}/orgs/{org["login"]}/repos?type=public&sort=full_name'
        org_repos = fetch_paginated(url, headers)
        repos.extend(org_repos)
        print(f"Found {len(org_repos)} repositories in {org['login']}")
    
    return list({repo['id']: repo for repo in repos}.values())

def count_commits_for_repo(repo):
    """Count commits in a repository using GitHub API"""
    try:
        headers = get_headers()
        # With one commit per page, the final page number is the default
        # branch's commit count. GitHub returns no Link header for 0-1 commits.
        url_with_params = f"{GITHUB_API_URL}/repos/{repo['full_name']}/commits?per_page=1"
        req = Request(url_with_params, headers=headers)
        response = urlopen(req, timeout=10)
        link_header = response.headers.get('Link', '')
        
        if 'last' in link_header:
            match = re.search(r'page=(\d+)>; rel="last"', link_header)
            if match:
                return int(match.group(1))
        
        data = json.loads(response.read().decode())
        return len(data) if isinstance(data, list) else 0
    except HTTPError as e:
        if e.code == 409:  # Empty repository.
            return 0
        raise RuntimeError(
            f"Could not count commits for {repo['full_name']}: {e}"
        ) from e
    except Exception as e:
        raise RuntimeError(
            f"Could not count commits for {repo['full_name']}: {e}"
        ) from e

def main():
    print("=" * 60)
    print("GitHub Commit Counter")
    print("=" * 60)
    print()
    
    repos = get_repos()
    print(f"\nTotal repositories found: {len(repos)}")
    if not repos:
        raise RuntimeError("GitHub returned no public repositories; refusing to publish zero stats")
    
    total_commits = 0
    # Filter out forks
    filtered_repos = [r for r in repos if not r.get('fork', False)]
    print(f"Counting commits for {len(filtered_repos)} non-forked repositories...\n")
    
    for i, repo in enumerate(filtered_repos, 1):
        print(f"[{i}/{len(filtered_repos)}] {repo['full_name']}...", end=' ', flush=True)
        commits = count_commits_for_repo(repo)
        total_commits += commits
        print(f"✓ {commits} commits")

    # Save results
    output = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'scope': 'public repositories and default branches',
        'total_commits': total_commits,
        'total_repositories': len(filtered_repos),
    }
    
    with open('commit_stats.json', 'w') as f:
        json.dump(output, f, indent=2)
        f.write('\n')
    
    print("\n" + "=" * 60)
    print(f"✓ Total commits: {total_commits:,}")
    print(f"✓ Total repositories: {len(filtered_repos)}")
    print(f"✓ Saved to commit_stats.json")
    print("=" * 60)

if __name__ == '__main__':
    main()
