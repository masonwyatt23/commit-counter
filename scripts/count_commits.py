#!/usr/bin/env python3
import os
import json
import subprocess
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import URLError
import re

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_API_URL = 'https://api.github.com'

def get_headers():
    """Get authorization headers for GitHub API"""
    return {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

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
        except URLError as e:
            print(f"Error fetching {url}: {e}")
            break
    
    return results

def get_repos():
    """Fetch all personal and org repositories"""
    repos = []
    headers = get_headers()
    
    print("Fetching personal repositories...")
    # Get personal repos
    url = f'{GITHUB_API_URL}/user/repos?type=owner'
    personal_repos = fetch_paginated(url, headers)
    repos.extend(personal_repos)
    print(f"Found {len(personal_repos)} personal repositories")
    
    # Get org repos
    print("Fetching organization memberships...")
    url = f'{GITHUB_API_URL}/user/orgs'
    orgs = fetch_paginated(url, headers)
    print(f"Found {len(orgs)} organizations")
    
    for org in orgs:
        print(f"Fetching repositories for {org['login']}...")
        url = f'{GITHUB_API_URL}/orgs/{org["login"]}/repos'
        org_repos = fetch_paginated(url, headers)
        repos.extend(org_repos)
        print(f"Found {len(org_repos)} repositories in {org['login']}")
    
    return repos

def count_commits_for_repo(repo):
    """Count commits in a repository using GitHub API"""
    try:
        headers = get_headers()
        url = f"{GITHUB_API_URL}/repos/{repo['full_name']}/commits"
        
        # Make a HEAD request to get the Link header which contains pagination info
        req = Request(url, headers=headers)
        req.get_method = lambda: 'HEAD'
        
        try:
            response = urlopen(req, timeout=10)
            link_header = response.headers.get('Link', '')
            
            # Extract total from Link header if available
            if 'last' in link_header:
                match = re.search(r'page=(\d+)>; rel="last"', link_header)
                if match:
                    return int(match.group(1))
        except:
            pass
        
        # Fallback: use GET request with per_page=1 to get count from Link header
        url_with_params = f"{GITHUB_API_URL}/repos/{repo['full_name']}/commits?per_page=1"
        req = Request(url_with_params, headers=headers)
        response = urlopen(req, timeout=10)
        link_header = response.headers.get('Link', '')
        
        if 'last' in link_header:
            match = re.search(r'page=(\d+)>; rel="last"', link_header)
            if match:
                return int(match.group(1))
        
        # If no Link header, fetch actual commits
        data = json.loads(response.read().decode())
        return len(data) if isinstance(data, list) else 1
        
    except Exception as e:
        print(f"Error counting commits for {repo['full_name']}: {e}")
        return 0

def main():
    print("=" * 60)
    print("GitHub Commit Counter")
    print("=" * 60)
    print()
    
    repos = get_repos()
    print(f"\nTotal repositories found: {len(repos)}")
    
    total_commits = 0
    repo_stats = []
    
    # Filter out forks
    filtered_repos = [r for r in repos if not r.get('fork', False)]
    print(f"Counting commits for {len(filtered_repos)} non-forked repositories...\n")
    
    for i, repo in enumerate(filtered_repos, 1):
        print(f"[{i}/{len(filtered_repos)}] {repo['full_name']}...", end=' ', flush=True)
        commits = count_commits_for_repo(repo)
        total_commits += commits
        print(f"✓ {commits} commits")
        
        repo_stats.append({
            'name': repo['full_name'],
            'commits': commits,
            'url': repo['html_url'],
            'language': repo.get('language'),
            'description': repo.get('description')
        })
    
    # Save results
    output = {
        'timestamp': datetime.now().isoformat(),
        'total_commits': total_commits,
        'total_repositories': len(filtered_repos),
        'repositories': sorted(repo_stats, key=lambda x: x['commits'], reverse=True)
    }
    
    with open('commit_stats.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print("\n" + "=" * 60)
    print(f"✓ Total commits: {total_commits:,}")
    print(f"✓ Total repositories: {len(filtered_repos)}")
    print(f"✓ Saved to commit_stats.json")
    print("=" * 60)

if __name__ == '__main__':
    main()
