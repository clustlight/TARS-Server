FROM python:3.11.2-slim-bullseye AS builder

COPY requirements.txt /

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install -r requirements.txt

FROM jrottenberg/ffmpeg:4.1-scratch AS ffmpeg

FROM python:3.11.2-slim-bullseye

ENV LD_LIBRARY_PATH=/usr/local/lib
COPY --from=ffmpeg / /

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/dotenv /usr/local/bin/dotenv
COPY --from=builder /usr/local/bin/normalizer /usr/local/bin/normalizer
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn

WORKDIR app/

RUN mkdir src/

COPY ./src/* /app/src/

COPY requirements.txt /app/

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install -r requirements.txt

CMD ["python", "src/main.py"]