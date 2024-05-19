FROM python:3.10-slim

USER root

WORKDIR /app

COPY ./requirements.txt ./

RUN pip install -r requirements.txt

COPY . /app

CMD ["python3","main.py"]
