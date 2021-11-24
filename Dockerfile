FROM python:3.9-bullseye

COPY ./web /root/web
COPY ./.env /root/web/.env
WORKDIR /root/web

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD python app.py