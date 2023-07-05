FROM python:3.9-slim-bullseye

RUN apt-get update && apt-get install -y \
    mkvtoolnix \
    && rm -rf /var/lib/apt/lists/*

COPY main.py /app/main.py
COPY mkvinfo.py /app/mkvinfo.py

WORKDIR /app

ENV PYTHONUNBUFFERED=1

ENTRYPOINT [ "python", "main.py" ]
