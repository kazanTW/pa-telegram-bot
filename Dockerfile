FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./
COPY bot.py handlers.py utils.py .

RUN pip install poetry && poetry config virtualenvs.create false

RUN poetry install --no-interaction --no-ansi --no-root

RUN touch data.json

CMD ["poetry", "run", "python", "bot.py"]
