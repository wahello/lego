# LEGO [![CircleCI](https://circleci.com/gh/webkom/lego/tree/master.svg?style=svg&circle-token=26520c314e094786c87c6a14af78c0cd7c82caec)](https://circleci.com/gh/webkom/lego/tree/master)

> LEGO Er Ganske Oppdelt

We use [Waffle](https://waffle.io/webkom/lego) for simple project management.

[Noob guide for setting up LEGO](https://github.com/webkom/lego/wiki/Noob-Guide)

## Getting started

LEGO requires python3, virtualenv, docker and docker-compose. Services like Postgres, Redis and
Elasticsearch runs in docker.


```bash
    git clone git@github.com:webkom/lego.git && cd lego/
    virtualenv venv -p python3
    source venv/bin/activate
    docker-compose up
    python manage.py migrate
    python manage.py runserver
```

We recommend Pycharm for development, use your @stud.ntnu.no email to register a free professional
account.

