FROM python:3.11.14-slim-bookworm AS backend-builder

WORKDIR /build
COPY backend/pyproject.toml backend/poetry.lock backend/poetry.toml ./

RUN apt-get update && apt-get install -y wget xz-utils tar \
	&& rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip setuptools
RUN pip install poetry poetry-plugin-export

RUN poetry export --without-hashes -f requirements.txt -o requirements.txt
RUN pip install -r requirements.txt


FROM node:18.17.1-bookworm-slim AS frontend-builder

WORKDIR /frontend

COPY frontend/package.json frontend/package-lock.json ./

RUN npm ci
COPY frontend/ ./

RUN npm run build


FROM gcr.io/distroless/python3-debian12 AS runner

COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/usr/local/lib/python3.11/site-packages:/usr/local/lib64/python3.11/site-packages
ENV PATH="/usr/bin"

COPY --from=mwader/static-ffmpeg:4.4.1 /ffmpeg /usr/bin/ffmpeg

WORKDIR /app

COPY backend/src/ /app/src/
COPY --from=frontend-builder /frontend/out/ /app/src/templates/

ENTRYPOINT ["python3", "/app/src/main.py"]