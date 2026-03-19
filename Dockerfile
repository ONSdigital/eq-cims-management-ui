FROM python:3.12-slim-bookworm

WORKDIR /eq_cims_management_ui

COPY pyproject.toml poetry.lock ./

ENV WEB_SERVER_WORKERS=3
ENV WEB_SERVER_THREADS=10
ENV HTTP_KEEP_ALIVE=2
ENV GUNICORN_CMD_ARGS="-c gunicorn_config.py"
ENV LOG_LEVEL=info

RUN pip install --no-cache-dir poetry==2.1.2 && \
    poetry config virtualenvs.create false && \
    poetry install --without dev

COPY . .

RUN groupadd -r appuser && useradd -r -g appuser -u 999 appuser && \
    chown -R appuser:appuser .

USER appuser

EXPOSE 5100

HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5100/status')" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5100", "app:app"]
