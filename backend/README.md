# AI Code Reviewer Backend

## Stack
- **FastAPI** (Web Framework)
- **SQLite** via `aiosqlite` (Database)
- **SQLAlchemy & Alembic** (ORM & Migrations)
- **FastAPI BackgroundTasks** (Async Processing handled natively, no Redis/Celery needed)
- **JWT** (Authentication)

## Running Locally (No Docker Required)

1. **Set up virtual environment (Optional but Recommended):**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

2. **Install requirements:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment:**
   Create a `.env` file in the same directory by using the example configuration:
   Add your `GEMINI_API_KEY` (and optionally a `GITHUB_TOKEN`). All other defaults (including the local SQLite connection) are already handled automatically.

4. **Start the API Server:**
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Viewing Documentation:**
   The database forms itself automatically on initialization. You can view and test the API endpoints at:
   - Interactive docs (Swagger): `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

*Note: Since Celery and Redis have been gracefully swapped out for native fastAPI `BackgroundTasks` alongside a local `SQLite` node, you do not need Docker running at all anymore!*
