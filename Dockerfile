FROM python:3.11.8-slim-bookworm AS builder

COPY pyproject.toml poetry.lock poetry.toml ./

RUN apt-get update && apt-get install -y wget xz-utils tar

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install poetry

RUN poetry export --without-hashes -f requirements.txt > requirements.txt
RUN pip install -r requirements.txt

RUN mkdir src/

WORKDIR static-ffmpeg/

RUN wget https://johnvansickle.com/ffmpeg/old-releases/ffmpeg-5.1.1-amd64-static.tar.xz
RUN tar Jxvf ./ffmpeg-5.1.1-amd64-static.tar.xz


FROM gcr.io/distroless/python3-debian12 AS runner

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/dotenv /usr/lib/python3.11/site-packages/dotenv
COPY --from=builder /usr/local/bin/normalizer /usr/lib/python3.11/site-packages/normalizer
COPY --from=builder /usr/local/bin/uvicorn /usr/lib/python3.11/site-packages/uvicorn

ENV PYTHONPATH=/usr/lib/python3.11/site-packages

COPY --from=builder /static-ffmpeg/ffmpeg-5.1.1-amd64-static/ffmpeg /bin/

WORKDIR app/

COPY ./src/ /app/src/

ENTRYPOINT ["python", "src/main.py"]