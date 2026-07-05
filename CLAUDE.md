@AGENTS.md

# Claude Code — additional notes

## Running tests

No test suite exists yet. When one is created, the command will be:

```bash
pytest
```

## Committing

Use conventional commits: `feat:`, `fix:`, `chore:`, `docs:`, `test:`, `refactor:`.
Always summarise what changed and why before asking to commit.
Do not commit without confirmation.

## Priorities for upcoming work

1. Remove `_secret_aws.txt` from git history and rotate the credentials
2. Add a `tests/` directory with at least: config parsing, EOL byte logic, S3 upload mock
3. Fix the four known bugs documented in AGENTS.md
4. Make S3 bucket name configurable via `settings.txt` or environment variable
