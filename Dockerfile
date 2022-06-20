FROM python:3.9

ENV PYTHONPATH "${PYTHONPATH}:/app/app"
ENV PYTHONUNBUFFERED 1

EXPOSE 8080

COPY ./requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY ./app /app/app
COPY ./KC-057.CSV /app

WORKDIR /app

