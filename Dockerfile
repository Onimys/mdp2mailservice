FROM python:3.12.7-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN mkdir -p /attachments

COPY poetry.lock pyproject.toml ./
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

COPY . ./

ENV  ENVIRONMENT="production"

EXPOSE 8000

CMD ["fastapi", "run", "mdp2mailservice/main.py", "--port", "8000", "--workers", "4"]