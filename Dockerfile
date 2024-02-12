FROM python:3.11.8-slim-bookworm AS backend-builder

COPY backend/pyproject.toml backend/poetry.lock backend/poetry.toml ./

RUN apt-get update && apt-get install -y wget xz-utils tar

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install poetry

RUN poetry export --without-hashes -f requirements.txt > requirements.txt
RUN pip install -r requirements.txt

RUN mkdir src/


FROM gcr.io/distroless/python3-debian12 AS runner

COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/lib/python3.11/site-packages
COPY --from=backend-builder /usr/local/bin/dotenv /usr/lib/python3.11/site-packages/dotenv
COPY --from=backend-builder /usr/local/bin/normalizer /usr/lib/python3.11/site-packages/normalizer
COPY --from=backend-builder /usr/local/bin/uvicorn /usr/lib/python3.11/site-packages/uvicorn

ENV PYTHONPATH=/usr/lib/python3.11/site-packages

COPY --from=mwader/static-ffmpeg:4.4.1 /ffmpeg /bin/

WORKDIR app/

COPY ./backend/src/ /app/src/

ENTRYPOINT ["python", "src/main.py"]