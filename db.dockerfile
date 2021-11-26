FROM postgres:14-bullseye

RUN apt update
RUN apt upgrade

# CMD postgres