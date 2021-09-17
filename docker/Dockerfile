# syntax = docker/dockerfile:1.0-experimental

FROM python:3.8

RUN pip install --upgrade pip

RUN git clone https://github.com/trickeydan/hue2mqtt-python.git

WORKDIR /hue2mqtt-python

ENV POETRY_HOME=/poetry

RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python

ENV PATH="/poetry/bin:${PATH}"

RUN poetry install -vvv --no-ansi

VOLUME [ "/hue2mqtt-python/hue2mqtt.toml" ]

ENTRYPOINT ["poetry"]
CMD ["run", "hue2mqtt"]
