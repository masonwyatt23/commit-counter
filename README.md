# 📊 GitHub Commit Counter

Automatically calculate and track total commits across all your GitHub personal and organization repositories.

## Features

✨ **Automated Tracking** - Runs daily via GitHub Actions
📈 **Comprehensive Stats** - Counts commits across all your repos
🌐 **Website Ready** - Display stats on your company website
📱 **Responsive Design** - Beautiful web interface included
🔒 **Public Access** - Stats JSON is publicly available for embedding

## How It Works

1. **GitHub Actions Workflow** runs daily at 2 AM UTC
2. **Python Script** fetches all your personal and organization repositories
3. **Commit Counting** uses the GitHub API to count commits per repo
4. **Results Storage** saves stats to `commit_stats.json`
5. **Website Display** shows stats in a beautiful web interface

## Setup

### 1. Ensure GitHub Token Access

The workflow uses the default `GITHUB_TOKEN` which is automatically created. However, to count commits across organization repositories, make sure your token has appropriate access.

### 2. Run Manually (Optional)

Trigger the workflow manually to test:
- Go to **Actions** → **Calculate Total Commits** → **Run workflow**

### 3. Integrate into Your Website

Add the following HTML to your website to display the commit stats:

```html
<iframe 
  src="https://masonwyatt23.github.io/commit-counter/"
  width="600"
  height="500"
  frameborder="0"
  style="border-radius: 8px;"
></iframe>
```

Or fetch the raw JSON data:

```javascript
fetch('https://raw.githubusercontent.com/masonwyatt23/commit-counter/main/commit_stats.json')
  .then(r => r.json())
  .then(data => {
    console.log('Total commits:', data.total_commits);
    console.log('Total repos:', data.total_repositories);
  });
```

## Output Format

The script generates a `commit_stats.json` file with the following structure:

```json
{
  "timestamp": "2024-01-15T02:00:00.000000",
  "total_commits": 15234,
  "total_repositories": 45,
  "repositories": [
    {
      "name": "masonwyatt23/my-repo",
      "commits": 1234,
      "url": "https://github.com/masonwyatt23/my-repo",
      "language": "Python",
      "description": "My awesome project"
    }
  ]
}
```

## Files

- `.github/workflows/commit-counter.yml` - GitHub Actions workflow
- `scripts/count_commits.py` - Main Python script
- `public/index.html` - Web display interface
- `README.md` - This file

## Customization

### Change Execution Schedule

Edit `.github/workflows/commit-counter.yml` and modify the cron expression:

```yaml
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
```

Common cron examples:
- `0 2 * * *` - Daily at 2 AM UTC
- `0 0 * * 0` - Weekly (Sunday midnight UTC)
- `0 0 1 * *` - Monthly (1st day, midnight UTC)

### Enable GitHub Pages

To use the website display:

1. Go to **Settings** → **Pages**
2. Set **Source** to `Deploy from a branch`
3. Select `main` branch and `/root` folder
4. Save

The site will be available at: `https://masonwyatt23.github.io/commit-counter/`

## Troubleshooting

### Workflow not running?
- Check **Actions** tab for any errors
- Manually trigger workflow to test
- Verify `GITHUB_TOKEN` has necessary permissions

### Stats not updating?
- Check the workflow logs in **Actions** tab
- Verify you have commits in your repositories
- GitHub API rate limits: 5,000 requests/hour per token

### Incorrect commit counts?
- GitHub API counts commits correctly for most repos
- Very large repositories (100k+ commits) may have slight variations
- Re-run the workflow if needed

## API Rate Limiting

The script respects GitHub's API rate limits:
- Authenticated requests: 5,000/hour
- Typical run: ~50-100 API calls

## Support

For issues or feature requests, create an issue in this repository.

## License

MIT License - feel free to use and modify this script!
