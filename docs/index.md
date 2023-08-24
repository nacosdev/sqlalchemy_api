<img src="assets/images/sqlalchemy_api.png"/>

SQLAlchemy API is a library that helps to turn the [SQLAlchemy](https://www.sqlalchemy.org/) models into a REST API. It uses the power of [Pydantic 2](https://docs.pydantic.dev/dev-v2/), to validate the data and serialize it.

This is intended to be a framework-agnostic library that can be used with any web framework. Currently, it provides support for [Starlette](https://www.starlette.io/) and [FastAPI](https://fastapi.tiangolo.com/).
## Requirements

- Python>=3.7
- SQLAlchemy>=1.4
- Pydantic>=2

## Installation

```bash
pip install sqlalchemy-api
```

## Example

### Create it

- Create a file `main.py` with a simple SQLAlchemy model

```Python hl_lines="2-3 5-9 11-14 16"
from sqlalchemy_api.adapters.starlette_crud import APICrud
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
engine = create_engine(
    "sqlite:///example.db",
    connect_args={"check_same_thread": False},
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)

Base.metadata.create_all(engine)  # Create tables

app = APICrud(User, engine)
```


- Create an instance of an APICrud from the Starlette adapter:

```Python hl_lines="1 18"
from sqlalchemy_api.adapters.starlette_crud import APICrud
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
engine = create_engine(
    "sqlite:///example.db",
    connect_args={"check_same_thread": False},
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)

Base.metadata.create_all(engine)  # Create tables

app = APICrud(User, engine)
```

You will also need an ASGI server and Starlette to be able to run the app, both are optional dependencies of SQLAlchemy API:

```bash
pip install sqlalchemy-api[asgi]
```

### Run it

```bash
uvicorn main:app --reload
```

### Use it

Endpoints are automatically generated for the defined model, you can use the following endpoints to interact with them:

- Create: `POST localhost:8000`
```bash
curl -X 'POST' \
  'http://localhost:8000' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "foo"
}'
```
- Get Many: `GET localhost:8000`
```bash
curl -X 'GET' \
  'http://localhost:8000?page_size=100&page=1' \
  -H 'accept: application/json'
```
- Get One: `GET localhost:8000/{id}`
```bash
curl -X 'GET' \
  'http://localhost:8000/1' \
  -H 'accept: application/json'
```
- Update: `PUT localhost:8000/{id}`
```bash
curl -X 'PUT' \
  'http://localhost:8000/1' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "bar"
}'
```
- Delete: `DELETE localhost:8000/{id}`
```bash
curl -X 'DELETE' \
  'http://localhost:8000/1' \
  -H 'accept: application/json'
```

More info about this in the [CRUD](crud/introduction.md) section.



