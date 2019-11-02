FROM python:3.7.2-slim

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY THE_MAYOR_OF_WHOVILLE ./

COPY center_for_mayoral_activities.py ./
COPY township.py ./
COPY town_start.sh ./
COPY cma_start.sh ./
