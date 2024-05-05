# "Currency exchange" web application using FastAPI

REST API for describing currencies and exchange rates. It allows users to view and edit lists of currencies and exchange rates, perform conversion calculations for arbitrary amounts from one currency to another.

The implementation does not include a web interface.

[Project specification](https://zhukovsd.github.io/python-backend-learning-course/Projects/CurrencyExchange/)

## Motivation
* Learn MVC Pattern [(docs)](https://gist.github.com/SergeyCP/0fd7f5ef83c48acc723de821315e01e9)
* Learn REST API
* Use FastAPI to build a REST API following [fastapi best practicies](https://github.com/zhanymkanov/fastapi-best-practices#3-use-dependencies-for-data-validation-vs-db) and [fastapi production template](https://github1s.com/zhanymkanov/fastapi_production_template/blob/main/src/config.py)
* Use SQLAlchemy to create database and tables for storing data [(SQLAlchemy course)](https://www.youtube.com/playlist?list=PLeLN0qH0-mCXARD_K-USF2wHctxzEVp40)
* Use [alembic](https://alembic.sqlalchemy.org/) for managing migrations
* Use [pytest](https://docs.pytest.org/) and [Factory Boy](https://factoryboy.readthedocs.io/) for testing


## Getting started

### Create environment variables

```bash
cp .env.example .env
```
Creates .env file from .env.example

### Install dependencies

```bash
pip install -r requirements.txt
```
Installs all project dependencies

### Run server

```bash
make run-prod
```
This command:
* creates database if it doesn't exist
* create tables if they don't exist
* starts web application server

### Use application

* Server available at http://127.0.0.1:8000
* REST API docs available at http://localhost:8000/docs#/


## Tests

All tests are integrational.

To run tests use
```bash
make test
```

To run tests with coverage use
```bash
make test-cov
```
After running tests with coverage report will be available at [tests/coverage/index.html](tests/coverage/index.html)
