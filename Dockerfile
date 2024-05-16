FROM python:3.11

WORKDIR /code
ARG TEST

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./kimoji /code/kimoji
COPY ./start_db.py /code/
COPY ./entrypoint.sh /code/
COPY ./tests /code/tests

VOLUME /db

RUN if [ -n "$TEST" ]; then pip install --no-cache-dir --upgrade -r /code/tests/requirements.txt ; fi
EXPOSE 8000:8000

ENTRYPOINT /code/entrypoint.sh "$TEST"