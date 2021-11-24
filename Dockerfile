FROM python:3.9-bullseye

COPY ./web /root/web
WORKDIR /root/web

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD python app.py