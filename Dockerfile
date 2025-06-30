FROM python:3.10-slim


ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && apt-get clean
COPY . /app/

RUN pip install --upgrade pip && pip install -r requirements.txt

RUN mkdir -p data/raw/matches data/raw/players data/raw/teams data/raw/weather data/processed data/squads

EXPOSE 8888

CMD ["python", "scripts/process_pipeline.py"]