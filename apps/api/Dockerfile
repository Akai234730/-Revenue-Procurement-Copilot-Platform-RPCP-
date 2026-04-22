FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
COPY .env.example ./.env.example
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir .
CMD ["python", "-m", "app.run"]
