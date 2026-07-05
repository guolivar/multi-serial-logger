# TODO — Urgent actions before retiring this repository

## CRITICAL — do these immediately

- [ ] **Rotate the AWS credentials in `_secret_aws.txt`**
  - These keys were committed to a public GitHub repository and must be considered compromised
  - Go to AWS IAM console → Users → find the key `AKIAYRIXBHNQIKGBLDGR` → Delete it
  - Create a new key pair and store it in `~/.aws/credentials` or as environment variables
  - Never store credentials in a file that could be committed to git

## Repo retirement

- [ ] Archive or delete `guolivar/multi-serial-logger` on GitHub
  - Settings → Danger Zone → Archive repository (keeps it readable but marks it inactive)
  - Or delete it entirely if no external links depend on it
- [ ] Update any scripts, systemd units, or documentation that reference
  `https://github.com/guolivar/multi-serial-logger` to point to the new repo

## New repository

This codebase has been moved to: **https://github.com/guolivar/muselo** (private)

The new repo has:
- No credential history
- `_secret_aws.txt` permanently gitignored
- `settings.txt` gitignored (use `settings.example.txt` as a template)
- `AGENTS.md` and `CLAUDE.md` for AI agent guidance
- Known bugs documented in `AGENTS.md`
