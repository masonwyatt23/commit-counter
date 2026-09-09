# GitHub Commit Counter - Quick Start Guide

## ✅ What's Been Set Up

### 1. **commit-counter Repository** (masonwyatt23/commit-counter)
- ✓ GitHub Actions workflow configured
- ✓ Python script ready to count commits
- ✓ Public repository for data access
- ✓ Status: Ready to run

### 2. **ashlar-landing Integration** (ashlrai/ashlar-landing)
- ✓ Sleek minimal commit counter component
- ✓ Positioned top-right of landing page
- ✓ Auto-refreshes hourly
- ✓ Status: Live on ashlr.ai

---

## 🚀 ACTIVATION

Add the `COMMIT_COUNTER_TOKEN` repository secret described in `README.md`, then
run the workflow:

### **Click This Link to Trigger the Workflow:**

https://github.com/masonwyatt23/commit-counter/actions/workflows/commit-counter.yml

**Then:**
1. Click the blue **"Run workflow"** button on the right side
2. Click **"Run workflow"** to confirm
3. Wait 2-3 minutes ⏱️
4. Visit https://ashlr.ai and look top-right corner for live commit count! 🎉

---

## 📊 What Happens Automatically

**Every Day at 2 AM UTC:**
- Workflow runs automatically
- Counts default-branch commits across non-fork repositories owned by
  `masonwyatt23`, `ashlrai`, and `Cash-Margin-Partners`
- Updates the live display on ashlr.ai
- You see the number update in top-right corner

---

## 🔍 Manual Verification Steps

If you want to verify everything is working:

```bash
# Check if stats file exists and has data
curl https://raw.githubusercontent.com/masonwyatt23/commit-counter/stats/commit_stats.json

# You should see JSON with:
# - total_commits: (number)
# - total_repositories: (number)
# The public payload intentionally omits repository names and per-repository counts.
```

---

## 💡 What You'll See

**On ashlr.ai (top-right corner):**
```
📊 123,456 commits
```

Click it to inspect the aggregate counter source on GitHub.

---

## 🆘 Troubleshooting

### "I don't see the number on ashlr.ai"
- The workflow hasn't run yet (click the button above)
- The stats JSON file is empty (run the workflow)
- Your browser cache is stale (hard refresh with Ctrl+Shift+R or Cmd+Shift+R)

### "The number is incorrect"
- Confirm `COMMIT_COUNTER_TOKEN` can read private repositories for all three owners
- Confirm forked repositories should remain excluded to avoid duplicate upstream history
- The workflow is still running (wait 2-3 minutes)

### "I want to change when it runs"
Edit `.github/workflows/commit-counter.yml` and change:
```yaml
cron: '0 2 * * *'  # Change this (currently 2 AM UTC daily)
```

---

## 📝 File Locations

**Main Files:**
- Workflow: `.github/workflows/commit-counter.yml`
- Script: `scripts/count_commits.py`
- Stats Output: `commit_stats.json` (auto-generated)
- Component: `components/studio/GitHubCommitsStats.tsx`

---

The live site revalidates the aggregate source hourly after a successful run.
