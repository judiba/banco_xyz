FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml poetry.lock README.md ./

RUN pip install --no-cache-dir poetry==1.8.2 \
    && poetry config virtualenvs.create false \
    && poetry install --with dev,mock,database,vector,ingestion,memory --no-root --no-interaction --no-ansi
COPY backend ./backend

CMD ["poetry", "run", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]