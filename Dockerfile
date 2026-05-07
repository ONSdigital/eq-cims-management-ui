FROM python:3.13-slim-bookworm

RUN mkdir -p /usr/src/
WORKDIR /usr/src/

COPY eq_cims_management_ui /usr/src/eq_cims_management_ui
COPY app.py gunicorn_config.py poetry.lock pyproject.toml package.json package-lock.json /usr/src/
COPY templates /usr/src/templates
COPY static /usr/src/static

ENV WEB_SERVER_WORKERS=3
ENV WEB_SERVER_THREADS=10
ENV HTTP_KEEP_ALIVE=2
ENV GUNICORN_CMD_ARGS="-c gunicorn_config.py"
ENV LOG_LEVEL=info

RUN pip install --no-cache-dir poetry==2.1.2 && \
    poetry config virtualenvs.create false && \
    poetry install --without dev

RUN apt-get update && apt-get install -y --no-install-recommends \
    npm \
    && rm -rf /var/lib/apt/lists/*

RUN npm install --frozen-lockfile

RUN groupadd -r appuser && useradd -r -g appuser -u 999 -m appuser && \
    chown -R appuser:appuser /usr/src

USER appuser

EXPOSE 5100

HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5100/status')" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5100", "app:app"]
