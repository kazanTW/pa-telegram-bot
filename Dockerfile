FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./
COPY bot.py handlers.py utils.py .

RUN pip install poetry && poetry config virtualenvs.create false

RUN poetry add "python-telegram-bot==20.0" && poetry add apscheduler && poetry add "python-telegram-bot[job_queue]" && poetry install --no-interaction --no-ansi --no-root

RUN touch data.json

CMD ["poetry", "run", "python", "bot.py"]
