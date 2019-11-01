FROM python:3.7.2-slim

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY find_the_mayor_of_whoville.py ./
CMD [ "python", "./find_the_mayor_of_whoville.py"]
