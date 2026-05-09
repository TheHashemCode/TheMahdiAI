# Contributing to TheMahdiAI

Thanks for your interest in improving TheMahdiAI.

## How to contribute

1. Fork the repository and create a feature branch from `main`.
2. Keep changes focused and include tests for behavior changes.
3. Run the test suite locally before opening a pull request.
4. Open a PR with a clear summary and checklist.

## Development workflow

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
make test
```

You can pass custom pytest args by using:

```bash
make test ARGS="-q -k quota"
```

## Code quality expectations

- Keep tests readable and minimal.
- Keep changes scoped and avoid unrelated refactors.
- Update docs when user-facing behavior changes.

## CI

Every pull request runs:

- `make test`

Make sure it is green locally before requesting review.

## Reporting issues

Please open an issue with:

- Expected behavior
- Reproduction steps
- Relevant logs or error output
- Environment (Python version, OS)
