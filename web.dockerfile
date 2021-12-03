FROM python:3.9-bullseye

COPY ./web /root/web
COPY ./data /root/data
COPY ./.env /root/.env
COPY ./DB_SQL.sql /root/DB_SQL.sql
WORKDIR /root/web

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD python app.py