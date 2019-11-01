FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY find_the_mayor_of_whoville.py ./
CMD [ "python", "./find_the_mayor_of_whoville.py"]
