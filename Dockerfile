FROM python:3.11.1-slim-bullseye

WORKDIR app/

RUN apt-get update && apt-get upgrade -y && apt-get install -y ffmpeg

RUN mkdir src/

COPY ./src/* /app/src/

COPY requirements.txt /app/

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install -r requirements.txt

CMD ["python", "src/main.py"]