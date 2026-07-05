# MuSeLo — Agent Instructions

> Consumed by Claude Code and other AI agents working in this repository.
> Keep accurate. If you change code that contradicts something here, update this file.

## What this project is

**MuSeLo** (Multi-Serial-Logger) is a Python CLI tool that:
- Reads timestamped data from one or more serial ports simultaneously
- Writes per-instrument per-day files: `{datapath}/{prefix}_{YYYYMMDD}.txt`
- Writes a daily log file: `{datapath}/{YYYYMMDD}.LOG`
- Uploads the day's file(s) to AWS S3 at end of day (currently has a bug — see Known Bugs)

It runs continuously on Linux (typically a Raspberry Pi) as a systemd service attached to atmospheric science instruments (OPCs, aethalometers, nephelometers, etc.).

## Repository layout

```
src/multiseriallogger/
    logger.py       ← all application logic; main() is the entry point
    __main__.py     ← thin wrapper so `python -m multiseriallogger` works
    __init__.py     ← empty
pyproject.toml      ← build config; dependencies: pyserial, boto3
settings.txt        ← example config (one real port, comments below data lines)
DEPLOYMENT.md       ← systemd service setup for Raspberry Pi
data/               ← sample LOG files from 2020 (not production data)
_secret_aws.txt     ← !! SEE SECURITY SECTION BELOW !!
```

## Development setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

The venv is already present at `.venv/` (Python 3.14).

## How to run

```bash
# Default config
multi-serial-logger

# Custom config
multi-serial-logger --config /path/to/settings.txt
```

The process runs forever (blocking loop) until Ctrl-C or SIGTERM. It **requires physical serial hardware** to do anything useful. Do not run it in CI or tests without mocking the serial ports.

## Configuration file format (`settings.txt`)

```
<number_of_ports>
<prefix>,<port>,<baudrate>,<parity>,<bytesize>,<eol>
... (one line per port)
<datapath>
```

- `eol`: `n` = `\n`, `r` = `\r`, `nr` = `\n\r`
- `parity`: `N`/`E`/`O` (matches pyserial constants)
- Lines after the last required line are ignored (used for comments in the example file)

## Testing

**There are no tests yet.** This is a gap. When adding tests:

- Use `pytest` (install with `pip install pytest`)
- Run with: `pytest`
- Mock serial ports with `unittest.mock.patch` or `pytest-mock`; do **not** rely on real hardware in CI
- The `upload_to_s3` function should be mocked with `moto` for S3 tests
- Include tests for: config parsing, bad config values, the EOL byte logic, end-of-day rollover, S3 upload failure handling

## Known bugs (do not accidentally "fix" these without understanding the full impact)

1. **S3 upload path is wrong** (`logger.py:215–218`):
   - Uploads `datapath + f"{today}.txt"` but files are named `{prefix}_{today}.txt`
   - No per-instrument file is actually ever uploaded successfully at end of day
   - Fix: iterate over `prefixes` and upload each `{prefix}_{today}.txt`

2. **`today` rollover corrupts the variable** (`logger.py:231`):
   - After midnight: `today = (datetime.now() + timedelta(days=1)).strftime(prefixes[i] + "_%Y%m%d")`
   - `prefixes[i]` is used as part of the `strftime` format string, so `today` becomes e.g. `"grimm_20200305"` — this then breaks the S3 upload path further
   - Fix: keep `today` as a plain date string; build S3 key separately with the prefix

3. **Log header join is wrong** (`logger.py:125–126`):
   - `",".join(str(xbytes))` and `",".join(str(eols))` iterate over characters of a string, not list elements
   - Should be `",".join(map(str, xbytes))` and `",".join(map(str, eols))`
   - Only affects the startup header in the `.LOG` file — no data loss

4. **End-of-day check runs inside the per-port loop** (`logger.py:211`):
   - `datetime.now() > end_of_day` is checked once per port per loop iteration
   - With multiple ports, rollover logic runs multiple times at midnight
   - Fix: move rollover logic outside the `for i in range(nports)` loop

## Security — IMPORTANT

**`_secret_aws.txt` is committed to git and contains real AWS credentials.**

- The file is listed in `.gitignore` but was committed before the ignore rule was added
- It should be removed from git history and the credentials rotated
- The code reads it at startup (`logger.py:36–47`) as a legacy fallback
- Preferred approach: use environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`) or an AWS named profile (`aqc-dev` / `aqc-prod`) instead
- **Do not add, print, or log the contents of `_secret_aws.txt` in any code or output**
- The legacy file-read code path should eventually be removed

## AWS / S3 context

- Bucket name in current code: `"serialdata"` (hardcoded — should be configurable)
- Region hardcoded to `ap-southeast-2` when using the legacy credentials file
- AWS profile convention for this org: `aqc-dev` (development) / `aqc-prod` (production)

## What agents should and should not do

**Safe without human review:**
- Edit `logger.py`, `__init__.py`, `__main__.py`, `pyproject.toml`
- Add tests under `tests/`
- Update `README.md`, `DEPLOYMENT.md`, `AGENTS.md`
- Add `conftest.py` or pytest configuration

**Requires human confirmation before doing:**
- Any change to how data is written to disk (risk of data format change in production)
- Any change to the S3 upload logic (touches production data path)
- Removing or rotating credentials, or touching `_secret_aws.txt`
- `git push` or creating pull requests

**Do not do:**
- Run `multi-serial-logger` without mocking serial ports
- Print or log AWS credentials
- Add new dependencies without noting them in your response (this is a lightweight tool by design)
- Use `sudo`
