# FROM python:3.8-slim

# RUN set -ex; \
#   	pip install --no-cache-dir confluent-kafka; \
#   	pip install --no-cache-dir python-twitch-client; \
# 	pip install --no-cache-dir sqlalchemy; \
# 	pip install --no-cache-dir python-twitch-client; \

# ADD .env /
# ADD twitch_kafka_consumer.py /
# ADD example.log /

# CMD ["python", "-u", "./twitch_kafka_consumer.py"]

###

FROM python:3.8-slim as base

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1


FROM base AS python-deps

RUN apt-get update 
RUN apt-get -y upgrade 
RUN apt-get -y install --no-install-recommends gcc 
RUN pip install --upgrade pip 
RUN pip install pipenv

COPY Pipfile .
COPY Pipfile.lock .
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy


FROM base AS runtime

COPY --from=python-deps /.venv /.venv
ENV PATH="/.venv/bin:$PATH"

RUN useradd --create-home appuser
WORKDIR /home/appuser
USER appuser

COPY twitch_kafka_consumer.py ./twitch_kafka_consumer.py
COPY .env ./.env

RUN mkdir python_logs
RUN cat > python_logs/example.log

CMD ["python", "-u", "./twitch_kafka_consumer.py"]