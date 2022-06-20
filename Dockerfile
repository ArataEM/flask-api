FROM python:3.8-slim-buster
ENV TZ=Europe/Kiev
WORKDIR /opt/flask-api

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "api.py"]
