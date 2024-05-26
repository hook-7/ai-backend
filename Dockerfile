FROM python:3.12-slim

WORKDIR /app

RUN pip install pipenv

COPY Pipfile Pipfile.lock /app/

RUN pipenv install --deploy --ignore-pipfile --system

COPY . /app

ENV PORT=8000

ENV HOST=0.0.0.0

ENV HTTP_PROXY="http://10.10.10.10:30809"

ENV HTTPS_PROXY="http://10.10.10.10:30809"

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
