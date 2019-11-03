FROM python:3.7.2-slim

RUN apt-get update && apt-get install -y libsndfile1

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# COPY azure.py ./

ENTRYPOINT ["python3", "./azure.py"]
