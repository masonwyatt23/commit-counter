# 📊 GitHub Commit Counter

Automatically track every commit GitHub attributes to `masonwyatt23` across
repositories the counter is authorized to search.

## Features

✨ **Automated Tracking** - Runs daily via GitHub Actions
📈 **Author Scoped** - Counts commits attributed to one GitHub identity
🌐 **Website Ready** - Display stats on your company website
📱 **Responsive Design** - Beautiful web interface included
🔒 **Aggregate Only** - Public JSON never contains repository inventory

## How It Works

1. **GitHub Actions Workflow** runs daily at 2 AM UTC
2. **Python Script** searches default-branch commits attributed to the configured GitHub user
3. **Private Coverage** comes from a read-only token with access to those repos
4. **Results Storage** saves stats to `commit_stats.json`
5. **Website Display** shows stats in a beautiful web interface

## Setup

### 1. GitHub Token Access

Add a repository secret named `COMMIT_COUNTER_TOKEN`. Use a dedicated,
short-lived token that can access every repository that should be counted. A
fine-grained personal access token is preferred when all repositories share one
resource owner. If coverage must span multiple organizations or owners, use a
dedicated classic token with `repo` access or a GitHub App installed on each
owner. The workflow publishes only the aggregate count; it never publishes
repository names or private metadata.

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
  });
```

## Output Format

The script generates a `commit_stats.json` file with the following structure:

```json
{
  "timestamp": "2024-01-15T02:00:00+00:00",
  "scope": "commits authored by masonwyatt23 across accessible repositories",
  "total_commits": 15234
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
- Verify `COMMIT_COUNTER_TOKEN` exists and can read the intended repositories

### Stats not updating?
- Check the workflow logs in **Actions** tab
- Verify commits are attributed to the configured GitHub username
- GitHub API rate limits: 5,000 requests/hour per token

### Incorrect commit counts?
- GitHub commit search evaluates repositories' default branches
- Commits must be attributed by GitHub to the configured username
- The token must be able to access every private repository that should count
- Re-run the workflow if needed

## API Rate Limiting

The script uses GitHub's authenticated commit-search endpoint and fails closed
when GitHub reports incomplete results. A normal run makes one search request.

## Support

For issues or feature requests, create an issue in this repository.

## License

MIT License - feel free to use and modify this script!
