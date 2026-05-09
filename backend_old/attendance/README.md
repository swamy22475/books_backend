Attendance Module (FastAPI)

Quick start (dev):

1. Create a Python venv and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Configure `.env` with `DATABASE_URL`.

3. Run:

```bash
uvicorn app.main:app --reload --port 8001
```

APIs are under `/api/attendance` (settings, mark, report).
